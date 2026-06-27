"""Mapeia itens no formato AttributeValue do DynamoDB (tabela Game) para apostas
normalizadas. Robusto a email NULL/ausente e converte dezenas para int."""

TYPE_TO_LOTERIA = {1: "megasena", 2: "lotofacil", 3: "lotomania"}


def map_item(item):
    game_type = int(item["gameType"]["N"])
    loteria = TYPE_TO_LOTERIA.get(game_type)
    if loteria is None:
        raise ValueError(f"gameType inválido: {game_type}")

    email = None
    e = item.get("email")
    if e and "S" in e:  # ignora {"NULL": true} e ausência
        email = e["S"]

    games = [[int(n["N"]) for n in g["L"]] for g in item["games"]["L"]]

    return {
        "loteria": loteria,
        "gameType": game_type,
        "voucher": item["voucher"]["S"],
        "concurso": int(item["lotteryNumber"]["N"]),
        "email": email,
        "games": games,
    }


def map_object(items):
    return [map_item(i) for i in items]
