#!/usr/bin/env python3
"""
Browser Arguments Management Tests
TDD Phase 8: Browser Arguments Management Tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Set, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whatsapp_media_ocr_extractor import WhatsAppMediaOCRExtractor


class TestBrowserArgumentsManagement:
    """브라우저 인수 관리 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.extractor = WhatsAppMediaOCRExtractor("Test Chat")
    
    def test_should_prevent_duplicate_browser_arguments(self):
        """브라우저 인수 중복 방지 테스트"""
        # Given: 중복된 인수들이 포함된 리스트
        duplicate_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage", 
            "--no-sandbox",  # 중복
            "--disable-dev-shm-usage",  # 중복
            "--disable-extensions",
            "--no-sandbox"  # 또 다른 중복
        ]
        
        # When: 중복 제거 메서드 호출
        deduplicated_args = self.extractor._deduplicate_browser_arguments(duplicate_args)
        
        # Then: 중복이 제거되어야 함
        assert len(deduplicated_args) == 3
        assert "--no-sandbox" in deduplicated_args
        assert "--disable-dev-shm-usage" in deduplicated_args
        assert "--disable-extensions" in deduplicated_args
        assert deduplicated_args.count("--no-sandbox") == 1
        assert deduplicated_args.count("--disable-dev-shm-usage") == 1
    
    def test_should_use_set_for_argument_deduplication(self):
        """Set 기반 인수 중복 제거 테스트"""
        # Given: 다양한 인수 조합
        args_list_1 = ["--no-sandbox", "--disable-dev-shm-usage"]
        args_list_2 = ["--disable-dev-shm-usage", "--disable-extensions"]
        
        # When: Set 기반 중복 제거
        combined_args = self.extractor._combine_browser_arguments(args_list_1, args_list_2)
        
        # Then: 중복이 제거되고 모든 고유 인수가 포함되어야 함
        assert len(combined_args) == 3
        assert "--no-sandbox" in combined_args
        assert "--disable-dev-shm-usage" in combined_args
        assert "--disable-extensions" in combined_args
    
    def test_should_log_browser_arguments_for_debugging(self):
        """브라우저 인수 로깅 테스트"""
        # Given: 브라우저 인수 목록
        test_args = ["--no-sandbox", "--disable-dev-shm-usage"]
        
        # When: 로깅 메서드 호출
        with patch('builtins.print') as mock_print:
            self.extractor._log_browser_arguments(test_args, "test_context")
            
        # Then: 로그가 출력되어야 함
        mock_print.assert_called()
        # 로그 메시지에 인수가 포함되어야 함
        call_args = [call[0][0] for call in mock_print.call_args_list]
        assert any("--no-sandbox" in str(arg) for arg in call_args)
    
    def test_should_handle_ignore_default_args_option(self):
        """ignore_default_args 옵션 처리 테스트"""
        # Given: 기본 인수 무시 설정
        ignore_defaults = ["--disable-extensions", "--disable-dev-shm-usage"]
        
        # When: ignore_default_args 설정
        config = self.extractor._get_browser_launch_config(
            ignore_default_args=ignore_defaults
        )
        
        # Then: ignore_default_args가 설정되어야 함
        assert "ignore_default_args" in config
        assert config["ignore_default_args"] == ignore_defaults
    
    def test_should_validate_browser_argument_format(self):
        """브라우저 인수 형식 검증 테스트"""
        # Given: 잘못된 형식의 인수들
        invalid_args = [
            "no-sandbox",  # -- 누락
            "--",  # 값 누락
            "--disable-dev-shm-usage=invalid",  # 잘못된 값
            "valid-arg"  # -- 누락
        ]
        
        # When: 인수 검증
        valid_args = self.extractor._validate_browser_arguments(invalid_args)
        
        # Then: 유효한 인수만 남아야 함
        assert len(valid_args) == 0  # 모든 인수가 잘못됨
    
    def test_should_handle_empty_argument_list(self):
        """빈 인수 리스트 처리 테스트"""
        # Given: 빈 인수 리스트
        empty_args = []
        
        # When: 중복 제거 처리
        result = self.extractor._deduplicate_browser_arguments(empty_args)
        
        # Then: 빈 리스트가 반환되어야 함
        assert result == []
    
    def test_should_preserve_argument_order(self):
        """인수 순서 보존 테스트"""
        # Given: 순서가 중요한 인수들
        ordered_args = [
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-extensions"
        ]
        
        # When: 중복 제거 (중복 없음)
        result = self.extractor._deduplicate_browser_arguments(ordered_args)
        
        # Then: 순서가 보존되어야 함
        assert result == ordered_args
    
    def test_should_handle_mixed_case_arguments(self):
        """대소문자 혼합 인수 처리 테스트"""
        # Given: 대소문자가 다른 동일한 인수들
        mixed_case_args = [
            "--no-sandbox",
            "--NO-SANDBOX",
            "--No-Sandbox"
        ]
        
        # When: 중복 제거
        result = self.extractor._deduplicate_browser_arguments(mixed_case_args)
        
        # Then: 대소문자가 다른 인수는 다른 것으로 처리되어야 함
        assert len(result) == 3
        assert "--no-sandbox" in result
        assert "--NO-SANDBOX" in result
        assert "--No-Sandbox" in result


