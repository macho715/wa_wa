"""WhatsApp Web.js 브릿지 유틸리티입니다. (KR) WhatsApp Web.js bridge utilities. (EN)

Python 환경에서 whatsapp-web.js Node 스크래퍼를 실행하기 위한 비동기 래퍼를 제공합니다.
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from macho_gpt.async_scraper.group_config import GroupConfig, WebJSSettings

LOGGER = logging.getLogger(__name__)


@dataclass
class BridgeResult:
    """브릿지 실행 결과입니다. (KR) Result payload returned by the bridge. (EN)

    Args:
        group_name (str): 대상 그룹 이름입니다.
        success (bool): 실행 성공 여부입니다.
        messages_scraped (int): 수집된 메시지 수입니다.
        error (Optional[str]): 오류 메시지입니다.
        raw_payload (Optional[Dict[str, Any]]): 원본 Node 출력입니다.
    """

    group_name: str
    success: bool
    messages_scraped: int
    error: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None
    messages: Optional[List[Dict[str, Any]]] = None


class WhatsAppWebJSBridge:
    """whatsapp-web.js Python 브릿지입니다. (KR) Python bridge for whatsapp-web.js. (EN)

    Args:
        settings (WebJSSettings): whatsapp-web.js 설정입니다.
        node_path (str): Node 실행 파일 경로입니다.
        npm_path (str): npm 실행 파일 경로입니다.
    """

    def __init__(
        self,
        settings: Optional[WebJSSettings] = None,
        *,
        node_path: str = "node",
        npm_path: str = "npm",
    ) -> None:
        self.settings = settings or WebJSSettings()
        self.node_path = node_path
        self.npm_path = npm_path
        self.script_dir = Path(self.settings.script_dir)
        self.node_script = self.script_dir / "whatsapp_webjs_scraper.js"
        self._environment_ready = False

    async def ensure_environment(self) -> bool:
        """실행 환경을 준비합니다. (KR) Ensure the execution environment is ready. (EN)"""

        if self._environment_ready:
            return True
        if not await self.check_nodejs_available():
            return False
        if not await self.check_dependencies_installed():
            if not self.settings.auto_install_deps:
                LOGGER.error("npm 의존성이 설치되지 않았습니다.")
                return False
            if not await self.install_dependencies():
                return False
        self._environment_ready = True
        return True

    async def check_nodejs_available(self) -> bool:
        """Node.js 사용 가능 여부를 확인합니다. (KR) Check whether Node.js is available. (EN)"""

        try:
            completed = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [self.node_path, "--version"],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=10,
                ),
            )
        except FileNotFoundError:
            LOGGER.error("Node.js 실행 파일을 찾을 수 없습니다.")
            return False
        except subprocess.TimeoutExpired:
            LOGGER.error("Node.js 버전 확인이 시간 초과되었습니다.")
            return False

        if completed.returncode != 0:
            LOGGER.error(
                "Node.js가 올바르게 설치되지 않았습니다: %s", completed.stderr.strip()
            )
            return False

        version_output = completed.stdout.strip()
        LOGGER.debug("Node.js version output: %s", version_output)
        try:
            major_version = int(version_output.lstrip("v").split(".")[0])
        except (ValueError, IndexError):
            LOGGER.warning("Node.js 버전 파싱에 실패했습니다: %s", version_output)
            return True
        if major_version < 14:
            LOGGER.error("Node.js 14 이상이 필요합니다. 현재: %s", version_output)
            return False
        return True

    async def check_dependencies_installed(self) -> bool:
        """필수 npm 패키지가 설치되었는지 확인합니다. (KR) Verify npm dependencies are installed. (EN)"""

        node_modules = self.script_dir / "node_modules"
        if not node_modules.exists():
            return False

        for package_name in ("whatsapp-web.js", "qrcode-terminal"):
            if not (node_modules / package_name).exists():
                LOGGER.debug("누락된 패키지 감지: %s", package_name)
                return False
        return True

    async def install_dependencies(self) -> bool:
        """npm 의존성을 설치합니다. (KR) Install required npm dependencies. (EN)"""

        LOGGER.info("npm 의존성 설치를 실행합니다.")
        try:
            completed = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [self.npm_path, "ci"],
                    cwd=str(self.script_dir),
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=max(self.settings.timeout, 60),
                ),
            )
        except FileNotFoundError:
            LOGGER.error("npm 실행 파일을 찾을 수 없습니다.")
            return False
        except subprocess.TimeoutExpired:
            LOGGER.error("npm ci 명령이 시간 초과되었습니다.")
            return False

        if completed.returncode != 0:
            LOGGER.error("npm ci 실패: %s", completed.stderr.strip())
            return False

        LOGGER.info("npm 의존성이 설치되었습니다.")
        return True

    async def scrape_group(
        self,
        group_config: GroupConfig,
        *,
        max_messages: Optional[int] = None,
    ) -> BridgeResult:
        """단일 그룹을 스크래핑합니다. (KR) Scrape a single WhatsApp group. (EN)

        Args:
            group_config (GroupConfig): 대상 그룹 설정입니다.
            max_messages (Optional[int]): 메시지 수집 상한입니다.
        """

        if not await self.ensure_environment():
            return BridgeResult(
                group_name=group_config.name,
                success=False,
                messages_scraped=0,
                error="Node.js 환경이 준비되지 않았습니다.",
            )

        if not self.node_script.exists():
            return BridgeResult(
                group_name=group_config.name,
                success=False,
                messages_scraped=0,
                error=f"Node 스크립트를 찾을 수 없습니다: {self.node_script}",
            )

        limit = max_messages or group_config.max_messages
        cmd = [
            self.node_path,
            str(self.node_script),
            group_config.name,
            str(limit),
        ]

        LOGGER.info("webjs 스크립트를 실행합니다: %s", " ".join(cmd))

        try:
            completed = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    cwd=str(self.script_dir),
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=self.settings.timeout,
                ),
            )
        except subprocess.TimeoutExpired:
            LOGGER.error("webjs 스크립트가 시간 초과되었습니다.")
            return BridgeResult(
                group_name=group_config.name,
                success=False,
                messages_scraped=0,
                error="whatsapp-web.js 실행이 시간 초과되었습니다.",
            )

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        if stderr:
            LOGGER.debug("webjs stderr: %s", stderr)

        payload: Dict[str, Any]
        try:
            payload = json.loads(stdout) if stdout else {}
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
            LOGGER.error("JSON 파싱 실패: %s", exc)
            return BridgeResult(
                group_name=group_config.name,
                success=False,
                messages_scraped=0,
                error="whatsapp-web.js 출력 파싱 실패",
            )

        status = payload.get("status", "FAIL")
        if completed.returncode != 0 or status != "SUCCESS":
            error_message = payload.get("error") or stderr or "알 수 없는 오류"
            LOGGER.error("webjs 스크립트 실패: %s", error_message)
            return BridgeResult(
                group_name=group_config.name,
                success=False,
                messages_scraped=0,
                error=error_message,
                raw_payload=payload or None,
            )

        groups = payload.get("groups", [])
        messages: List[Dict[str, Any]] = []
        for group_entry in groups:
            if group_entry.get("name") == group_config.name:
                messages = group_entry.get("messages", [])
                break
        else:
            LOGGER.warning("타깃 그룹이 결과에 없습니다: %s", group_config.name)
            messages = groups[0].get("messages", []) if groups else []

        return BridgeResult(
            group_name=group_config.name,
            success=True,
            messages_scraped=len(messages),
            raw_payload=payload,
            messages=messages,
        )

    async def scrape_groups(
        self, group_configs: List[GroupConfig], *, max_messages: Optional[int] = None
    ) -> List[BridgeResult]:
        """여러 그룹을 순차로 스크래핑합니다. (KR) Scrape multiple groups sequentially. (EN)"""

        results: List[BridgeResult] = []
        for group_config in group_configs:
            result = await self.scrape_group(group_config, max_messages=max_messages)
            results.append(result)
        return results


async def scrape_whatsapp_group(
    group_config: GroupConfig,
    *,
    max_messages: Optional[int] = None,
    settings: Optional[WebJSSettings] = None,
) -> BridgeResult:
    """헬퍼 함수로 단일 그룹을 스크래핑합니다. (KR) Convenience wrapper to scrape one group. (EN)"""

    bridge = WhatsAppWebJSBridge(settings)
    return await bridge.scrape_group(group_config, max_messages=max_messages)


async def check_webjs_environment(
    settings: Optional[WebJSSettings] = None,
) -> Dict[str, Any]:
    """whatsapp-web.js 실행 환경을 점검합니다. (KR) Inspect the whatsapp-web.js environment. (EN)"""

    bridge = WhatsAppWebJSBridge(settings)
    return {
        "nodejs_available": await bridge.check_nodejs_available(),
        "dependencies_installed": await bridge.check_dependencies_installed(),
        "script_exists": bridge.node_script.exists(),
        "package_json_exists": (bridge.script_dir / "package.json").exists(),
    }


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="whatsapp-web.js bridge CLI")
    parser.add_argument("group", help="스크래핑할 그룹 이름")
    parser.add_argument("max_messages", nargs="?", type=int, default=50)
    args = parser.parse_args()

    async def _main() -> None:
        settings = WebJSSettings()
        group = GroupConfig(
            name=args.group,
            save_file="bridge_cli.json",
            max_messages=args.max_messages,
        )
        result = await scrape_whatsapp_group(group, settings=settings)
        print(json.dumps(result.raw_payload or {}, ensure_ascii=False, indent=2))

    asyncio.run(_main())
