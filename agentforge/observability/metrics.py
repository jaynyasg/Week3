from __future__ import annotations

import threading
from collections import Counter


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counts: Counter[str] = Counter()

    def inc(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counts[name] += value

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counts)

    def render_prometheus(self) -> str:
        snapshot = self.snapshot()
        lines: list[str] = []
        for name, value in sorted(snapshot.items()):
            metric = f"agentforge_{name}"
            lines.append(f"# TYPE {metric} counter")
            lines.append(f"{metric} {value}")
        return "\n".join(lines) + ("\n" if lines else "")
