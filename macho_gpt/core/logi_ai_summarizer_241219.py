"""WhatsApp AI 요약기. WhatsApp AI summarizer for HVDC project."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import openai
import yaml

from .role_config import (
    RoleConfigManager,
    create_system_message,
    get_role_status,
)


def _default_logger() -> logging.Logger:
    """로거 생성. Create module logger."""

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


@dataclass
class SummaryResult:
    """요약 결과 데이터. Summary payload container."""

    summary: str
    tasks: List[str]
    urgent: str
    important: str

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환. Convert to dictionary."""

        return {
            "summary": self.summary,
            "tasks": self.tasks,
            "urgent": self.urgent,
            "important": self.important,
        }


class LogiAISummarizer:
    """MACHO-GPT WhatsApp 요약기. MACHO-GPT WhatsApp summarizer."""

    def __init__(self, mode: str = "LATTICE", config_path: str = "configs/openai_config.yaml") -> None:
        self.logger = _default_logger()
        self.mode = mode
        self.confidence_threshold = 0.90
        self.version = "3.4-mini"
        self.role_manager = RoleConfigManager()
        self.config = self._load_config(config_path)
        self._setup_openai()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """설정 파일 로드. Load configuration file."""

        try:
            with open(config_path, "r", encoding="utf-8") as file_handle:
                return yaml.safe_load(file_handle) or {}
        except FileNotFoundError:
            self.logger.warning("Config file not found, using defaults")
            return {}

    def _setup_openai(self) -> None:
        """OpenAI 설정. Configure OpenAI client."""

        api_key = os.getenv("OPENAI_API_KEY") or self.config.get("openai", {}).get("api_key")
        if api_key:
            openai.api_key = api_key
            self.logger.info("OpenAI API key configured")
        else:
            self.logger.info("OpenAI API key missing; using mock mode")

    def _get_task_prompt(self) -> str:
        """태스크 프롬프트 제공. Provide task prompt."""

        return (
            "WhatsApp 대화를 분석하여 핵심 요약, 태스크 목록, 긴급 사항, 중요 사항을 정리하세요. "
            "HVDC 프로젝트와 ADNOC·DSV 협력, 계약/통관 정보를 반영하세요."
        )

    def _extract_summary_sections(self, content: str) -> SummaryResult:
        """AI 응답 섹션 추출. Extract summary sections from AI content."""

        def _section(label: str) -> str:
            marker = f"**{label}:**"
            if marker not in content:
                return ""
            segment = content.split(marker, 1)[1]
            return segment.split("**", 1)[0].strip().strip("- ")

        tasks_block = _section("태스크")
        tasks = [line.strip("- ").strip() for line in tasks_block.splitlines() if line.strip()]
        return SummaryResult(
            summary=_section("요약"),
            tasks=tasks,
            urgent=_section("긴급"),
            important=_section("중요"),
        )

    def summarize_conversation(self, messages: Sequence[str]) -> Dict[str, Any]:
        """대화 요약 실행. Summarize WhatsApp conversation."""

        system_message = create_system_message(self._get_task_prompt(), self.mode)
        conversation_text = "\n".join(messages)
        user_prompt = (
            f"{self._get_task_prompt()}\n\n"
            f"대화 내용:\n{conversation_text}"
        )
        response = openai.chat.completions.create(
            model=self.config.get("openai", {}).get("model", "gpt-4o-mini"),
            messages=[system_message, {"role": "user", "content": user_prompt}],
            temperature=self.config.get("openai", {}).get("temperature", 0.3),
            max_tokens=self.config.get("openai", {}).get("max_tokens", 2000),
        )
        summary = self._extract_summary_sections(response.choices[0].message.content)
        return summary.to_dict()

    def analyze_chat_messages(self, messages: Sequence[str], chat_title: str) -> Dict[str, Any]:
        """채팅 메시지 분석. Analyze chat messages."""

        try:
            summary = self.summarize_conversation(messages)
            return {
                "chat_title": chat_title,
                "message_count": len(messages),
                "analysis": summary,
                "timestamp": datetime.now().isoformat(),
                "confidence": self.confidence_threshold,
            }
        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.error("Analysis failed: %s", exc)
            return {
                "chat_title": chat_title,
                "message_count": len(messages),
                "analysis": {"error": str(exc)},
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.00,
            }

    def analyze_extraction_file(self, file_path: str) -> Dict[str, Any]:
        """추출 파일 분석. Analyze extraction JSON file."""

        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except FileNotFoundError:
            return {"error": "file_not_found"}

        results: List[Dict[str, Any]] = []
        total_messages = 0
        for chat_data in data:
            if chat_data.get("status") != "SUCCESS":
                continue
            messages = chat_data.get("messages", [])
            if not messages:
                continue
            chat_title = chat_data.get("chat_title", "Unknown")
            self.logger.info("Analyzing %s (%s messages)", chat_title, len(messages))
            analysis = self.analyze_chat_messages(messages, chat_title)
            results.append(analysis)
            total_messages += len(messages)

        report = {
            "total_chats_analyzed": len(results),
            "total_messages": total_messages,
            "analysis_timestamp": datetime.now().isoformat(),
            "chat_analyses": results,
            "overall_summary": self._create_overall_summary(results),
        }
        return report

    def _create_overall_summary(self, analyses: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        """전체 요약 생성. Create overall summary from analyses."""

        keywords: List[str] = []
        urgent_items: List[str] = []
        important_items: List[str] = []
        for analysis in analyses:
            payload = analysis.get("analysis", {})
            if isinstance(payload, dict):
                keywords.extend(payload.get("tasks", []))
                urgent = payload.get("urgent")
                important = payload.get("important")
                if urgent:
                    urgent_items.append(urgent)
                if important:
                    important_items.append(important)
        return {
            "total_keywords": len(keywords),
            "urgent_notes": urgent_items,
            "important_notes": important_items,
        }

    def save_analysis(self, analysis: Dict[str, Any], output_path: str) -> None:
        """분석 결과 저장. Save analysis to file."""

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(analysis, handle, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict[str, Any]:
        """상태 정보 반환. Return summarizer status."""

        return {
            "mode": self.mode,
            "version": self.version,
            "confidence_threshold": self.confidence_threshold,
            "role_config": get_role_status(),
            "status": "ready",
        }


def main() -> None:
    """수동 테스트 진입점. Manual test entry point."""

    summarizer = LogiAISummarizer()
    sample_messages = ["테스트 메시지 1", "테스트 메시지 2"]
    print(summarizer.analyze_chat_messages(sample_messages, "Demo Chat"))


if __name__ == "__main__":
    main()
