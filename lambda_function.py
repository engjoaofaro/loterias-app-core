"""Apuração das apostas (core).

Varre a tabela Game em busca de apostas pendentes, consulta o resultado oficial de
cada concurso, calcula os acertos, grava o resultado na tabela de Outcomes, notifica
e marca a aposta como DONE. Apostas cujo concurso ainda não foi sorteado permanecem
pendentes para a próxima execução. NÃO apaga/recria a tabela (corrige anti-pattern).
"""
import os
import logging

import boto3

from mapper.map_dto import map_object
from service.apuracao import build_outcome
from helper.results_api import fetch_result, NotDrawnYet
from helper.mailer import send_result_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddb = boto3.client("dynamodb")
resource = boto3.resource("dynamodb")
ses = boto3.client("sesv2")

GAME_TABLE = os.getenv("GAME_TABLE", "Game")
OUTCOMES_TABLE = os.getenv("OUTCOMES_TABLE", "LoteriasOutcomes")
BASE_URL = os.getenv("BASE_URL")
TOKEN = os.getenv("TOKEN")
SES_SENDER = os.getenv("SES_SENDER", "Loterias Sim <nao-responda@loteriassim.com.br>")


def _scan_pending():
    """Itens da Game ainda não apurados (sem status ou status != DONE)."""
    items = []
    kwargs = {"TableName": GAME_TABLE}
    while True:
        resp = ddb.scan(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" in resp:
            kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
        else:
            break
    return [i for i in items if i.get("status", {}).get("S") != "DONE"]


def _mark_done(voucher, max_hits):
    ddb.update_item(
        TableName=GAME_TABLE,
        Key={"voucher": {"S": voucher}},
        UpdateExpression="SET #s = :d, maxAcertos = :m",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":d": {"S": "DONE"}, ":m": {"N": str(max_hits)}},
    )


def lambda_handler(event, context):
    outcomes = resource.Table(OUTCOMES_TABLE)
    bets = map_object(_scan_pending())
    logger.info("Apostas pendentes: %d", len(bets))

    cache = {}
    done = pending = errors = 0

    for bet in bets:
        key = (bet["loteria"], bet["concurso"])
        try:
            if key not in cache:
                cache[key] = fetch_result(BASE_URL, TOKEN, bet["loteria"], bet["concurso"])
            drawn = cache[key]["dezenas"]
        except NotDrawnYet:
            pending += 1
            continue
        except Exception as error:  # noqa: BLE001
            logger.exception("Erro consultando resultado %s: %s", key, error)
            errors += 1
            continue

        outcome = build_outcome(bet, drawn)
        try:
            outcomes.put_item(Item=outcome)
        except Exception as error:  # noqa: BLE001
            logger.exception("Erro gravando outcome %s: %s", bet["voucher"], error)
            errors += 1
            continue

        try:
            send_result_email(ses, SES_SENDER, outcome)
        except Exception as error:  # noqa: BLE001 - notificação é best-effort
            logger.exception("Erro enviando e-mail %s: %s", bet["voucher"], error)

        _mark_done(bet["voucher"], outcome["maxAcertos"])
        done += 1

    result = {
        "code": 200,
        "done": done,
        "pending": pending,
        "errors": errors,
        "allDone": pending == 0 and errors == 0,
    }
    logger.info("Apuração concluída: %s", result)
    return result
