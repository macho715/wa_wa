import json
import subprocess
from pathlib import Path

import pytest

from macho_gpt.async_scraper.group_config import GroupConfig, WebJSSettings
from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge


@pytest.mark.asyncio
async def test_scrape_group_success(tmp_path, monkeypatch):
    script_dir = tmp_path
    (script_dir / "whatsapp_webjs_scraper.js").write_text(
        "console.log()", encoding="utf-8"
    )
    for package_name in ("whatsapp-web.js", "qrcode-terminal"):
        (script_dir / "node_modules" / package_name).mkdir(parents=True, exist_ok=True)

    settings = WebJSSettings(script_dir=str(script_dir), timeout=60)
    bridge = WhatsAppWebJSBridge(settings)
    group = GroupConfig(name="Demo Group", save_file="demo.json", max_messages=5)

    def fake_run(args, **kwargs):
        if args[:2] == ["node", "--version"]:
            return subprocess.CompletedProcess(args, 0, stdout="v18.0.0", stderr="")
        if args[0] == "node" and args[1].endswith("whatsapp_webjs_scraper.js"):
            payload = {
                "status": "SUCCESS",
                "groups": [
                    {
                        "name": "Demo Group",
                        "messages": [
                            {"id": "1", "body": "hello", "timestamp_unix": 1},
                            {"id": "2", "body": "world", "timestamp_unix": 2},
                        ],
                    }
                ],
            }
            return subprocess.CompletedProcess(
                args, 0, stdout=json.dumps(payload), stderr=""
            )
        raise AssertionError(f"Unexpected command: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = await bridge.scrape_group(group, max_messages=5)

    assert result.success is True
    assert result.messages_scraped == 2
    assert result.raw_payload is not None


@pytest.mark.asyncio
async def test_scrape_group_handles_missing_node(monkeypatch, tmp_path):
    settings = WebJSSettings(script_dir=str(tmp_path))
    (Path(settings.script_dir) / "whatsapp_webjs_scraper.js").write_text(
        "console.log()", encoding="utf-8"
    )

    for package_name in ("whatsapp-web.js", "qrcode-terminal"):
        (Path(settings.script_dir) / "node_modules" / package_name).mkdir(
            parents=True, exist_ok=True
        )

    def missing_node(args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", missing_node)

    bridge = WhatsAppWebJSBridge(settings)
    group = GroupConfig(name="Demo Group", save_file="demo.json", max_messages=5)

    result = await bridge.scrape_group(group, max_messages=5)

    assert result.success is False
    assert "환경" in result.error
