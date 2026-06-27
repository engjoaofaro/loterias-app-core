"""Lê o token da API do Secrets Manager (se SECRET_NAME setado), com fallback para
a env var TOKEN. Import de boto3 é lazy para facilitar testes."""
import os

_cache = {}


def get_api_token(client=None, use_cache=True):
    if use_cache and "v" in _cache:
        return _cache["v"]

    value = None
    name = os.getenv("SECRET_NAME")
    if name:
        try:
            if client is None:
                import boto3
                client = boto3.client("secretsmanager")
            value = client.get_secret_value(SecretId=name)["SecretString"]
        except Exception:
            value = None  # fallback p/ env
    if value is None:
        value = os.getenv("TOKEN")

    if use_cache:
        _cache["v"] = value
    return value
