"""Monta e envia o e-mail de resultado da aposta via Amazon SES (SESv2).

`build_result_email` é puro (testável); `send_result_email` faz o envio.
"""
from service.apuracao import prize_tier, has_prize

LOTERIA_NOMES = {"megasena": "Mega-Sena", "lotofacil": "Lotofácil", "lotomania": "Lotomania"}


def _pad(n):
    return f"{int(n):02d}"


def build_result_email(outcome, site_url="https://loteriassim.com.br"):
    loteria = outcome["loteria"]
    nome = LOTERIA_NOMES.get(loteria, loteria)
    concurso = outcome["concurso"]
    dezenas = outcome["dezenasSorteadas"]
    premiado = has_prize(outcome)

    subject = f"Resultado {nome} • Concurso {concurso}"

    dezenas_html = "".join(
        f'<span style="display:inline-block;min-width:34px;text-align:center;margin:3px;'
        f'padding:8px 0;border-radius:50%;background:#1c1f26;color:#f8f9fa;font-weight:700;">{_pad(d)}</span>'
        for d in dezenas
    )

    linhas = []
    for i, r in enumerate(outcome["resultados"], start=1):
        tier = prize_tier(loteria, r["hits"])
        nums = " ".join(_pad(n) for n in r["numbers"])
        badge = (f'<strong style="color:#00c853;">★ {tier}</strong>' if tier
                 else f'<span style="color:#a0a5b1;">{r["hits"]} acertos</span>')
        linhas.append(
            f'<tr><td style="padding:6px 10px;color:#a0a5b1;">Jogo {i}</td>'
            f'<td style="padding:6px 10px;font-family:monospace;">{nums}</td>'
            f'<td style="padding:6px 10px;text-align:right;">{badge}</td></tr>'
        )
    jogos_html = "".join(linhas)

    banner = (
        '<div style="background:linear-gradient(135deg,#8a2be2,#00e5ff);color:#fff;'
        'padding:16px;border-radius:10px;text-align:center;font-size:18px;font-weight:700;">'
        '🎉 Parabéns! Você foi premiado!</div>'
        if premiado else
        '<div style="background:#1c1f26;color:#a0a5b1;padding:16px;border-radius:10px;text-align:center;">'
        'Não foi dessa vez. Continue tentando! 🍀</div>'
    )

    html = f"""<!DOCTYPE html><html><body style="margin:0;background:#0a0c10;font-family:Arial,Helvetica,sans-serif;">
  <div style="max-width:560px;margin:0 auto;padding:24px;color:#f8f9fa;">
    <h1 style="font-size:22px;margin:0 0 4px;">Loterias <span style="color:#00e5ff;">Sim</span></h1>
    <p style="color:#a0a5b1;margin:0 0 20px;">{nome} — Concurso {concurso}</p>
    {banner}
    <h3 style="margin:24px 0 8px;">Dezenas sorteadas</h3>
    <div>{dezenas_html}</div>
    <h3 style="margin:24px 0 8px;">Seus jogos</h3>
    <table style="width:100%;border-collapse:collapse;background:#14161b;border-radius:8px;">{jogos_html}</table>
    <p style="color:#6b7280;font-size:12px;margin-top:24px;">Voucher: {outcome['voucher']}</p>
    <p style="color:#6b7280;font-size:12px;">{site_url} — Jogue com responsabilidade. As análises são informativas e não aumentam suas chances reais.</p>
  </div></body></html>"""

    text_linhas = "\n".join(
        f"  Jogo {i}: {' '.join(_pad(n) for n in r['numbers'])} -> {r['hits']} acertos"
        + (f" ({prize_tier(loteria, r['hits'])})" if prize_tier(loteria, r["hits"]) else "")
        for i, r in enumerate(outcome["resultados"], start=1)
    )
    text = (
        f"{nome} - Concurso {concurso}\n"
        f"{'PARABENS! Voce foi premiado!' if premiado else 'Nao foi dessa vez.'}\n\n"
        f"Dezenas sorteadas: {' '.join(_pad(d) for d in dezenas)}\n\n"
        f"Seus jogos:\n{text_linhas}\n\n"
        f"Voucher: {outcome['voucher']}\n{site_url}"
    )

    return {"subject": subject, "html": html, "text": text}


def send_result_email(ses_client, sender, outcome):
    """Envia o e-mail de resultado se a aposta tiver e-mail. Retorna True se enviou."""
    email = outcome.get("email")
    if not email:
        return False
    msg = build_result_email(outcome)
    ses_client.send_email(
        FromEmailAddress=sender,
        Destination={"ToAddresses": [email]},
        Content={
            "Simple": {
                "Subject": {"Data": msg["subject"], "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": msg["html"], "Charset": "UTF-8"},
                    "Text": {"Data": msg["text"], "Charset": "UTF-8"},
                },
            }
        },
    )
    return True
