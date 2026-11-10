"""Synthetic algebra/validation tests. No model, saved activation or network."""
from itertools import product
import unittest
import numpy as np
from fit_direction import fit_direction, GOALS, ORDERS, PRICES, SERVICES, LABELS


def synthetic_states(signal=1.):
    data = {}
    for item, goal, order, price, service, label in product(range(6), GOALS, ORDERS, PRICES, SERVICES, LABELS):
        g = 1 if goal == 'welfare' else -1
        o = 1 if order == 'target_last' else -1
        p = 1 if price == 'double' else -1
        s = 1 if service == 'negative' else -1
        l = 1 if label == 1 else -1
        data[str(item), goal, order, price, service, label] = np.array(
            [signal * g * l, 2*l, 3*g, 4*p, 5*s, 6*o, 7*p*s*g*l, float(item)], dtype=float)
    return data


class FactorialFitTests(unittest.TestCase):
    def test_known_interaction_cancels_balanced_nuisances(self):
        direction, center, report = fit_direction(synthetic_states())
        np.testing.assert_array_equal(direction, [1,0,0,0,0,0,0,0])
        np.testing.assert_array_equal(center, [0,0,0,0,0,0,0,2.5])
        self.assertEqual(report['training_states'], 192)
        self.assertEqual(report['raw_interaction_norm'], 4.)
        self.assertEqual(report['development_states_used_for_fit'], 0)
        self.assertFalse(report['measurement_validated'])
        for name in ('price_double_minus_base', 'service_negative_minus_positive', 'order_last_minus_first'):
            self.assertEqual(report['within_training_paired_effects'][name]['mean_absolute_projected_difference'], 0.)

    def test_missing_cell_rejected(self):
        data = synthetic_states(); data.pop(next(iter(data)))
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            fit_direction(data)

    def test_duplicate_record_rejected_before_mapping(self):
        records = list(synthetic_states().items()); records.append(records[0])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            fit_direction(records)

    def test_nonfinite_rejected(self):
        for invalid in (np.nan, np.inf):
            data = synthetic_states(); data[next(iter(data))][0] = invalid
            with self.assertRaisesRegex(ValueError, 'finite'):
                fit_direction(data)

    def test_zero_interaction_not_fabricated(self):
        with self.assertRaisesRegex(ValueError, 'Zero'):
            fit_direction(synthetic_states(signal=0.))

    def test_inconsistent_dimensions_rejected(self):
        data = synthetic_states(); data[next(iter(data))] = np.zeros(3)
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            fit_direction(data)

    def test_unknown_factor_level_rejected(self):
        data = synthetic_states(); key = next(iter(data)); value = data.pop(key)
        changed = list(key); changed[3] = 'unregistered_price'; data[tuple(changed)] = value
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            fit_direction(data)

    def test_negative_signal_is_not_flipped(self):
        direction, _, report = fit_direction(synthetic_states(signal=-1.))
        np.testing.assert_array_equal(direction, [-1,0,0,0,0,0,0,0])
        self.assertEqual(report['sign_rule'], 'unmodified higher-minus-lower welfare-minus-facts')


if __name__ == '__main__':
    unittest.main()
