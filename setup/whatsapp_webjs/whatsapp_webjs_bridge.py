"""whatsapp-web.js 브릿지 모듈/whatsapp-web.js bridge module."""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


@dataclass(slots=True)
class WebJSEnvironmentStatus:
    """whatsapp-web.js 환경 상태/whatsapp-web.js environment status."""

    node_available: bool
    npm_available: bool
    dependencies_installed: bool
    script_exists: bool
    package_json_exists: bool
    timestamp: str


class WhatsAppWebJSBridge:
    """whatsapp-web.js 연동 브릿지/Bridge for whatsapp-web.js integration."""

    def __init__(
        self,
        *,
        script_dir: Optional[str | Path] = None,
        timeout: int = 300,
        auto_install_deps: bool = True,
    ) -> None:
        """브릿지 초기화/Initialise the bridge."""

        self.script_dir = (
            Path(script_dir).resolve()
            if script_dir
            else Path(__file__).resolve().parent
        )
        self.script_path = self.script_dir / "whatsapp_webjs_scraper.js"
        self.timeout = timeout
        self.auto_install_deps = auto_install_deps
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def ensure_ready(self) -> None:
        """실행 전 환경 준비/Prepare environment before execution."""

        self.logger.debug("Checking whatsapp-web.js environment readiness")

        if not self._is_node_available():
            raise EnvironmentError("Node.js executable not found in PATH")

        if not self.script_path.exists():
            raise FileNotFoundError(f"Script not found: {self.script_path}")

        if not self._dependencies_installed():
            if not self.auto_install_deps:
                raise EnvironmentError("Dependencies missing and auto-install disabled")
            await self.install_dependencies()

    async def install_dependencies(self) -> None:
        """npm 의존성 설치/Install npm dependencies."""

        npm_command = (
            "ci" if (self.script_dir / "package-lock.json").exists() else "install"
        )
        self.logger.info(
            "Installing whatsapp-web.js dependencies via npm %s", npm_command
        )

        process = await asyncio.create_subprocess_exec(
            "npm",
            npm_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.script_dir),
        )
        stdout_bytes, stderr_bytes = await process.communicate()

        self._log_subprocess_stream(stdout_bytes, level=logging.DEBUG)
        self._log_subprocess_stream(stderr_bytes, level=logging.INFO)

        if process.returncode != 0:
            raise RuntimeError(
                "Failed to install npm dependencies: " f"exit code {process.returncode}"
            )

    async def scrape_group(
        self,
        group_name: str,
        *,
        limit: int = 50,
        include_media: bool = False,
    ) -> Dict[str, Any]:
        """단일 그룹 스크랩/Scrape a single WhatsApp group."""

        result = await self.scrape_groups(
            [group_name],
            limit=limit,
            include_media=include_media,
            group_limits={group_name: limit},
        )
        groups = result.get("groups", [])
        if groups:
            return {
                "status": result.get("status", "UNKNOWN"),
                "timestamp": result.get("timestamp"),
                "group": groups[0],
                "errors": result.get("errors", []),
            }
        return result

    async def scrape_groups(
        self,
        group_names: Sequence[str],
        *,
        limit: int = 50,
        include_media: bool = False,
        group_limits: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """다중 그룹 스크랩/Scrape multiple WhatsApp groups."""

        if not group_names:
            raise ValueError("At least one group name must be provided")

        await self.ensure_ready()

        command: List[str] = [
            "node",
            str(self.script_path),
            "--limit",
            str(limit),
            "--timeout",
            str(self.timeout),
        ]

        if include_media:
            command.append("--include-media")

        for name in group_names:
            command.extend(["--group", name])

        if group_limits:
            for name, value in group_limits.items():
                command.extend(["--group-limit", f"{name}={value}"])

        self.logger.info("Executing whatsapp-web.js scraper: %s", " ".join(command))

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.script_dir),
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(), timeout=self.timeout
            )
        except asyncio.TimeoutError as exc:
            process.kill()
            raise TimeoutError("whatsapp-web.js scraper timed out") from exc

        self._log_subprocess_stream(stderr_bytes, level=logging.INFO)

        if process.returncode != 0:
            raise RuntimeError(
                "whatsapp-web.js scraper exited with code " f"{process.returncode}"
            )

        return self._parse_json(stdout_bytes)

    async def cleanup_session(self) -> bool:
        """세션 데이터 정리/Clean whatsapp-web.js session data."""

        auth_dir = self.script_dir / ".wwebjs_auth"
        if auth_dir.exists():
            shutil.rmtree(auth_dir)
            self.logger.info("whatsapp-web.js session directory removed")
        return True

    async def inspect_environment(self) -> WebJSEnvironmentStatus:
        """환경 상태 조회/Inspect current environment status."""

        status = WebJSEnvironmentStatus(
            node_available=self._is_node_available(),
            npm_available=self._is_npm_available(),
            dependencies_installed=self._dependencies_installed(),
            script_exists=self.script_path.exists(),
            package_json_exists=(self.script_dir / "package.json").exists(),
            timestamp=datetime.utcnow().isoformat(),
        )
        return status

    def _is_node_available(self) -> bool:
        """Node.js 가용성 확인/Check Node.js availability."""

        return shutil.which("node") is not None

    def _is_npm_available(self) -> bool:
        """npm 가용성 확인/Check npm availability."""

        return shutil.which("npm") is not None

    def _dependencies_installed(self) -> bool:
        """npm 의존성 설치 여부/Check npm dependencies installed."""

        node_modules = self.script_dir / "node_modules"
        required = [
            node_modules / "whatsapp-web.js",
            node_modules / "qrcode-terminal",
        ]
        return all(path.exists() for path in required)

    def _parse_json(self, payload: bytes) -> Dict[str, Any]:
        """JSON 파싱 실행/Parse JSON payload from scraper."""

        try:
            decoded = payload.decode("utf-8").strip()
            return json.loads(decoded) if decoded else {}
        except json.JSONDecodeError as error:
            self.logger.error("Failed to parse whatsapp-web.js output: %s", decoded)
            raise ValueError(
                "Invalid JSON output from whatsapp-web.js scraper"
            ) from error

    def _log_subprocess_stream(self, payload: bytes, *, level: int) -> None:
        """서브프로세스 출력 로깅/Log subprocess stream payload."""

        if not payload:
            return

        text = payload.decode("utf-8", errors="ignore")
        for line in text.splitlines():
            self.logger.log(level, "[webjs] %s", line)


async def scrape_whatsapp_group(
    group_name: str,
    *,
    limit: int = 50,
    include_media: bool = False,
    timeout: int = 300,
) -> Dict[str, Any]:
    """단일 그룹 스크랩 편의 함수/Convenience wrapper to scrape one group."""

    bridge = WhatsAppWebJSBridge(timeout=timeout)
    return await bridge.scrape_group(
        group_name, limit=limit, include_media=include_media
    )


async def check_webjs_environment() -> Dict[str, Any]:
    """whatsapp-web.js 환경 상태 확인/Inspect whatsapp-web.js environment."""

    bridge = WhatsAppWebJSBridge()
    status = await bridge.inspect_environment()
    return status.__dict__


# CLI 테스트용
if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="whatsapp-web.js bridge tester")
    parser.add_argument("group", help="Group name to scrape")
    parser.add_argument(
        "--limit", type=int, default=50, help="Number of messages to fetch"
    )
    parser.add_argument(
        "--include-media",
        action="store_true",
        help="Include base64 media payloads",
    )
    args = parser.parse_args()

    async def _main() -> None:
        result = await scrape_whatsapp_group(
            args.group,
            limit=args.limit,
            include_media=args.include_media,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    asyncio.run(_main())
