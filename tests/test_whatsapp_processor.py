"""
WhatsApp 프로세서 테스트 모듈
----------------------------------
Samsung C&T Logistics · HVDC Project
파일명: test_whatsapp_processor.py

TDD 접근 방식으로 작성된 테스트 케이스
"""

import pytest
from datetime import datetime
from typing import List

from macho_gpt.core.logi_whatsapp_241219 import WhatsAppProcessor, WhatsAppMessage


class TestWhatsAppProcessor:
    """WhatsApp 프로세서 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.processor = WhatsAppProcessor(mode="PRIME")
        
        # 테스트 데이터
        self.sample_whatsapp_text = """
[2024-12-19 09:00:00] MR.CHA: 좋은 아침입니다. 오늘 회의 준비 상황 공유드립니다.
[2024-12-19 09:01:00] 팀장: 네, 확인했습니다. 긴급 사항이 있나요?
[2024-12-19 09:02:00] MR.CHA: 네, 긴급히 검토가 필요한 문서가 있습니다.
[2024-12-19 09:03:00] 팀원A: 중요한 승인 건이 있어서 확인 부탁드립니다.
[2024-12-19 09:04:00] 팀원B: ASAP 처리 부탁드립니다.
"""
    
    def test_processor_initialization(self):
        """프로세서 초기화 테스트"""
        # Given: 프로세서 생성
        processor = WhatsAppProcessor(mode="PRIME")
        
        # Then: 기본 설정 확인
        assert processor.mode == "PRIME"
        assert processor.confidence_threshold == 0.90
        assert len(processor.urgent_patterns) > 0
        assert len(processor.important_patterns) > 0
    
    def test_parse_whatsapp_text_success(self):
        """WhatsApp 텍스트 파싱 성공 테스트"""
        # Given: 샘플 WhatsApp 텍스트
        
        # When: 텍스트 파싱
        messages = self.processor.parse_whatsapp_text(self.sample_whatsapp_text)
        
        # Then: 메시지 파싱 확인
        assert len(messages) == 5
        assert all(isinstance(msg, WhatsAppMessage) for msg in messages)
        
        # 첫 번째 메시지 확인
        first_msg = messages[0]
        assert first_msg.sender == "MR.CHA"
        assert "좋은 아침입니다" in first_msg.content
        assert first_msg.timestamp.year == 2024
        assert first_msg.timestamp.month == 12
        assert first_msg.timestamp.day == 19
    
    def test_parse_empty_text(self):
        """빈 텍스트 파싱 테스트"""
        # Given: 빈 텍스트
        empty_text = ""
        
        # When: 텍스트 파싱
        messages = self.processor.parse_whatsapp_text(empty_text)
        
        # Then: 빈 리스트 반환
        assert len(messages) == 0
    
    def test_urgent_keyword_detection(self):
        """긴급 키워드 감지 테스트"""
        # Given: 긴급 키워드가 포함된 텍스트
        
        # When: 텍스트 파싱
        messages = self.processor.parse_whatsapp_text(self.sample_whatsapp_text)
        
        # Then: 긴급 메시지 식별
        urgent_messages = [msg for msg in messages if msg.is_urgent]
        assert len(urgent_messages) >= 2  # "긴급히", "ASAP" 포함
        
        # 구체적인 긴급 메시지 확인
        urgent_contents = [msg.content for msg in urgent_messages]
        assert any("긴급히" in content for content in urgent_contents)
        assert any("ASAP" in content for content in urgent_contents)
    
    def test_important_keyword_detection(self):
        """중요 키워드 감지 테스트"""
        # Given: 중요 키워드가 포함된 텍스트
        
        # When: 텍스트 파싱
        messages = self.processor.parse_whatsapp_text(self.sample_whatsapp_text)
        
        # Then: 중요 메시지 식별
        important_messages = [msg for msg in messages if msg.is_important]
        assert len(important_messages) >= 1  # "중요한", "승인", "확인" 포함
        
        # 구체적인 중요 메시지 확인
        important_contents = [msg.content for msg in important_messages]
        assert any("중요한" in content for content in important_contents)
        assert any("승인" in content for content in important_contents)
    
    def test_extract_summary_data_success(self):
        """요약 데이터 추출 성공 테스트"""
        # Given: 파싱된 메시지
        messages = self.processor.parse_whatsapp_text(self.sample_whatsapp_text)
        
        # When: 요약 데이터 추출
        summary_data = self.processor.extract_summary_data(messages)
        
        # Then: 요약 데이터 확인
        assert summary_data['status'] == 'SUCCESS'
        assert summary_data['confidence'] >= 0.90
        assert summary_data['mode'] == 'PRIME'
        assert summary_data['message_count'] == 5
        assert len(summary_data['participants']) >= 3
        assert summary_data['time_range'] is not None
        assert len(summary_data['urgent_messages']) >= 2
        assert len(summary_data['important_messages']) >= 1
    
    def test_extract_summary_data_empty(self):
        """빈 메시지 목록 요약 데이터 추출 테스트"""
        # Given: 빈 메시지 목록
        empty_messages = []
        
        # When: 요약 데이터 추출
        summary_data = self.processor.extract_summary_data(empty_messages)
        
        # Then: 실패 상태 확인
        assert summary_data['status'] == 'FAIL'
        assert summary_data['confidence'] == 0.0
        assert summary_data['message_count'] == 0
        assert len(summary_data['triggers']) > 0
        assert '/switch_mode ZERO' in summary_data['triggers']
    
    def test_calculate_confidence_high(self):
        """높은 신뢰도 계산 테스트"""
        # Given: 완전한 메시지 목록
        messages = self.processor.parse_whatsapp_text(self.sample_whatsapp_text)
        
        # When: 신뢰도 계산
        confidence = self.processor._calculate_confidence(messages)
        
        # Then: 높은 신뢰도 확인
        assert confidence >= 0.90
        assert confidence <= 1.0
    
    def test_generate_kpi_summary(self):
        """KPI 요약 생성 테스트"""
        # Given: 파싱된 메시지
        messages = self.processor.parse_whatsapp_text(self.sample_whatsapp_text)
        
        # When: KPI 요약 생성
        kpi_data = self.processor.generate_kpi_summary(messages)
        
        # Then: KPI 데이터 확인
        assert kpi_data['total_messages'] == 5
        assert kpi_data['urgent_count'] >= 2
        assert kpi_data['important_count'] >= 1
        assert kpi_data['participant_count'] >= 3
        assert 0 <= kpi_data['urgent_ratio'] <= 1
        assert 0 <= kpi_data['important_ratio'] <= 1
        assert kpi_data['peak_hour'] is not None
    
    def test_mode_switching_triggers(self):
        """모드 전환 트리거 테스트"""
        # Given: 많은 긴급 메시지가 있는 텍스트
        urgent_text = """
