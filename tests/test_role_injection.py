"""
MACHO-GPT v3.4-mini Role Configuration 테스트
Samsung C&T Logistics · HVDC Project

테스트 항목:
1. Role Description 기본 기능
2. Enhanced System Prompt 생성
3. System Message 포맷
4. 환경별 설정
5. AI Summarizer 통합
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from macho_gpt.core.logi_ai_summarizer_241219 import LogiAISummarizer
from macho_gpt.core.role_config import (DEFAULT_ROLE_DESCRIPTION,
                                        ENVIRONMENT_ROLES, RoleConfigManager,
                                        create_system_message,
                                        get_enhanced_system_prompt,
                                        get_role_description, get_role_status)


class TestRoleConfig:
    """Role Configuration 기본 기능 테스트"""

    def test_role_description_contains_key_terms(self):
        """역할 설명에 핵심 키워드가 포함되어 있는지 테스트"""
        role_desc = get_role_description()

        # 필수 키워드 확인 (대소문자 구분 없음)
        role_desc_lower = role_desc.lower()
        assert "samsung c&t" in role_desc_lower
        assert "hvdc" in role_desc_lower
        assert "logistics" in role_desc_lower

        # 환경별로 다른 역할 설명을 사용할 수 있으므로 더 유연하게 체크
        # 기본 역할 설명이 로드되는 경우에만 추가 키워드 확인
        if "adnoc" in role_desc_lower:
            assert "dsv" in role_desc_lower

        # 프로젝트 관련 정보는 항상 있어야 함
        assert len(role_desc) > 10  # 최소 길이 확인

    def test_enhanced_system_prompt_structure(self):
        """향상된 시스템 프롬프트 구조 테스트"""
        base_prompt = "Test prompt for WhatsApp analysis"
        mode = "LATTICE"

        prompt = get_enhanced_system_prompt(base_prompt, mode)

        # 기본 구조 확인
        assert "Samsung C&T" in prompt
        assert "MACHO-GPT v3.4-mini" in prompt
        assert "Test prompt for WhatsApp analysis" in prompt
        assert "LATTICE" in prompt

        # 모드별 지침 확인
        assert "OCR" in prompt or "문서 분석" in prompt

        # 가이드라인 확인
        assert "신뢰도 ≥0.90" in prompt
        assert "추천 명령어" in prompt

    def test_system_message_format(self):
        """시스템 메시지 형식 테스트"""
        content = "Analyze WhatsApp messages"
        mode = "PRIME"

        message = create_system_message(content, mode)

        # 형식 검증
        assert isinstance(message, dict)
        assert message["role"] == "system"
        assert "content" in message

        # 내용 검증
        assert "Samsung C&T" in message["content"]
        assert "Analyze WhatsApp messages" in message["content"]
        assert "PRIME" in message["content"]

    def test_role_status_information(self):
        """역할 상태 정보 테스트"""
        status = get_role_status()

        # 필수 필드 확인
        assert "environment" in status
        assert "role_source" in status
        assert "role_length" in status
        assert "version" in status
        assert "status" in status

        # 값 검증
        assert status["version"] == "3.4-mini"
        assert status["status"] == "ready"
        assert isinstance(status["role_length"], int)
        assert status["role_length"] > 0


class TestRoleConfigManager:
    """RoleConfigManager 클래스 테스트"""

    def test_manager_initialization(self):
        """역할 관리자 초기화 테스트"""
        manager = RoleConfigManager("development")

        assert manager.environment == "development"
        assert len(manager.role_description) > 0

    def test_environment_specific_roles(self):
        """환경별 역할 설정 테스트"""
        # 개발 환경
        dev_manager = RoleConfigManager("development")
        assert "[DEV]" in dev_manager.get_role_description()

        # 프로덕션 환경
        prod_manager = RoleConfigManager("production")
        prod_role = prod_manager.get_role_description()
        assert "Samsung C&T" in prod_role
        assert "HVDC" in prod_role

    @patch.dict(os.environ, {"MACHO_GPT_ROLE_DESCRIPTION": "Custom Role Description"})
    def test_environment_variable_override(self):
        """환경변수 우선순위 테스트"""
        manager = RoleConfigManager()
        role_desc = manager.get_role_description()

        assert role_desc == "Custom Role Description"

    def test_role_update(self):
        """역할 업데이트 테스트"""
        manager = RoleConfigManager()
        original_role = manager.get_role_description()

        new_role = "Updated Role Description"
        success = manager.update_role(new_role)

        assert success is True
        assert manager.get_role_description() == new_role
        assert manager.get_role_description() != original_role

    def test_status_information(self):
        """상태 정보 테스트"""
        manager = RoleConfigManager("staging")
        status = manager.get_status()

        assert status["environment"] == "staging"
        assert status["version"] == "3.4-mini"
        assert "available_modes" in status


class TestAISummarizerIntegration:
    """AI Summarizer와 Role Configuration 통합 테스트"""

    def test_summarizer_initialization_with_role(self):
        """Role Configuration이 포함된 AI Summarizer 초기화 테스트"""
        summarizer = LogiAISummarizer(mode="RHYTHM")

        assert summarizer.mode == "RHYTHM"
        assert summarizer.confidence_threshold == 0.90

    def test_summarizer_status_includes_role_config(self):
        """AI Summarizer 상태에 Role Configuration 정보 포함 테스트"""
        summarizer = LogiAISummarizer(mode="COST-GUARD")
        status = summarizer.get_status()

        assert "mode" in status
        assert "role_config" in status
        assert status["mode"] == "COST-GUARD"
        assert status["version"] == "3.4-mini"

        # Role config 정보 검증
        role_config = status["role_config"]
        assert "environment" in role_config
        assert "version" in role_config

    def test_task_prompt_content(self):
        """태스크 프롬프트 내용 테스트"""
        summarizer = LogiAISummarizer()
        task_prompt = summarizer._get_task_prompt()

        # 기본 기능 확인
        assert "WhatsApp 대화를 분석" in task_prompt
        assert "핵심 요약" in task_prompt
        assert "태스크 목록" in task_prompt
        assert "긴급 사항" in task_prompt
        assert "중요 사항" in task_prompt

        # HVDC 프로젝트 관련 내용 확인
        assert "HVDC 프로젝트" in task_prompt
        assert "ADNOC·DSV" in task_prompt
        assert "계약/통관" in task_prompt

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test"})
    @patch("openai.chat.completions.create")
    def test_summarizer_uses_role_config(self, mock_openai):
        """AI Summarizer가 Role Configuration을 사용하는지 테스트"""
        # Mock OpenAI 응답
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        **요약:**
        테스트 요약 내용
        
        **태스크:**
        - 테스트 태스크 1
        - 테스트 태스크 2
        
        **긴급:**
        - 긴급 사항 없음
        
        **중요:**
        - 중요 사항 없음
        """
        mock_openai.return_value = mock_response

        # AI Summarizer 실행
        summarizer = LogiAISummarizer(mode="ORACLE")
        result = summarizer.summarize_conversation(["테스트 메시지"])

        # OpenAI 호출 확인
        assert mock_openai.called
        call_args = mock_openai.call_args

        # 시스템 메시지 검증
        messages = call_args[1]["messages"]
        system_message = messages[0]

        assert system_message["role"] == "system"
        assert "Samsung C&T" in system_message["content"]
        assert "ORACLE" in system_message["content"]
        assert "MACHO-GPT v3.4-mini" in system_message["content"]

        # 결과 검증
        assert result["summary"] == "테스트 요약 내용"
        assert len(result["tasks"]) == 2
        assert "confidence" in result
        assert "timestamp" in result


