import asyncio
import json
from pathlib import Path

import pytest

from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge


class _DummyProcess:
    def __init__(self, stdout: bytes, stderr: bytes, returncode: int = 0) -> None:
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode
        self.killed = False

    async def communicate(self) -> tuple[bytes, bytes]:
        return self._stdout, self._stderr

    def kill(self) -> None:
        self.killed = True


@pytest.mark.asyncio
async def test_scrape_group_parses_payload(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    script_dir = tmp_path
    (script_dir / "whatsapp_webjs_scraper.js").write_text(
        "console.log('noop')\n", encoding="utf-8"
    )

    bridge = WhatsAppWebJSBridge(script_dir=script_dir, timeout=5)

    async def _noop_ready() -> None:
        return None

    monkeypatch.setattr(bridge, "ensure_ready", _noop_ready)

    payload = {
        "status": "SUCCESS",
        "timestamp": "2024-01-01T00:00:00Z",
        "groups": [
            {
                "name": "HVDC 물류팀",
                "messages": [
                    {"id": "1", "body": "hello", "timestamp": 1},
                ],
                "summary": {"totalMessages": 1},
            }
        ],
        "errors": [],
    }

    async def _fake_process(*cmd: str, **kwargs: object) -> _DummyProcess:
        assert "--group" in cmd
        stdout = json.dumps(payload).encode("utf-8")
        return _DummyProcess(stdout=stdout, stderr=b"[log]\n")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _fake_process)

    result = await bridge.scrape_group("HVDC 물류팀", limit=25)

    assert result["status"] == "SUCCESS"
    assert result["group"]["summary"]["totalMessages"] == 1
    assert result["errors"] == []


@pytest.mark.asyncio
async def test_scrape_groups_invalid_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    script_dir = tmp_path
    (script_dir / "whatsapp_webjs_scraper.js").write_text(
        "console.log('noop')\n", encoding="utf-8"
    )

    bridge = WhatsAppWebJSBridge(script_dir=script_dir, timeout=5)

    async def _noop_ready() -> None:
        return None

    monkeypatch.setattr(bridge, "ensure_ready", _noop_ready)

    async def _fake_process(*cmd: str, **kwargs: object) -> _DummyProcess:
        return _DummyProcess(stdout=b"not-json", stderr=b"", returncode=0)

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _fake_process)

    with pytest.raises(ValueError):
        await bridge.scrape_groups(["HVDC 물류팀"], limit=10)
