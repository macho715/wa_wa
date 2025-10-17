"""PyMuPDF 모듈 스텁. PyMuPDF module stub for tests."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def open(file_path: str):  # type: ignore[override]
    """문서 열기 스텁. Stub context manager for documents."""

    yield []
