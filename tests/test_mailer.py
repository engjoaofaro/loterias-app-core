import unittest

from helper.mailer import build_result_email


def outcome(loteria="megasena", hits=(6, 3), email="a@b.com"):
    return {
        "voucher": "vch-123",
        "concurso": 2890,
        "loteria": loteria,
        "gameType": 1,
        "email": email,
        "dezenasSorteadas": [5, 12, 22, 25, 30, 60],
        "resultados": [{"numbers": [5, 12, 22, 25, 30, 60][: 6], "hits": h} for h in hits],
        "maxAcertos": max(hits),
    }


class TestBuildResultEmail(unittest.TestCase):
    def test_estrutura_basica(self):
        msg = build_result_email(outcome())
        self.assertIn("subject", msg)
        self.assertIn("html", msg)
        self.assertIn("text", msg)

    def test_assunto_tem_loteria_e_concurso(self):
        msg = build_result_email(outcome())
        self.assertIn("2890", msg["subject"])
        self.assertRegex(msg["subject"].lower(), r"mega")

    def test_html_contem_voucher_dezenas_e_acertos(self):
        msg = build_result_email(outcome(hits=(6, 3)))
        self.assertIn("vch-123", msg["html"])
        self.assertIn("60", msg["html"])  # dezena sorteada
        self.assertIn("6", msg["html"])   # acertos

    def test_indica_premiacao_quando_ha(self):
        msg = build_result_email(outcome(hits=(6, 0)))  # Sena
        self.assertRegex(msg["html"].lower(), r"premi|parab")

    def test_sem_premiacao_nao_alarma(self):
        msg = build_result_email(outcome(hits=(3, 2)))  # nada
        self.assertNotRegex(msg["html"].lower(), r"parab")


if __name__ == "__main__":
    unittest.main()
