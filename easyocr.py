"""EasyOCR 모듈 스텁. EasyOCR module stub for tests."""

from __future__ import annotations

from typing import List, Sequence, Tuple


class Reader:
    """테스트용 OCR 리더 스텁. Stub OCR reader for tests."""

    def __init__(self, languages: Sequence[str]):
        self.languages = list(languages)

    def readtext(self, image_path: str) -> List[Tuple[None, str, float]]:
        """OCR 결과 스텁 반환. Return stub OCR results."""

        return []
