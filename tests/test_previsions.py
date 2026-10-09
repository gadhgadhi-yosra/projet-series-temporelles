"""Contrats de la validation temporelle et du format d'actualisation."""
import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR', os.path.join(tempfile.gettempdir(), 'wattif-matplotlib'))
import unittest
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from scripts.finalisation import rolling, metrics


class RollingForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.y = pd.Series(np.random.default_rng(42).normal(100, 4, 70),
                          index=pd.date_range('2020-01-01', periods=70, freq='D'), name='conso_gwh')
        cls.history = cls.y.iloc[:40]
        cls.future = cls.y.iloc[40:]
        cls.fit = SARIMAX(cls.history, order=(1, 0, 0), trend='c').fit(disp=False)

    def test_horizons_and_last_partial_block(self):
        pred = rolling(self.fit, self.history, self.future, 'modele')
        self.assertEqual(len(pred), 30)
        self.assertEqual(pred.groupby('origine').size().tolist(), [7, 7, 7, 7, 2])
        self.assertTrue((pred.date > pred.origine).all())
        self.assertTrue(np.isfinite(pred.prevision).all())

    def test_future_values_do_not_affect_first_forecast(self):
        original = rolling(self.fit, self.history, self.future, 'modele')
        modified = rolling(self.fit, self.history, self.future + 100, 'modele')
        np.testing.assert_allclose(original.prevision.iloc[:7], modified.prevision.iloc[:7])

    def test_seasonal_naive_and_metrics(self):
        pred = rolling(None, self.history, self.future, 'naif_saisonnier')
        np.testing.assert_allclose(pred.prevision.iloc[:7], self.history.iloc[-7:])
        self.assertTrue(np.isnan(metrics(pred)['couverture_95']))
        pred['prevision'] = pred.observe
        self.assertEqual(metrics(pred)['RMSE'], 0)


if __name__ == '__main__':
    unittest.main()
