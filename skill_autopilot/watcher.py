from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Dict

try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer
except Exception:  # pragma: no cover
    FileSystemEvent = object  # type: ignore
    FileSystemEventHandler = object  # type: ignore
    Observer = None  # type: ignore


class _BriefEventHandler(FileSystemEventHandler):
    def __init__(self, brief_path: Path, callback: Callable[[], None], debounce_seconds: float = 1.5):
        super().__init__()
        self.brief_path = brief_path.resolve()
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self._last_trigger = 0.0

    def on_modified(self, event: FileSystemEvent) -> None:  # type: ignore[override]
        self._maybe_trigger(event)

    def on_created(self, event: FileSystemEvent) -> None:  # type: ignore[override]
        self._maybe_trigger(event)

    def _maybe_trigger(self, event: FileSystemEvent) -> None:
        event_path = Path(getattr(event, "src_path", "")).resolve()
        if event_path != self.brief_path:
            return
        now = time.monotonic()
        if now - self._last_trigger < self.debounce_seconds:
            return
        self._last_trigger = now
        self.callback()


class BriefWatcherRegistry:
    def __init__(self):
        self._items: Dict[str, tuple[object, object]] = {}

    def supports_watch(self) -> bool:
        return Observer is not None

    def add(self, project_id: str, brief_path: str, callback: Callable[[], None]) -> None:
        if not self.supports_watch() or project_id in self._items:
            return

        brief = Path(brief_path).resolve()
        observer = Observer()
        handler = _BriefEventHandler(brief_path=brief, callback=callback)
        try:
            observer.schedule(handler, str(brief.parent), recursive=False)
            observer.start()
        except RuntimeError:
            return
        self._items[project_id] = (observer, handler)

    def remove(self, project_id: str) -> None:
        item = self._items.pop(project_id, None)
        if not item:
            return
        observer, _ = item
        observer.stop()
        observer.join(timeout=2)

    def clear(self) -> None:
        for project_id in list(self._items):
            self.remove(project_id)