class TestEnvironmentConfiguration:
    """환경별 설정 테스트"""

    def test_all_environments_have_configurations(self):
        """모든 환경에 대한 설정이 있는지 테스트"""
        expected_environments = ["development", "staging", "production", "demo"]

        for env in expected_environments:
            assert env in ENVIRONMENT_ROLES
            assert len(ENVIRONMENT_ROLES[env]) > 0

    def test_default_role_description_quality(self):
        """기본 역할 설명 품질 테스트"""
        # 길이 검증
        assert len(DEFAULT_ROLE_DESCRIPTION) > 100

        # 필수 정보 포함 검증
        required_terms = [
            "Samsung C&T",
            "HVDC",
            "Logistics",
            "ADNOC",
            "DSV",
            "Import/Export",
            "customs",
            "contract",
            "KPI",
            "confidence",
            "productivity",
        ]

        for term in required_terms:
            assert term.lower() in DEFAULT_ROLE_DESCRIPTION.lower()

    @patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_environment_auto_detection(self):
        """환경 자동 감지 테스트"""
        from macho_gpt.core.role_config import get_environment

        env = get_environment()
        assert env == "development"

    @patch.dict(os.environ, {"ENV": "staging"})
    def test_env_variable_detection(self):
        """ENV 변수 감지 테스트"""
        from macho_gpt.core.role_config import get_environment

        env = get_environment()
        assert env == "staging"


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v", "--tb=short"]) 