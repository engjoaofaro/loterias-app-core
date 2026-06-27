"""Consulta o resultado oficial de um concurso na API de loterias.

`fetch_fn` é injetável para testes (default: requests.get)."""


class NotDrawnYet(Exception):
    """O concurso solicitado ainda não foi sorteado."""


def fetch_result(base_url, token, loteria, concurso, fetch_fn=None):
    if fetch_fn is None:
        import requests
        fetch_fn = requests.get

    resp = fetch_fn(base_url, params={"loteria": loteria, "token": token, "concurso": concurso})
    data = resp.json()

    drawn = int(data["numero_concurso"])
    if drawn != int(concurso):
        raise NotDrawnYet(f"Concurso {concurso} de {loteria} ainda não sorteado.")

    return {"concurso": drawn, "dezenas": [int(d) for d in data["dezenas"]]}
