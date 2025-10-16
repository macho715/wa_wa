"""
MACHO-GPT v3.4-mini WhatsApp 메시지 처리 모듈
--------------------------------------------
Samsung C&T Logistics · HVDC Project
파일명: logi_whatsapp_241219.py

기능:
- WhatsApp 메시지 텍스트 파싱
- 긴급/중요 메시지 자동 분류
- AI 요약을 위한 데이터 구조화
- KPI 지표 생성
Samsung C&T Logistics · HVDC Project
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class WhatsAppMessage:
    """WhatsApp 메시지 구조체"""

    timestamp: datetime
    sender: str
    content: str
    is_urgent: bool = False
    is_important: bool = False
    message_type: str = "text"  # text, media, system


class WhatsAppProcessor:
    """
    MACHO-GPT WhatsApp 메시지 처리 클래스

    Mode: PRIME (기본 모드)
    Confidence: ≥0.90 필요
    """

    def __init__(self, mode: str = "PRIME"):
        self.mode = mode
        self.confidence_threshold = 0.90
        self.urgent_patterns = [
            r"\b긴급\b",
            r"긴급히",
            r"\burgent\b",
            r"\bimmediate\b",
            r"\bcritical\b",
            r"\bASAP\b",
            r"\b응급\b",
            r"\b즉시\b",
        ]
        self.important_patterns = [
            r"\b중요\b",
            r"\bimportant\b",
            r"\bapproval\b",
            r"\b승인\b",
            r"\b확인\b",
            r"\bdecision\b",
            r"\b결정\b",
        ]

    def parse_whatsapp_text(self, raw_text: str) -> List[WhatsAppMessage]:
        """
        WhatsApp 텍스트를 구조화된 메시지로 파싱

        Args:
            raw_text: 복사된 WhatsApp 텍스트

        Returns:
            List[WhatsAppMessage]: 파싱된 메시지 리스트

        Triggers:
            - 메시지 파싱 실패 시 ZERO 모드 전환
            - 긴급 키워드 감지 시 자동 태그
        """
        messages = []
        lines = raw_text.strip().split("\n")

        for line in lines:
            if not line.strip():
                continue

            # WhatsApp 메시지 패턴 매칭
            # 패턴: [YYYY-MM-DD HH:MM:SS] Sender: Message
            # 또는: [MM/DD/YY, HH:MM:SS PM] Sender: Message
            message = self._parse_single_message(line)
            if message:
                messages.append(message)

        return messages

    def _parse_single_message(self, line: str) -> Optional[WhatsAppMessage]:
        """단일 메시지 라인 파싱"""
        # 다양한 WhatsApp 시간 형식 지원
        patterns = [
            r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] ([^:]+): (.+)",
            r"\[(\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}:\d{2} [AP]M)\] ([^:]+): (.+)",
            r"(\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2} [AP]M) - ([^:]+): (.+)",
        ]

        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                timestamp_str, sender, content = match.groups()

                # 타임스탬프 파싱
                timestamp = self._parse_timestamp(timestamp_str)
                if not timestamp:
                    continue

                # 긴급/중요 분류
                is_urgent = self._is_urgent(content)
                is_important = self._is_important(content)

                return WhatsAppMessage(
                    timestamp=timestamp,
                    sender=sender.strip(),
                    content=content.strip(),
                    is_urgent=is_urgent,
                    is_important=is_important,
                )

        return None

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """타임스탬프 문자열을 datetime 객체로 변환"""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%y, %I:%M:%S %p",
            "%m/%d/%y, %I:%M %p",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        return None

    def _is_urgent(self, content: str) -> bool:
        """긴급 키워드 검사"""
        return any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.urgent_patterns
        )

    def _is_important(self, content: str) -> bool:
        """중요 키워드 검사"""
        return any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.important_patterns
        )

    def extract_summary_data(self, messages: List[WhatsAppMessage]) -> Dict:
        """
        AI 요약을 위한 데이터 추출

        Returns:
            dict: {
                'status': 'SUCCESS|FAIL',
                'confidence': float,
                'mode': str,
                'urgent_messages': list,
                'important_messages': list,
                'participants': set,
                'time_range': tuple,
                'message_count': int,
                'triggers': list,
                'next_cmds': list
            }
        """
        if not messages:
            return {
                "status": "FAIL",
                "confidence": 0.0,
                "mode": self.mode,
                "urgent_messages": [],
                "important_messages": [],
                "participants": set(),
                "time_range": None,
                "message_count": 0,
                "triggers": ["/switch_mode ZERO"],
                "next_cmds": ["/logi-master --fallback"],
            }

        urgent_messages = [msg for msg in messages if msg.is_urgent]
        important_messages = [msg for msg in messages if msg.is_important]
        participants = {msg.sender for msg in messages}

        time_range = (
            min(msg.timestamp for msg in messages),
            max(msg.timestamp for msg in messages),
        )

        # 자동 트리거 조건 확인
        triggers = []
        if len(urgent_messages) > 5:
            triggers.append("/alert_system urgent_threshold_exceeded")
        if len(participants) > 10:
            triggers.append("/team_coordination large_group_detected")

        # 다음 명령어 추천
        next_cmds = [
            "/logi-master summarize",
            "/visualize_data --type=timeline",
            "/kpi_monitor message_analysis",
        ]

        confidence = self._calculate_confidence(messages)

        return {
            "status": (
                "SUCCESS" if confidence >= self.confidence_threshold else "PARTIAL"
            ),
            "confidence": confidence,
            "mode": self.mode,
            "urgent_messages": urgent_messages,
            "important_messages": important_messages,
            "participants": participants,
            "time_range": time_range,
            "message_count": len(messages),
            "triggers": triggers,
            "next_cmds": next_cmds,
        }

    def _calculate_confidence(self, messages: List[WhatsAppMessage]) -> float:
        """메시지 파싱 품질 기반 신뢰도 계산"""
        if not messages:
            return 0.0

        # 타임스탬프가 있는 메시지 비율
        valid_timestamp_ratio = len(messages) / len(
            messages
        )  # 모든 메시지가 파싱되었다면 1.0

        # 발신자 정보가 있는 메시지 비율
        valid_sender_ratio = len([msg for msg in messages if msg.sender]) / len(
            messages
        )

        # 내용이 있는 메시지 비율
        valid_content_ratio = len(
            [msg for msg in messages if msg.content.strip()]
        ) / len(messages)

        # 가중 평균으로 신뢰도 계산
        confidence = (
            valid_timestamp_ratio * 0.4
            + valid_sender_ratio * 0.3
            + valid_content_ratio * 0.3
        )

        return round(confidence, 2)

    def generate_kpi_summary(self, messages: List[WhatsAppMessage]) -> Dict:
        """KPI 요약 생성"""
        if not messages:
            return {}

        total_messages = len(messages)
        urgent_count = len([msg for msg in messages if msg.is_urgent])
        important_count = len([msg for msg in messages if msg.is_important])
        participant_count = len({msg.sender for msg in messages})

        # 시간대별 분포
        hour_distribution = {}
        for msg in messages:
            hour = msg.timestamp.hour
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1

        return {
            "total_messages": total_messages,
            "urgent_count": urgent_count,
            "important_count": important_count,
            "participant_count": participant_count,
            "urgent_ratio": (
                round(urgent_count / total_messages, 2) if total_messages > 0 else 0
            ),
            "important_ratio": (
                round(important_count / total_messages, 2) if total_messages > 0 else 0
            ),
            "hour_distribution": hour_distribution,
            "peak_hour": (
                max(hour_distribution.items(), key=lambda x: x[1])[0]
                if hour_distribution
                else None
            ),
        } 