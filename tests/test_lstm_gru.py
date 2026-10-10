"""Vérifie le protocole et les calculs du notebook sans entraîner ses modèles."""

import ast
import json
from pathlib import Path
import unittest

import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.sandwich_covariance import cov_hac
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


ROOT = Path(__file__).resolve().parents[1]


def notebook_definitions():
    """Charge seulement les définitions utiles, jamais les cellules de calcul."""
    notebook = json.loads((ROOT / '07_lstm_gru.ipynb').read_text(encoding='utf-8'))
    names = {
        'RecurrentForecaster', 'Standardizer', 'network_inputs', 'training_set',
        'forecast_blocks', 'rmse', 'scores', 'diebold_mariano', 'holm',
    }
    nodes = []
    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue
        for node in ast.parse(''.join(cell['source'])).body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names:
                nodes.append(node)
    found = {node.name for node in nodes}
    if found != names:
        raise AssertionError(f'Définitions manquantes : {sorted(names - found)}')
    namespace = {
        'np': np, 'torch': torch, 'nn': nn, 'stats': stats,
        'DataLoader': DataLoader, 'TensorDataset': TensorDataset,
        'WINDOW': 28, 'BLOCK': 7, 'HIDDEN': 8,
    }
    module = ast.Module(body=nodes, type_ignores=[])
    exec(compile(module, str(ROOT / '07_lstm_gru.ipynb'), 'exec'), namespace)
    return namespace


class IncrementForecaster(nn.Module):
    """Prévision déterministe sensible au passé et au calendrier de la cible."""

    def forward(self, window, target_calendar):
        return window[:, -1, 0] + target_calendar[:, 0] + 1


class RecurrentProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.defs = notebook_definitions()

    def test_lstm_and_gru_use_values_and_calendar(self):
        for kind in ('LSTM', 'GRU'):
            for n_calendar in (0, 3):
                with self.subTest(kind=kind, n_calendar=n_calendar):
                    torch.manual_seed(42)
                    model = self.defs['RecurrentForecaster'](kind, n_calendar)
                    windows = torch.randn(3, 28, 1 + n_calendar)
                    calendars = torch.randn(3, n_calendar)
                    predicted = model(windows, calendars)
                    self.assertEqual(tuple(predicted.shape), (3,))
                    self.assertTrue(torch.isfinite(predicted).all())
                    predicted.sum().backward()
                    self.assertIsNotNone(model.recurrent.weight_ih_l0.grad)
                    self.assertGreater(model.recurrent.weight_ih_l0.grad.abs().sum().item(), 0)

    def test_training_targets_and_windows_stop_before_fit_end(self):
        values = np.arange(60, dtype=float)
        calendars = np.column_stack((np.arange(60), -np.arange(60)))
        dataset = self.defs['training_set'](values, calendars, 40)
        self.assertEqual(len(dataset), 12)
        windows, target_calendars, targets = dataset.tensors
        np.testing.assert_array_equal(targets.numpy(), values[28:40])
        np.testing.assert_array_equal(windows[0, :, 0].numpy(), values[:28])
        np.testing.assert_array_equal(windows[-1, :, 0].numpy(), values[11:39])
        np.testing.assert_array_equal(windows[-1, :, 1:].numpy(), calendars[11:39])
        np.testing.assert_array_equal(target_calendars.numpy(), calendars[28:40])

    def test_current_block_observations_never_affect_its_forecasts(self):
        values = np.arange(70, dtype=float)
        calendars = np.zeros((77, 1))
        original = self.defs['forecast_blocks'](IncrementForecaster(), values, calendars, 35, 52)
        self.assertEqual(len(original), 17)  # deux semaines et un bloc final de trois jours
        for start in (35, 42, 49):
            with self.subTest(block_start=start):
                changed = values.copy()
                changed[start:] += 10000
                predicted = self.defs['forecast_blocks'](IncrementForecaster(), changed, calendars, 35, 52)
                current_stop = min(start + 7, 52) - 35
                np.testing.assert_array_equal(original[:current_stop], predicted[:current_stop])
                if current_stop < len(original):
                    self.assertNotEqual(original[current_stop], predicted[current_stop])

    def test_calendar_uses_target_date_and_observations_reset_each_block(self):
        values = np.arange(70, dtype=float) * 3
        calendars = np.arange(77, dtype=float)[:, None] / 10
        predicted = self.defs['forecast_blocks'](IncrementForecaster(), values, calendars, 35, 52)
        expected = []
        for start in (35, 42, 49):
            previous = values[start - 1]
            for day in range(start, min(start + 7, 52)):
                previous += 1 + calendars[day, 0]
                expected.append(previous)
        np.testing.assert_allclose(predicted, expected, rtol=1e-6)

    def test_final_forecast_needs_no_future_observed_values(self):
        values = np.arange(70, dtype=float)
        calendars = np.zeros((77, 1))
        final = self.defs['forecast_blocks'](IncrementForecaster(), values, calendars, 70, 77)
        np.testing.assert_allclose(final, np.arange(70, 77))

    def test_standardizer_fits_training_period_and_inverts(self):
        training = np.array([10., 12., 14., 16.])
        scaler = self.defs['Standardizer'](training)
        self.assertEqual(scaler.mean, training.mean())
        self.assertAlmostEqual(scaler.std, training.std())
        future = np.array([10000., -5000.])
        np.testing.assert_allclose(scaler.inverse(scaler.transform(future)), future)
        self.assertEqual(scaler.mean, training.mean())

    def test_standardizer_rejects_constant_training_series(self):
        with self.assertRaises(ValueError):
            self.defs['Standardizer'](np.ones(28))

    def test_metrics_match_hand_calculation(self):
        observed, predicted = np.array([10., 20., 40.]), np.array([12., 16., 50.])
        result = self.defs['scores'](observed, predicted)
        self.assertAlmostEqual(result['MSE'], 40)
        self.assertAlmostEqual(result['RMSE'], np.sqrt(40))
        self.assertAlmostEqual(result['MAE'], 16 / 3)
        self.assertAlmostEqual(result['MAPE (%)'], 100 * .65 / 3)
        self.assertAlmostEqual(result['biais'], 8 / 3)
        self.assertAlmostEqual(self.defs['rmse'](observed, predicted), result['RMSE'])

    def test_mape_rejects_zero_observations(self):
        with self.assertRaises(ValueError):
            self.defs['scores'](np.array([0., 10.]), np.array([1., 9.]))


class ForecastAccuracyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.defs = notebook_definitions()
        rng = np.random.default_rng(2026)
        cls.errors_a = rng.normal(.2, 1.1, 390)
        cls.errors_b = rng.normal(.8, 2.3, 390)

    def test_dm_matches_independent_statsmodels_hac_reference(self):
        for power in (1, 2):
            for lag in (0, 2, 4, None):
                with self.subTest(power=power, lag=lag):
                    differences = np.abs(self.errors_a[:385]) ** power - np.abs(self.errors_b[:385]) ** power
                    weekly = differences.reshape(-1, 7).mean(axis=1)
                    actual_lag = int(np.floor(4 * (len(weekly) / 100) ** (2 / 9))) if lag is None else lag
                    reference = sm.OLS(weekly, np.ones((len(weekly), 1))).fit()
                    variance = cov_hac(reference, nlags=actual_lag, use_correction=False)[0, 0]
                    expected_statistic = reference.params[0] / np.sqrt(variance)
                    expected_p = 2 * stats.norm.sf(abs(expected_statistic))
                    statistic, p_value = self.defs['diebold_mariano'](
                        self.errors_a, self.errors_b, power=power, max_lag=lag)
                    self.assertAlmostEqual(statistic, expected_statistic, places=10)
                    self.assertAlmostEqual(p_value, expected_p, places=12)

    def test_dm_sign_and_symmetry(self):
        dm = self.defs['diebold_mariano']
        statistic_ab, p_ab = dm(self.errors_a, self.errors_b)
        statistic_ba, p_ba = dm(self.errors_b, self.errors_a)
        self.assertLess(statistic_ab, 0)
        self.assertAlmostEqual(statistic_ab, -statistic_ba)
        self.assertAlmostEqual(p_ab, p_ba)
        self.assertGreaterEqual(p_ab, 0)
        self.assertLessEqual(p_ab, 1)

    def test_dm_does_not_depend_on_consumption_units(self):
        dm = self.defs['diebold_mariano']
        expected = dm(self.errors_a, self.errors_b)
        for factor in (1e-3, 1e3):
            with self.subTest(factor=factor):
                np.testing.assert_allclose(
                    dm(self.errors_a * factor, self.errors_b * factor), expected,
                    rtol=1e-10, atol=1e-14)

    def test_dm_identical_models_have_no_difference(self):
        self.assertEqual(self.defs['diebold_mariano'](self.errors_a, self.errors_a), (0., 1.))
        self.assertEqual(self.defs['diebold_mariano'](self.errors_a, -self.errors_a), (0., 1.))

    def test_dm_excludes_last_incomplete_block(self):
        dm = self.defs['diebold_mariano']
        expected = dm(self.errors_a[:385], self.errors_b[:385])
        changed_a, changed_b = self.errors_a.copy(), self.errors_b.copy()
        changed_a[-5:], changed_b[-5:] = 1e9, -1e10
        np.testing.assert_allclose(dm(changed_a, changed_b), expected, atol=1e-14)

    def test_dm_constant_nonzero_loss_difference(self):
        statistic, p_value = self.defs['diebold_mariano'](np.ones(28), np.zeros(28))
        self.assertEqual(statistic, np.inf)
        self.assertEqual(p_value, 0)

    def test_dm_rejects_invalid_data(self):
        cases = [
            (np.ones(13), np.zeros(13), {}),
            (np.ones(14), np.zeros(15), {}),
            (np.ones((2, 7)), np.zeros((2, 7)), {}),
            (np.full(14, np.nan), np.zeros(14), {}),
            (np.full(14, np.inf), np.zeros(14), {}),
            (np.ones(14), np.zeros(14), {'power': 3}),
            (np.ones(14), np.zeros(14), {'horizon': 0}),
            (np.ones(14), np.zeros(14), {'max_lag': -1}),
        ]
        for errors_a, errors_b, kwargs in cases:
            with self.subTest(kwargs=kwargs, shape=errors_a.shape):
                with self.assertRaises(ValueError):
                    self.defs['diebold_mariano'](errors_a, errors_b, **kwargs)

    def test_holm_matches_statsmodels_with_unsorted_and_duplicate_values(self):
        p_values = np.array([.04, .001, .2, .03, 1., 0., .04])
        expected = multipletests(p_values, method='holm')[1]
        np.testing.assert_allclose(self.defs['holm'](p_values), expected)

    def test_holm_rejects_invalid_p_values(self):
        for p_values in ([np.nan], [np.inf], [-.01], [1.01]):
            with self.subTest(p_values=p_values):
                with self.assertRaises(ValueError):
                    self.defs['holm'](p_values)


if __name__ == '__main__':
    unittest.main()
