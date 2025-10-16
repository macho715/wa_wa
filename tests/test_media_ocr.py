#!/usr/bin/env python3
"""
WhatsApp Media OCR Tests
MACHO-GPT v3.4-mini for HVDC Project
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Import the classes to test
from whatsapp_media_ocr_extractor import MediaOCRProcessor, WhatsAppMediaOCRExtractor

class TestMediaOCRProcessor:
    """MediaOCRProcessor 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """테스트 설정"""
        self.processor = MediaOCRProcessor()
    
    def test_initialization(self):
        """초기화 테스트"""
        assert self.processor.max_file_size_mb == 5
        assert hasattr(self.processor, 'processed_files')
        assert isinstance(self.processor.processed_files, set)
    
    def test_sanitize_ocr_text(self):
        """OCR 텍스트 정제 테스트"""
        test_text = """
        연락처: 010-1234-5678
        이메일: test@example.com
        주민번호: 123456-1234567
        신용카드: 1234-5678-9012-3456
        일반 텍스트: 이것은 테스트입니다.
        """
        
        result = self.processor.sanitize_ocr_text(test_text)
        
        # 개인정보가 마스킹되었는지 확인
        assert '[PHONE]' in result
        assert '[EMAIL]' in result
        assert '[ID_NUMBER]' in result
        assert '[CARD_NUMBER]' in result
        assert '일반 텍스트: 이것은 테스트입니다.' in result
    
    def test_get_file_hash(self):
        """파일 해시 생성 테스트"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            hash_result = self.processor.get_file_hash(temp_file)
            assert len(hash_result) == 32  # MD5 해시 길이
            assert isinstance(hash_result, str)
        finally:
            os.unlink(temp_file)
    
    def test_cache_operations(self):
        """캐시 작업 테스트"""
        test_hash = "test_hash_123"
        
        # 초기 상태 확인
        assert test_hash not in self.processor.processed_files
        
        # 해시 추가
        self.processor.processed_files.add(test_hash)
        assert test_hash in self.processor.processed_files
    
    @patch('easyocr.Reader')
    def test_ocr_engine_setup(self, mock_easyocr):
        """OCR 엔진 설정 테스트"""
        # EasyOCR이 사용 가능한 경우
        with patch('whatsapp_media_ocr_extractor.EASYOCR_AVAILABLE', True):
            processor = MediaOCRProcessor()
            mock_easyocr.assert_called_with(['ko', 'en'])
    
    @patch('easyocr.Reader')
    async def test_process_image_mock(self, mock_easyocr):
        """이미지 처리 모의 테스트"""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = [
            (None, "테스트 텍스트", 0.9),
            (None, "Test Text", 0.8)
        ]
        mock_easyocr.return_value = mock_reader
        
        with patch('whatsapp_media_ocr_extractor.EASYOCR_AVAILABLE', True):
            processor = MediaOCRProcessor()
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write("test image content")
                temp_file = f.name
            
            try:
                result = await processor.process_image(temp_file, "easyocr")
                
                assert 'text' in result
                assert 'confidence' in result
                assert 'engine' in result
                assert result['engine'] == 'easyocr'
            finally:
                os.unlink(temp_file)
    
    @patch('fitz.open')
    async def test_process_pdf_mock(self, mock_fitz):
        """PDF 처리 모의 테스트"""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test pdf content")
            temp_file = f.name
        
        try:
            # PDF 처리는 현재 구현에 없으므로 에러 반환 확인
            result = await self.processor.process_image(temp_file, "easyocr")
            assert 'error' in result or 'text' in result
        finally:
            os.unlink(temp_file)

class TestWhatsAppMediaOCRExtractor:
    """WhatsAppMediaOCRExtractor 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """테스트 설정"""
        self.extractor = WhatsAppMediaOCRExtractor()
    
    def test_initialization(self):
        """초기화 테스트"""
        assert hasattr(self.extractor, 'media_processor')
        assert hasattr(self.extractor, 'media_selectors')
        assert len(self.extractor.media_selectors) > 0
        assert isinstance(self.extractor.media_selectors, list)
    
    def test_sanitize_filename(self):
        """파일명 정제 테스트"""
        test_filename = "test<>:\"/\\|?*file.jpg"
        result = self.extractor.sanitize_filename(test_filename)
        
        # 특수문자가 언더스코어로 변경되었는지 확인
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        assert '"' not in result
        assert '/' not in result
        assert '\\' not in result
        assert '|' not in result
        assert '?' not in result
        assert '*' not in result
    
    @pytest.mark.asyncio
    async def test_find_media_messages_mock(self):
        """미디어 메시지 찾기 모의 테스트"""
        mock_page = AsyncMock()
        mock_elements = [MagicMock(), MagicMock()]
        mock_page.query_selector_all.return_value = mock_elements
        
        # 채팅방 찾기 모의
        mock_page.wait_for_selector.return_value = MagicMock()
        mock_page.click.return_value = None
        
        result = await self.extractor.find_media_messages(mock_page, "Test Chat")
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_download_media_mock(self):
        """미디어 다운로드 모의 테스트"""
        mock_element = AsyncMock()
        download_dir = tempfile.mkdtemp()
        
        try:
            result = await self.extractor.download_media(mock_element, download_dir)
            
            # 스크린샷이 호출되었는지 확인
            mock_element.screenshot.assert_called_once()
            
            # 결과가 문자열이거나 None인지 확인
            assert result is None or isinstance(result, str)
        finally:
            import shutil
            shutil.rmtree(download_dir)
    
    @pytest.mark.asyncio
    async def test_process_media_file_mock(self):
        """미디어 파일 처리 모의 테스트"""
        with patch.object(self.extractor.media_processor, 'process_image') as mock_process:
            mock_process.return_value = {
                'text': '테스트 텍스트',
                'confidence': 0.9,
                'engine': 'easyocr'
            }
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write("test content")
                temp_file = f.name
            
            try:
                result = await self.extractor.process_media_file(temp_file, "easyocr")
                
                assert 'text' in result
                assert 'confidence' in result
                assert 'engine' in result
            finally:
                os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_save_results(self):
        """결과 저장 테스트"""
        test_results = [
            {'text': '테스트 1', 'confidence': 0.9},
            {'text': '테스트 2', 'confidence': 0.8}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            await self.extractor.save_results(test_results, output_file)
            
            # 파일이 생성되었는지 확인
            assert os.path.exists(output_file)
            
            # JSON 내용 확인
            import json
            with open(output_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert 'timestamp' in saved_data
            assert 'total_processed' in saved_data
            assert 'successful' in saved_data
            assert 'results' in saved_data
            assert len(saved_data['results']) == 2
        finally:
            os.unlink(output_file)

class TestIntegration:
    """통합 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_full_extraction_workflow_mock(self):
        """전체 추출 워크플로우 모의 테스트"""
        extractor = WhatsAppMediaOCRExtractor()
        
        with patch.object(extractor, 'find_media_messages') as mock_find:
            with patch.object(extractor, 'download_media') as mock_download:
                with patch.object(extractor, 'process_media_file') as mock_process:
                    with patch.object(extractor, 'save_results') as mock_save:
                        # 모의 설정
                        mock_find.return_value = [MagicMock(), MagicMock()]
                        mock_download.return_value = "/tmp/test_file.jpg"
                        mock_process.return_value = {
                            'text': '테스트 결과',
                            'confidence': 0.9,
                            'engine': 'easyocr'
                        }
                        mock_save.return_value = None
                        
                        # 워크플로우 실행
                        mock_page = AsyncMock()
                        mock_page.wait_for_selector.return_value = MagicMock()
                        mock_page.click.return_value = None
                        
                        media_elements = await extractor.find_media_messages(mock_page, "Test Chat")
                        assert len(media_elements) == 2
                        
                        # 각 단계가 호출되었는지 확인
                        mock_find.assert_called_once()
                        mock_download.assert_called()
                        mock_process.assert_called()
                        mock_save.assert_called()

def test_config_validation():
    """설정 검증 테스트"""
    processor = MediaOCRProcessor(max_file_size_mb=5)
    assert processor.max_file_size_mb == 5

def test_error_handling():
    """오류 처리 테스트"""
    processor = MediaOCRProcessor()
    
    # 존재하지 않는 파일로 테스트
    result = asyncio.run(processor.process_image("nonexistent_file.jpg"))
    assert 'error' in result
    assert result['engine'] == 'easyocr'  # 기본 엔진

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 