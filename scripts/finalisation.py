"""Finalisation reproductible : sélection interne, test réservé et prévision.

La sélection est enregistrée avant toute évaluation du test. Les paramètres
restent fixes pendant chaque évaluation glissante ; seuls les états évoluent.
"""
from pathlib import Path
import hashlib
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.stats.stattools import jarque_bera
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.gofplots import qqplot

OUT = Path('exports')
FIG = Path('figures/arima_sarima')
HORIZON = 7
ALPHA = 0.05


def fit(series, spec, trend='n'):
    """Une même méthode d'optimisation pour les modèles supplémentaires."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        result = SARIMAX(series, order=spec[0], seasonal_order=spec[1],
                         trend=trend, enforce_stationarity=True,
                         enforce_invertibility=True).fit(disp=False, maxiter=500)
    messages = sorted(set(str(w.message) for w in caught))
    if not result.mle_retvals.get('converged', False):
        raise RuntimeError(f'Non-convergence : {spec} ; {messages}')
    if not np.isfinite(result.params).all():
        raise ValueError('Paramètres non finis')
    return result, messages


def rolling(result, history, future, label):
    """Prévoir un bloc puis seulement incorporer ses observations réelles.

    Le dernier bloc peut contenir moins de sept jours. append(refit=False)
    conserve les paramètres estimés ; pas de fuite de valeurs futures.
    """
    rows = []
    state = result
    past = history.copy()
    for start in range(0, len(future), HORIZON):
        block = future.iloc[start:start + HORIZON]
        origin = past.index[-1]
        assert block.index[0] == origin + pd.Timedelta(days=1)
        if label == 'naif_saisonnier':
            mean = np.resize(past.iloc[-7:].to_numpy(), len(block))
            lower = upper = np.full(len(block), np.nan)
        elif label == 'naif_derniere_valeur':
            mean = np.repeat(past.iloc[-1], len(block))
            lower = upper = np.full(len(block), np.nan)
        else:
            fc = state.get_forecast(steps=len(block))
            mean = np.asarray(fc.predicted_mean)
            ci = np.asarray(fc.conf_int(alpha=ALPHA))
            lower, upper = ci[:, 0], ci[:, 1]
        for h, (date, actual, pred, lo, hi) in enumerate(
                zip(block.index, block, mean, lower, upper), start=1):
            rows.append(dict(modele=label, origine=origin, date=date, horizon=h,
                             observe=float(actual), prevision=float(pred),
                             borne_inferieure_95=float(lo), borne_superieure_95=float(hi)))
        if state is not None:
            # Les versions statsmodels/pmdarima ne conservent pas toutes le nom
            # de colonne. La conversion numérique évite ce conflit de noms.
            state = state.append(block.to_numpy(), refit=False)
        past = pd.concat([past, block])
    frame = pd.DataFrame(rows)
    assert (frame.date > frame.origine).all()
    assert ((frame.date - frame.origine).dt.days == frame.horizon).all()
    assert frame.horizon.between(1, 7).all()
    assert np.isfinite(frame[['observe', 'prevision']]).all().all()
    return frame


def metrics(frame):
    err = frame.observe - frame.prevision
    result = dict(n=len(frame), MAE=float(err.abs().mean()),
                  RMSE=float(np.sqrt(np.mean(err**2))),
                  biais_prevision=float(-err.mean()))
    valid = frame.borne_inferieure_95.notna() & frame.borne_superieure_95.notna()
    if valid.any():
        subset = frame.loc[valid]
        result['couverture_95'] = float(((subset.observe >= subset.borne_inferieure_95) &
                                        (subset.observe <= subset.borne_superieure_95)).mean())
        result['largeur_moyenne_95'] = float((subset.borne_superieure_95 - subset.borne_inferieure_95).mean())
    else:
        result['couverture_95'] = result['largeur_moyenne_95'] = np.nan
    return result


def diagnostics(result, spec, label, stage):
    order, seasonal = spec
    burn = max(int(result.loglikelihood_burn), order[1] + seasonal[1] * seasonal[3])
    resid = pd.Series(np.asarray(result.resid)[burn:]).dropna()
    dof = order[0] + order[2] + seasonal[0] + seasonal[2]
    lags = [lag for lag in (7, 14, 28) if lag > dof and lag < len(resid) // 5]
    lb = acorr_ljungbox(resid, lags=lags, model_df=dof, return_df=True)
    jb, jb_p, skew, kurt = jarque_bera(resid)
    lm, lm_p, _, _ = het_arch(resid, nlags=7, ddof=dof)
    rows = []
    for lag, row in lb.iterrows():
        rows.append(dict(modele=label, etape=stage, n_residus=len(resid),
                         observations_initiales_exclues=burn, model_df=dof,
                         retard_LB=int(lag), **row.to_dict(), JB=float(jb), JB_p=float(jb_p),
                         asymetrie=float(skew), kurtosis=float(kurt),
                         ARCH_LM=float(lm), ARCH_p=float(lm_p), ARCH_retards=7))
    return pd.DataFrame(rows), resid


def diagnostic_plot(resid, path, title):
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    axes[0, 0].plot(resid.to_numpy(), linewidth=.5)
    axes[0, 0].set_title('Résidus après initialisation')
    axes[0, 0].set_ylabel('GWh/jour')
    plot_acf(resid, lags=56, ax=axes[0, 1], title='ACF des résidus')
    qqplot(resid, line='s', ax=axes[1, 0])
    axes[1, 0].set_title('QQ-plot : comparaison à la normale')
    axes[1, 1].plot(resid.rolling(28).std().to_numpy(), linewidth=.8)
    axes[1, 1].set_title('Écart-type glissant sur 28 observations')
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def finaliser(y, train, validation, development, test, fits, specs, comparison):
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    assert len(y) == len(development) + len(test)
    assert development.index[-1] < test.index[0]
    assert train.index[-1] < validation.index[0]
    assert validation.index[-1] == development.index[-1]
    # Complément limité, motivé par les diagnostics déjà observés. La validation
    # est réutilisée : cet ajustement est explicitement exploratoire.
    extra = {
        'SARIMA_211_011': ((2, 1, 1), (0, 1, 1, 7)),
        'SARIMA_212_011': ((2, 1, 2), (0, 1, 1, 7)),
        'SARIMA_311_011': ((3, 1, 1), (0, 1, 1, 7)),
        'SARIMA_110_111': ((1, 1, 0), (1, 1, 1, 7)),
    }
    notes, extra_scores, extra_predictions = {}, [], []
    for name, spec in extra.items():
        print('Complément :', name, flush=True)
        try:
            fitted, messages = fit(train, spec)
            pred = rolling(fitted, train, validation, name)
        except Exception as exc:
            notes[name] = {'echec': str(exc)}
            continue
        fits[name], specs[name] = fitted, spec
        notes[name] = {'avertissements': messages}
        extra_predictions.append(pred)
        extra_scores.append({'modele': name, **metrics(pred), 'AIC': fitted.aic, 'BIC': fitted.bic})
    combined = comparison[['MAE', 'RMSE', 'AIC', 'BIC']].copy()
    if extra_scores:
        extra_table = pd.DataFrame(extra_scores).set_index('modele')
        combined = pd.concat([combined, extra_table[['MAE', 'RMSE', 'AIC', 'BIC']]])
        pd.concat(extra_predictions).to_csv(OUT / 'predictions_validation_complement.csv', index=False)
    combined = combined.sort_values(['RMSE', 'MAE'])
    combined.to_csv(OUT / 'comparaison_validation_complete.csv')
    (OUT / 'avertissements_complement.json').write_text(json.dumps(notes, ensure_ascii=False, indent=2))
    # RMSE minimale parmi les ARIMA/SARIMA convergés. Les références naïves
    # restent dans le tableau et sont également évaluées sur le test final.
    candidate_names = [name for name in combined.index if name in fits]
    selected = candidate_names[0]
    spec = specs[selected]
    trend = fits[selected].model.trend
    details = {
        name: {'order': list(specs[name][0]), 'seasonal_order': list(specs[name][1]),
               'trend': fits[name].model.trend, 'converge': bool(fits[name].mle_retvals.get('converged', False))}
        for name in fits
    }
    (OUT / 'specifications_modeles.json').write_text(json.dumps(details, ensure_ascii=False, indent=2))
    diag_frames = []
    for name in fits:
        table, _ = diagnostics(fits[name], specs[name], name, 'estimation_interne')
        diag_frames.append(table)
    all_diag = pd.concat(diag_frames, ignore_index=True)
    all_diag.to_csv(OUT / 'diagnostics_tous_modeles.csv', index=False)
    chosen_diag, chosen_resid = diagnostics(fits[selected], spec, selected, 'estimation_interne')
    diagnostic_plot(chosen_resid, FIG / 'diagnostics_selection.png', 'Modèle sélectionné — estimation interne')
    selection = dict(modele=selected, order=list(spec[0]), seasonal_order=list(spec[1]), trend=trend,
                     regle='RMSE minimale en validation interne parmi les modèles ARIMA/SARIMA convergés ; test non consulté',
                     validation_debut=str(validation.index[0].date()), validation_fin=str(validation.index[-1].date()),
                     test_debut=str(test.index[0].date()), test_fin=str(test.index[-1].date()),
                     RMSE_validation=float(combined.loc[selected, 'RMSE']),
                     meilleur_naif_RMSE_validation=float(combined.loc[['naif_saisonnier','naif_derniere_valeur'],'RMSE'].min()),
                     limites='Validation estivale réutilisée ; EDA initiale sur tout l’apprentissage ; diagnostics à commenter.',
                     sha256_donnees=hashlib.sha256(Path('data/daily.csv').read_bytes()).hexdigest())
    # Ce fichier est écrit AVANT le calcul des erreurs sur le test réservé.
    (OUT / 'selection_avant_test.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2))
    print('Choix figé avant test :', selected, spec, flush=True)
    test_fit, test_warnings = fit(development, spec, trend)
    test_diag, _ = diagnostics(test_fit, spec, selected, 'apprentissage_complet_avant_test')
    test_predictions = [rolling(test_fit, development, test, selected)]
    for naive in ('naif_saisonnier', 'naif_derniere_valeur'):
        test_predictions.append(rolling(None, development, test, naive))
    test_frame = pd.concat(test_predictions, ignore_index=True)
    test_frame.to_csv(OUT / 'predictions_test.csv', index=False)
    test_scores = pd.DataFrame([{'modele': name, **metrics(group)}
                               for name, group in test_frame.groupby('modele', sort=False)]).set_index('modele')
    test_scores.to_csv(OUT / 'scores_test.csv')
    per_h = pd.DataFrame([{'modele': name, 'horizon': h, **metrics(group)}
                         for (name, h), group in test_frame.groupby(['modele', 'horizon'])])
    per_h.to_csv(OUT / 'scores_test_par_horizon.csv', index=False)
    # Le test est évalué une fois ; on ne change pas les ordres ensuite.
    print(test_scores.to_string(), flush=True)
    final_fit, final_warnings = fit(y, spec, trend)
    final_diag, final_resid = diagnostics(final_fit, spec, selected, 'reajustement_final')
    pd.concat([test_diag, final_diag]).to_csv(OUT / 'diagnostics_modele_retenu.csv', index=False)
    diagnostic_plot(final_resid, FIG / 'diagnostics_finaux.png', 'Modèle final — toutes les observations')
    fc = final_fit.get_forecast(steps=HORIZON)
    ci = np.asarray(fc.conf_int(alpha=ALPHA))
    dates = pd.date_range(y.index[-1] + pd.Timedelta(days=1), periods=HORIZON, freq='D')
    export = pd.DataFrame(dict(date=dates, prevision=np.asarray(fc.predicted_mean),
                              borne_inferieure_95=ci[:, 0], borne_superieure_95=ci[:, 1]))
    assert np.isfinite(export.iloc[:, 1:]).all().all()
    assert (export.borne_inferieure_95 <= export.prevision).all()
    assert (export.prevision <= export.borne_superieure_95).all()
    export.to_csv(OUT / 'previsions_7j.csv', index=False, date_format='%Y-%m-%d')
    (OUT / 'resume_modele_final.txt').write_text(final_fit.summary().as_text())
    model_params = pd.DataFrame({'parametre': final_fit.param_names,
                                'estimation': np.asarray(final_fit.params),
                                'erreur_standard': np.asarray(final_fit.bse)})
    model_params.to_csv(OUT / 'parametres_modele_final.csv', index=False)
    metadata = dict(selection, cible='conso_gwh', unite='GWh/jour', source='data/daily.csv',
                    derniere_observation=str(y.index[-1].date()), horizon_jours=7,
                    niveau_intervalle=.95, nature_intervalle='prévision gaussienne conditionnelle au modèle ; couverture non garantie',
                    avertissements_apprentissage=test_warnings, avertissements_final=final_warnings,
                    test_n=len(test), test_blocs=int(np.ceil(len(test) / 7)),
                    test_dernier_bloc=len(test) % 7 or 7,
                    test_metriques={k: float(v) for k, v in test_scores.loc[selected].items()},
                    recalage='États actualisés chaque semaine ; paramètres fixes pendant le test ; réestimation finale sur toutes les données.')
    (OUT / 'metadonnees_previsions.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False))
    ax = y.iloc[-90:].plot(figsize=(12, 4), label='Observations', color='#29465b')
    ax.plot(export.date, export.prevision, marker='o', label='Prévision', color='#dc6d32')
    ax.fill_between(export.date, export.borne_inferieure_95, export.borne_superieure_95,
                    alpha=.2, color='#dc6d32', label='Intervalle nominal à 95 %')
    ax.set(title='Consommation électrique — prévisions du 1er au 7 septembre 2026', ylabel='GWh/jour', xlabel='Date')
    ax.legend(); ax.figure.tight_layout(); ax.figure.savefig(FIG / 'previsions_7j.png', dpi=160); plt.close(ax.figure)
    selected_test = test_frame.loc[test_frame.modele == selected]
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(selected_test.date, selected_test.observe, label='Observations', linewidth=.9)
    ax.plot(selected_test.date, selected_test.prevision, label='Prévisions par blocs de 7 jours', linewidth=.8)
    ax.set(title='Test externe — ordres fixés avant évaluation', ylabel='GWh/jour')
    ax.legend(); fig.tight_layout(); fig.savefig(FIG / 'test_externe.png', dpi=150); plt.close(fig)
    print('Exports finaux créés.', flush=True)
    return {'selection': selection, 'comparaison': combined, 'scores_test': test_scores,
            'diagnostics_finaux': final_diag, 'previsions': export, 'metadata': metadata}