[2024-12-19 09:00:00] User1: 긴급 상황입니다!
[2024-12-19 09:01:00] User2: urgent 처리 필요
[2024-12-19 09:02:00] User3: immediate action required
[2024-12-19 09:03:00] User4: critical issue
[2024-12-19 09:04:00] User5: ASAP 확인 부탁
[2024-12-19 09:05:00] User6: 응급 상황
"""
        
        # When: 메시지 파싱 및 요약 데이터 추출
        messages = self.processor.parse_whatsapp_text(urgent_text)
        summary_data = self.processor.extract_summary_data(messages)
        
        # Then: 자동 트리거 확인
        assert len(summary_data['urgent_messages']) > 5
        assert '/alert_system urgent_threshold_exceeded' in summary_data['triggers']
    
    def test_timestamp_parsing_formats(self):
        """다양한 타임스탬프 형식 파싱 테스트"""
        # Given: 다양한 형식의 타임스탬프
        different_formats = """
[2024-12-19 09:00:00] User1: Format 1
[12/19/24, 9:01:00 AM] User2: Format 2
12/19/24, 9:02 AM - User3: Format 3
"""
        
        # When: 텍스트 파싱
        messages = self.processor.parse_whatsapp_text(different_formats)
        
        # Then: 모든 형식 파싱 확인
        assert len(messages) >= 2  # 최소 2개 이상 파싱되어야 함
        assert all(msg.timestamp is not None for msg in messages)
    
    def test_confidence_threshold_enforcement(self):
        """신뢰도 임계값 강제 적용 테스트"""
        # Given: 낮은 품질의 텍스트 (타임스탬프 없음)
        low_quality_text = """
