from __future__ import annotations

from typing import Annotated

from fastapi import Header, HTTPException, Request

from agentforge.config import AgentForgeSettings


def get_settings(request: Request) -> AgentForgeSettings:
    return request.app.state.settings


def get_store(request: Request):
    return request.app.state.store


def get_executor(request: Request):
    return request.app.state.executor


def get_metrics(request: Request):
    return request.app.state.metrics


def require_operator(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
    x_agentforge_operator_token: Annotated[
        str | None,
        Header(alias="X-AgentForge-Operator-Token"),
    ] = None,
    x_agentforge_operator: Annotated[
        str | None,
        Header(alias="X-AgentForge-Operator"),
    ] = None,
) -> str:
    settings = get_settings(request)
    expected = settings.operator_token
    supplied = x_agentforge_operator_token
    if not supplied and authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer":
            supplied = token.strip()
    if not expected or supplied != expected:
        raise HTTPException(status_code=401, detail="operator authentication required")
    return (x_agentforge_operator or "operator").strip() or "operator"