class TestSessionManagement:
    """세션 관리 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.extractor = WhatsAppMediaOCRExtractor("Test Chat")
    
    def test_should_cleanup_session_directory_on_failure(self):
        """실패 시 세션 디렉토리 정리 테스트"""
        # Given: 세션 디렉토리 존재
        session_dir = self.extractor.user_data_dir
        
        # When: 실패 시 정리 메서드 호출
        with patch('shutil.rmtree') as mock_rmtree:
            self.extractor._cleanup_session_directory()
            
        # Then: rmtree가 호출되어야 함
        mock_rmtree.assert_called_once_with(session_dir, ignore_errors=True)
    
    def test_should_handle_context_close_exceptions(self):
        """컨텍스트 종료 예외 처리 테스트"""
        # Given: 컨텍스트 종료 시 예외 발생
        mock_context = AsyncMock()
        mock_context.close.side_effect = Exception("Context close failed")
        
        # When: 안전한 컨텍스트 종료
        with patch('builtins.print') as mock_print:
            self.extractor._safe_close_context(mock_context)
            
        # Then: 예외가 처리되어야 함
        mock_print.assert_called()
        # 에러 메시지가 로그되어야 함
        call_args = [call[0][0] for call in mock_print.call_args_list]
        assert any("Context close failed" in str(arg) for arg in call_args)
    
    def test_should_monitor_browser_process_during_login(self):
        """로그인 중 브라우저 프로세스 모니터링 테스트"""
        # Given: 브라우저 페이지와 모니터링 설정
        mock_page = Mock()
        mock_page.is_closed.return_value = False
        
        # When: 브라우저 상태 모니터링
        with patch('asyncio.sleep') as mock_sleep:
            result = self.extractor._monitor_browser_status(mock_page, timeout=5)
            
        # Then: 모니터링이 정상적으로 수행되어야 함
        assert result is True
        mock_sleep.assert_called()
    
    def test_should_force_cleanup_on_critical_errors(self):
        """치명적 오류 시 강제 정리 테스트"""
        # Given: 치명적 오류 상황
        critical_error = RuntimeError("Critical browser failure")
        
        # When: 강제 정리 수행
        with patch.object(self.extractor, '_cleanup_session_directory') as mock_cleanup:
            with patch('builtins.print') as mock_print:
                self.extractor._handle_critical_error(critical_error)
                
        # Then: 강제 정리가 수행되어야 함
        mock_cleanup.assert_called_once()
        mock_print.assert_called()


class TestOperationalStability:
    """운영 안정성 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.extractor = WhatsAppMediaOCRExtractor("Test Chat")
    
    def test_should_log_playwright_version_and_chromium_info(self):
        """Playwright 버전 및 Chromium 정보 로깅 테스트"""
        # When: 버전 정보 로깅
        with patch('builtins.print') as mock_print:
            self.extractor._log_system_info()
            
        # Then: 버전 정보가 로그되어야 함
        mock_print.assert_called()
        # Playwright 버전 정보가 포함되어야 함
        call_args = [call[0][0] for call in mock_print.call_args_list]
        assert any("Playwright" in str(arg) for arg in call_args)
    
    def test_should_handle_headless_headful_mode_switching(self):
        """Headless/Headful 모드 전환 테스트"""
        # Given: 모드 전환 설정
        headless_config = self.extractor._get_browser_launch_config(headless=True)
        headful_config = self.extractor._get_browser_launch_config(headless=False)
        
        # Then: 모드가 올바르게 설정되어야 함
        assert headless_config["headless"] is True
        assert headful_config["headless"] is False
    
    def test_should_implement_polling_for_browser_status(self):
        """브라우저 상태 폴링 테스트"""
        # Given: 브라우저 상태 폴링 설정
        mock_page = Mock()
        mock_page.is_closed.return_value = False
        
        # When: 폴링 수행
        with patch('asyncio.sleep') as mock_sleep:
            result = self.extractor._poll_browser_status(mock_page, interval=1, max_attempts=3)
            
        # Then: 폴링이 정상적으로 수행되어야 함
        assert result is True
        assert mock_sleep.call_count == 2  # 3번 시도, 2번 대기
    
    def test_should_generate_operational_debug_logs(self):
        """운영 디버그 로그 생성 테스트"""
        # Given: 디버그 정보
        debug_info = {
            "user_data_dir": "/test/path",
            "browser_args": ["--no-sandbox"],
            "mode": "headless"
        }
        
        # When: 디버그 로그 생성
        with patch('builtins.print') as mock_print:
            self.extractor._log_debug_info(debug_info)
            
        # Then: 디버그 정보가 로그되어야 함
        mock_print.assert_called()
        # 디버그 정보가 포함되어야 함
        call_args = [call[0][0] for call in mock_print.call_args_list]
        assert any("user_data_dir" in str(arg) for arg in call_args)
        assert any("--no-sandbox" in str(arg) for arg in call_args)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 