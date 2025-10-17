"""WhatsApp 미디어 OCR 도구. WhatsApp media OCR utilities."""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import logging
import re
from datetime import datetime
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Sequence, Set


LOGGER = logging.getLogger(__name__)

_EASYOCR_SPEC = importlib.util.find_spec("easyocr")
EASYOCR_AVAILABLE = _EASYOCR_SPEC is not None
if EASYOCR_AVAILABLE:
    from easyocr import Reader  # type: ignore
else:  # pragma: no cover - optional dependency guard
    Reader = None  # type: ignore[assignment]

_PYMUPDF_SPEC = importlib.util.find_spec("fitz")
PYMUPDF_AVAILABLE = _PYMUPDF_SPEC is not None
if PYMUPDF_AVAILABLE:
    import fitz  # type: ignore  # noqa: F401


class MediaOCRProcessor:
    """미디어 OCR 처리기 클래스. Media OCR processor class."""

    def __init__(self, max_file_size_mb: int = 5) -> None:
        self.max_file_size_mb = max_file_size_mb
        self.supported_engines: Set[str] = {"easyocr"}
        if PYMUPDF_AVAILABLE:
            self.supported_engines.add("pymupdf")
        self.processed_files: Set[str] = set()
        self._reader: Optional[Any] = None
        if EASYOCR_AVAILABLE:
            self._reader = Reader(["ko", "en"])  # type: ignore[arg-type]

    def sanitize_ocr_text(self, text: str) -> str:
        """OCR 텍스트 개인정보 마스킹. Mask sensitive data in OCR text."""

        patterns = [
            (r"\d{6}-\d{7}", "[ID_NUMBER]"),
            (r"\d{4}-\d{4}-\d{4}-\d{4}", "[CARD_NUMBER]"),
            (r"[\w.%-]+@[\w.-]+\.[A-Za-z]{2,4}", "[EMAIL]"),
            (r"(\+?\d{2,3}[- ]?)?\d{2,4}[- ]?\d{3,4}[- ]?\d{4}", "[PHONE]"),
        ]

        sanitized = text
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    def get_file_hash(self, file_path: str | Path) -> str:
        """파일 해시(MD5) 계산. Compute MD5 hash of a file."""

        path = Path(file_path)
        hash_md5 = hashlib.md5()
        with path.open("rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    async def process_image(self, file_path: str | Path, engine: str = "easyocr") -> Dict[str, Any]:
        """이미지 OCR 처리. Perform OCR on an image file."""

        chosen_engine = engine.lower()
        file_path = Path(file_path)
        if not file_path.exists():
            return {
                "error": "file_not_found",
                "engine": chosen_engine,
                "timestamp": datetime.utcnow().isoformat(),
            }

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            return {
                "error": "file_too_large",
                "engine": chosen_engine,
                "size_mb": f"{file_size_mb:.2f}",
                "timestamp": datetime.utcnow().isoformat(),
            }

        file_hash = self.get_file_hash(file_path)
        if file_hash in self.processed_files:
            return {
                "text": "",
                "confidence": "0.00",
                "engine": chosen_engine,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat(),
            }

        if chosen_engine not in self.supported_engines:
            return {
                "error": "unsupported_engine",
                "engine": chosen_engine,
                "timestamp": datetime.utcnow().isoformat(),
            }

        if chosen_engine == "easyocr" and not EASYOCR_AVAILABLE:
            return {
                "error": "engine_not_available",
                "engine": chosen_engine,
                "timestamp": datetime.utcnow().isoformat(),
            }

        try:
            if chosen_engine == "easyocr" and self._reader is not None:
                ocr_result = self._reader.readtext(str(file_path))
                text_items: List[str] = []
                confidences: List[float] = []
                for _, text, confidence in ocr_result:
                    text_items.append(text)
                    confidences.append(confidence)
                sanitized_text = self.sanitize_ocr_text("\n".join(text_items))
                confidence_score = (
                    f"{(sum(confidences) / len(confidences)):.2f}"
                    if confidences
                    else "0.00"
                )
                result = {
                    "text": sanitized_text,
                    "confidence": confidence_score,
                    "engine": chosen_engine,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            elif chosen_engine == "pymupdf" and PYMUPDF_AVAILABLE:
                result = {
                    "text": "",
                    "confidence": "0.00",
                    "engine": chosen_engine,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": "not_implemented",
                }
            else:
                result = {
                    "error": "engine_not_available",
                    "engine": chosen_engine,
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as exc:  # pragma: no cover - defensive guard
            LOGGER.error("OCR processing failed: %s", exc)
            result = {
                "error": "processing_failed",
                "engine": chosen_engine,
                "timestamp": datetime.utcnow().isoformat(),
            }

        if "error" not in result:
            self.processed_files.add(file_hash)
        return result


class WhatsAppMediaOCRExtractor:
    """WhatsApp 미디어 OCR 추출기. WhatsApp media OCR extractor."""

    def __init__(self, chat_title: Optional[str] = None) -> None:
        self.chat_title = chat_title or "MR.CHA 전용"
        self.download_root = Path("data/ocr_media")
        self.download_root.mkdir(parents=True, exist_ok=True)
        self.user_data_dir = Path("data/ocr_sessions") / self.sanitize_filename(self.chat_title)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        self.media_processor = MediaOCRProcessor()
        self.media_selectors: List[str] = [
            "div[data-testid='media-viewer']",
            "img[alt='Media']",
        ]
        self.browser_default_arguments: List[str] = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ]

    def sanitize_filename(self, filename: str) -> str:
        """파일명 특수문자 정제. Sanitize filename characters."""

        sanitized = re.sub(r'[\\/:*?"<>|]', "_", filename)
        return sanitized.strip() or "media"

    def _deduplicate_browser_arguments(self, args: Sequence[str]) -> List[str]:
        """브라우저 인수 중복 제거. Deduplicate browser arguments preserving order."""

        seen: Set[str] = set()
        deduplicated: List[str] = []
        for arg in args:
            if arg not in seen:
                deduplicated.append(arg)
                seen.add(arg)
        return deduplicated

    def _combine_browser_arguments(self, *args_lists: Sequence[str]) -> List[str]:
        """브라우저 인수 결합. Combine browser argument sequences."""

        combined: List[str] = []
        for args in args_lists:
            combined.extend(args)
        return self._deduplicate_browser_arguments(combined)

    def _log_browser_arguments(self, args: Sequence[str], context: str) -> None:
        """브라우저 인수 로깅. Log browser arguments for debugging."""

        print(f"[{context}] Browser arguments: {list(args)}")

    def _validate_browser_arguments(self, args: Sequence[str]) -> List[str]:
        """브라우저 인수 검증. Validate browser argument formatting."""

        valid_args: List[str] = []
        for arg in args:
            if not isinstance(arg, str):
                continue
            if not arg.startswith("--"):
                continue
            if len(arg) <= 2 or "=" in arg:
                continue
            valid_args.append(arg)
        return valid_args

    def _get_browser_launch_config(
        self,
        *,
        headless: bool = True,
        ignore_default_args: Optional[Sequence[str]] = None,
        extra_args: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """브라우저 실행 설정 생성. Build browser launch configuration."""

        ignore_defaults = list(ignore_default_args or [])
        validated_extra = self._validate_browser_arguments(extra_args or [])
        combined_args = self._combine_browser_arguments(self.browser_default_arguments, validated_extra)
        config: Dict[str, Any] = {
            "headless": headless,
            "args": combined_args,
        }
        if ignore_defaults:
            config["ignore_default_args"] = ignore_defaults
        return config

    async def find_media_messages(self, page: Any, chat_title: str) -> List[Any]:
        """미디어 메시지 요소 탐색. Locate media message elements."""

        selector = f"span[title='{chat_title}']"
        await page.wait_for_selector(selector, timeout=5000)
        await page.click(selector)
        elements: List[Any] = []
        for media_selector in self.media_selectors:
            try:
                found = await page.query_selector_all(media_selector)
                elements.extend(found)
            except Exception as exc:  # pragma: no cover - defensive guard
                LOGGER.debug("Selector %s lookup failed: %s", media_selector, exc)
        return elements

    async def download_media(self, element: Any, download_dir: str | Path) -> Optional[str]:
        """미디어 파일 다운로드. Download media file from element."""

        target_dir = Path(download_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        file_path = target_dir / f"media_{timestamp}.png"
        await element.screenshot(path=str(file_path))
        return str(file_path)

    async def process_media_file(self, file_path: str | Path, engine: str = "easyocr") -> Dict[str, Any]:
        """미디어 파일 OCR 처리. Process media file with OCR."""

        return await self.media_processor.process_image(file_path, engine=engine)

    async def save_results(self, results: Sequence[Dict[str, Any]], output_file: str | Path) -> None:
        """결과 JSON 저장. Persist OCR results to JSON."""

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        successful = [item for item in results if "error" not in item]
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_processed": len(results),
            "successful": len(successful),
            "confidence_avg": (
                f"{(sum(float(item.get('confidence', 0.0)) for item in successful) / len(successful)):.2f}"
                if successful
                else "0.00"
            ),
            "results": list(results),
        }
        with output_path.open("w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, ensure_ascii=False, indent=2)

    def _cleanup_session_directory(self) -> None:
        """세션 디렉터리 정리. Cleanup session directory on failure."""

        shutil.rmtree(self.user_data_dir, ignore_errors=True)

    def _safe_close_context(self, context: Any) -> None:
        """컨텍스트 안전 종료. Safely close async browser context."""

        try:
            close_coro = context.close()
            asyncio.run(close_coro)
        except Exception as exc:  # pragma: no cover - defensive guard
            print(f"[SAFE_CLOSE] Context close failed: {exc}")

    def _monitor_browser_status(self, page: Any, timeout: int = 10) -> bool:
        """브라우저 상태 모니터링. Monitor browser status during login."""

        for _ in range(timeout):
            if page.is_closed():
                return False
            asyncio.run(asyncio.sleep(0))
        return True

    def _handle_critical_error(self, error: Exception) -> None:
        """치명적 오류 처리. Handle critical browser errors."""

        print(f"[CRITICAL] {error}")
        self._cleanup_session_directory()

    def _log_system_info(self) -> None:
        """시스템 정보 로깅. Log Playwright and Chromium info."""

        print("Playwright Version: 1.0.0 (mock)")
        print("Chromium Info: mock build")

    def _poll_browser_status(self, page: Any, interval: int = 1, max_attempts: int = 3) -> bool:
        """브라우저 상태 폴링. Poll browser status repeatedly."""

        attempts = 0
        while attempts < max_attempts:
            if page.is_closed():
                return False
            attempts += 1
            if attempts >= max_attempts:
                break
            asyncio.run(asyncio.sleep(interval))
        return True

    def _log_debug_info(self, info: Dict[str, Any]) -> None:
        """디버그 정보 로깅. Log operational debug information."""

        print(json.dumps(info, ensure_ascii=False, indent=2))

