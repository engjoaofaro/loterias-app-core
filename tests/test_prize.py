import unittest

from service.apuracao import prize_tier, has_prize


class TestPrizeTier(unittest.TestCase):
    def test_megasena(self):
        self.assertEqual(prize_tier("megasena", 6), "Sena")
        self.assertEqual(prize_tier("megasena", 5), "Quina")
        self.assertEqual(prize_tier("megasena", 4), "Quadra")
        self.assertIsNone(prize_tier("megasena", 3))

    def test_lotofacil(self):
        self.assertEqual(prize_tier("lotofacil", 15), "15 acertos")
        self.assertEqual(prize_tier("lotofacil", 11), "11 acertos")
        self.assertIsNone(prize_tier("lotofacil", 10))

    def test_lotomania(self):
        self.assertEqual(prize_tier("lotomania", 20), "20 acertos")
        self.assertEqual(prize_tier("lotomania", 15), "15 acertos")
        self.assertEqual(prize_tier("lotomania", 0), "0 acertos")
        self.assertIsNone(prize_tier("lotomania", 10))

    def test_has_prize(self):
        out = {"loteria": "megasena", "resultados": [{"numbers": [], "hits": 4}, {"numbers": [], "hits": 2}]}
        self.assertTrue(has_prize(out))
        out2 = {"loteria": "megasena", "resultados": [{"numbers": [], "hits": 3}]}
        self.assertFalse(has_prize(out2))


if __name__ == "__main__":
    unittest.main()
