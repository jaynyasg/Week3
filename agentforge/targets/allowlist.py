from __future__ import annotations

from urllib.parse import urljoin, urlparse

from pydantic import BaseModel


class TargetConfig(BaseModel):
    alias: str
    base_url: str

    @property
    def origin(self) -> str:
        parsed = urlparse(self.base_url)
        return f"{parsed.scheme}://{parsed.netloc}"


class TargetAllowlist:
    def __init__(self, targets: dict[str, str]) -> None:
        self._targets = {
            alias: TargetConfig(alias=alias, base_url=url.rstrip("/"))
            for alias, url in targets.items()
            if url
        }

    @property
    def aliases(self) -> list[str]:
        return sorted(self._targets)

    def resolve(self, alias: str) -> TargetConfig:
        try:
            return self._targets[alias]
        except KeyError as exc:
            raise ValueError(f"target alias is not allowlisted: {alias}") from exc

    def require_any(self) -> None:
        if not self._targets:
            raise ValueError("no allowlisted target is configured")

    def build_url(self, alias: str, path: str) -> str:
        target = self.resolve(alias)
        return urljoin(f"{target.base_url}/", path.lstrip("/"))

    def validate_url(self, alias: str, candidate: str) -> str:
        target = self.resolve(alias)
        parsed_target = urlparse(target.base_url)
        parsed_candidate = urlparse(candidate)
        same_origin = (
            parsed_target.scheme == parsed_candidate.scheme
            and parsed_target.netloc == parsed_candidate.netloc
        )
        if not same_origin:
            raise ValueError("target URL override is outside the allowlist")
        target_path = parsed_target.path.rstrip("/")
        candidate_path = parsed_candidate.path.rstrip("/")
        if target_path and not candidate_path.startswith(target_path):
            raise ValueError("target URL path is outside the allowlisted prefix")
        return candidate
