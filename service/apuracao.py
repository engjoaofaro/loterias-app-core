"""Lógica pura de apuração: contagem de acertos e montagem do resultado por aposta."""


def count_hits(drawn, game):
    """Quantos números do jogo saíram no sorteio (tolerante a strings/zeros à esquerda)."""
    drawn_set = {int(x) for x in drawn}
    return sum(1 for n in game if int(n) in drawn_set)


def build_outcome(bet, drawn_numbers):
    drawn = sorted(int(x) for x in drawn_numbers)
    resultados = [{"numbers": g, "hits": count_hits(drawn, g)} for g in bet["games"]]
    max_hits = max((r["hits"] for r in resultados), default=0)
    return {
        "voucher": bet["voucher"],
        "concurso": bet["concurso"],
        "loteria": bet["loteria"],
        "gameType": bet["gameType"],
        "email": bet.get("email"),
        "dezenasSorteadas": drawn,
        "resultados": resultados,
        "maxAcertos": max_hits,
    }
