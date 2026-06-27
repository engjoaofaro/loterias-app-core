import unittest

from mapper.map_dto import map_object, map_item
from service.apuracao import count_hits, build_outcome
from helper.results_api import fetch_result, NotDrawnYet


def dynamo_item(game_type="1", email_attr=None, games=None):
    item = {
        "gameType": {"N": game_type},
        "voucher": {"S": "v-1"},
        "lotteryNumber": {"N": "2890"},
        "games": {"L": [{"L": [{"N": str(n)} for n in g]} for g in (games or [[1, 2, 3, 4, 5, 6]])]},
    }
    if email_attr is not None:
        item["email"] = email_attr
    return item


class TestMapper(unittest.TestCase):
    def test_mapeia_item_com_email(self):
        bet = map_item(dynamo_item(email_attr={"S": "a@b.com"}))
        self.assertEqual(bet["loteria"], "megasena")
        self.assertEqual(bet["gameType"], 1)
        self.assertEqual(bet["concurso"], 2890)
        self.assertEqual(bet["email"], "a@b.com")
        self.assertEqual(bet["games"], [[1, 2, 3, 4, 5, 6]])

    def test_email_null_vira_none(self):
        bet = map_item(dynamo_item(email_attr={"NULL": True}))
        self.assertIsNone(bet["email"])

    def test_email_ausente_vira_none(self):
        bet = map_item(dynamo_item(email_attr=None))
        self.assertIsNone(bet["email"])

    def test_mapeia_tipos_de_loteria(self):
        self.assertEqual(map_item(dynamo_item(game_type="2"))["loteria"], "lotofacil")
        self.assertEqual(map_item(dynamo_item(game_type="3"))["loteria"], "lotomania")

    def test_map_object_lista(self):
        bets = map_object([dynamo_item(), dynamo_item(game_type="2")])
        self.assertEqual(len(bets), 2)


class TestContagem(unittest.TestCase):
    def test_conta_acertos(self):
        self.assertEqual(count_hits([5, 12, 45, 67, 78, 90], [5, 12, 45, 1, 2, 3]), 3)

    def test_ignora_zeros_a_esquerda_e_tipos(self):
        # dezenas da API podem vir como strings com zero à esquerda ("05")
        self.assertEqual(count_hits(["05", "12"], [5, 12, 99]), 2)

    def test_sem_acertos(self):
        self.assertEqual(count_hits([1, 2, 3], [4, 5, 6]), 0)


class TestOutcome(unittest.TestCase):
    def test_build_outcome(self):
        bet = {"loteria": "megasena", "gameType": 1, "voucher": "v-9", "concurso": 2890,
               "email": "a@b.com", "games": [[5, 12, 45, 1, 2, 3], [10, 20, 30, 40, 50, 60]]}
        out = build_outcome(bet, ["05", "12", "45", "67", "78", "90"])
        self.assertEqual(out["voucher"], "v-9")
        self.assertEqual(out["concurso"], 2890)
        self.assertEqual(out["maxAcertos"], 3)
        self.assertEqual(out["resultados"][0]["hits"], 3)
        self.assertEqual(out["resultados"][1]["hits"], 0)
        self.assertEqual(out["dezenasSorteadas"], [5, 12, 45, 67, 78, 90])


def fake_get(payload, capture=None):
    def _get(url, params=None):
        if capture is not None:
            capture["url"] = url
            capture["params"] = params
        class R:
            def json(self_inner):
                return payload
        return R()
    return _get


class TestResultsApi(unittest.TestCase):
    def test_retorna_dezenas_como_int_quando_sorteado(self):
        r = fetch_result("http://api", "tk", "megasena", 2890,
                         fetch_fn=fake_get({"numero_concurso": 2890, "dezenas": ["05", "12", "45"]}))
        self.assertEqual(r["concurso"], 2890)
        self.assertEqual(r["dezenas"], [5, 12, 45])

    def test_lanca_not_drawn_quando_concurso_nao_bate(self):
        with self.assertRaises(NotDrawnYet):
            fetch_result("http://api", "tk", "megasena", 2890,
                         fetch_fn=fake_get({"numero_concurso": 2889, "dezenas": []}))

    def test_envia_loteria_token_concurso(self):
        cap = {}
        fetch_result("http://api", "tk", "lotomania", 2894,
                     fetch_fn=fake_get({"numero_concurso": 2894, "dezenas": ["00", "99"]}, cap))
        self.assertEqual(cap["params"]["loteria"], "lotomania")
        self.assertEqual(cap["params"]["token"], "tk")
        self.assertEqual(cap["params"]["concurso"], 2894)


if __name__ == "__main__":
    unittest.main()