User1: 안녕하세요
User2: 네 안녕하세요
User3: 오늘 날씨가 좋네요
"""
        
        # When: 텍스트 파싱
        messages = self.processor.parse_whatsapp_text(low_quality_text)
        
        # Then: 신뢰도 확인
        if messages:  # 일부 메시지가 파싱되었다면
            summary_data = self.processor.extract_summary_data(messages)
            # 신뢰도가 임계값 이하일 경우 PARTIAL 상태
            if summary_data['confidence'] < 0.90:
                assert summary_data['status'] == 'PARTIAL'


# 통합 테스트 클래스
class TestWhatsAppProcessorIntegration:
    """WhatsApp 프로세서 통합 테스트"""
    
    def test_full_processing_pipeline(self):
        """전체 처리 파이프라인 테스트"""
        # Given: 실제 WhatsApp 메시지 형태의 텍스트
        real_whatsapp_text = """
[2024-12-19 14:30:00] MR.CHA: 안녕하세요. 오늘 프로젝트 상황을 공유드립니다.
[2024-12-19 14:31:00] 팀장Kim: 네, 확인하겠습니다. 현재 진행 상황은 어떤가요?
[2024-12-19 14:32:00] MR.CHA: 긴급히 검토가 필요한 문서가 있습니다. 승인 부탁드립니다.
[2024-12-19 14:33:00] 팀원Lee: 중요한 일정 변경이 있어서 확인 필요합니다.
[2024-12-19 14:34:00] 팀원Park: ASAP 처리 부탁드립니다.
[2024-12-19 14:35:00] 팀장Kim: 네, 바로 확인하겠습니다.
"""
        
        # When: 전체 파이프라인 실행
        processor = WhatsAppProcessor(mode="PRIME")
        messages = processor.parse_whatsapp_text(real_whatsapp_text)
        summary_data = processor.extract_summary_data(messages)
        kpi_data = processor.generate_kpi_summary(messages)
        
        # Then: 모든 단계 성공적 완료 확인
        assert len(messages) == 6
        assert summary_data['status'] == 'SUCCESS'
        assert summary_data['confidence'] >= 0.90
        assert kpi_data['total_messages'] == 6
        assert kpi_data['urgent_count'] >= 2
        assert kpi_data['important_count'] >= 1
        assert len(summary_data['next_cmds']) >= 3
        
        # MACHO-GPT 요구사항 확인
        assert summary_data['mode'] == 'PRIME'
        assert '/logi-master summarize' in summary_data['next_cmds']


# 픽스처 및 헬퍼 함수
@pytest.fixture
def sample_processor():
    """테스트용 프로세서 인스턴스"""
    return WhatsAppProcessor(mode="PRIME")


@pytest.fixture
def sample_messages():
    """테스트용 메시지 데이터"""
    return [
        WhatsAppMessage(
            timestamp=datetime(2024, 12, 19, 9, 0, 0),
            sender="MR.CHA",
            content="긴급 상황입니다",
            is_urgent=True,
            is_important=False
        ),
        WhatsAppMessage(
            timestamp=datetime(2024, 12, 19, 9, 1, 0),
            sender="팀장",
            content="중요한 승인 건입니다",
            is_urgent=False,
            is_important=True
        ),
        WhatsAppMessage(
            timestamp=datetime(2024, 12, 19, 9, 2, 0),
            sender="팀원",
            content="일반 메시지입니다",
            is_urgent=False,
            is_important=False
        )
    ]


def test_with_fixtures(sample_processor, sample_messages):
    """픽스처를 사용한 테스트"""
    # Given: 픽스처 메시지
    
    # When: 요약 데이터 추출
    summary_data = sample_processor.extract_summary_data(sample_messages)
    
    # Then: 올바른 분류 확인
    assert len(summary_data['urgent_messages']) == 1
    assert len(summary_data['important_messages']) == 1
    assert summary_data['confidence'] >= 0.90 