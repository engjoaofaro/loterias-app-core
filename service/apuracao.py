"""Lógica pura de apuração: contagem de acertos e montagem do resultado por aposta."""


def count_hits(drawn, game):
    """Quantos números do jogo saíram no sorteio (tolerante a strings/zeros à esquerda)."""
    drawn_set = {int(x) for x in drawn}
    return sum(1 for n in game if int(n) in drawn_set)


def prize_tier(loteria, hits):
    """Rótulo da faixa de premiação para a quantidade de acertos, ou None."""
    if loteria == "megasena":
        return {6: "Sena", 5: "Quina", 4: "Quadra"}.get(hits)
    if loteria == "lotofacil":
        return f"{hits} acertos" if 11 <= hits <= 15 else None
    if loteria == "lotomania":
        return f"{hits} acertos" if (hits == 0 or 15 <= hits <= 20) else None
    return None


def has_prize(outcome):
    """True se algum jogo da aposta caiu em uma faixa de premiação."""
    loteria = outcome["loteria"]
    return any(prize_tier(loteria, r["hits"]) for r in outcome["resultados"])


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
