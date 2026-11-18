import hmac
import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def verificar_chave(api_key: str | None = Security(api_key_header)):
    autenticacao_ativa = os.getenv(
        "PASSOLIVRE_REQUIRE_API_KEY", "false"
    ).lower() == "true"

    if not autenticacao_ativa:
        return

    chave_correta = os.getenv("PASSOLIVRE_API_KEY")

    if not chave_correta:
        raise HTTPException(
            status_code=503,
            detail="Autenticacao nao configurada"
        )

    if not hmac.compare_digest(api_key or "", chave_correta):
        raise HTTPException(
            status_code=401,
            detail="Chave de acesso invalida"
        )