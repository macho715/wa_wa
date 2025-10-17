"""테스트 유틸리티 및 asyncio 지원. Asyncio support for tests."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: Any) -> bool | None:
    """비동기 테스트 실행 지원. Execute async tests without external plugins."""

    test_function = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_function):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_function(**pyfuncitem.funcargs))
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                loop.close()
                asyncio.set_event_loop(None)
        return True
    return None
