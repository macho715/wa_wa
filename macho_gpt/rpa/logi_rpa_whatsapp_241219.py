"""
MACHO-GPT v3.4-mini - RPA WhatsApp 자동화 모듈
------------------------------------------
Samsung C&T Logistics · HVDC Project
파일명: logi_rpa_whatsapp_241219.py

기능:
- WhatsApp Web 자동화 (Playwright)
- 메시지 자동 추출
- AI 요약 처리
- 데이터 저장 및 관리
- 보안 및 스텔스 기능

Mode: LATTICE (OCR 및 자동화 모드)
Confidence: ≥0.90 필요
"""

import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
try:
    from playwright_stealth import stealth_async
except ImportError:
    # Fallback for stealth functionality
    stealth_async = None
    logging.warning("playwright_stealth not available, using basic mode")

# MACHO-GPT 모듈 import
from macho_gpt.core.logi_whatsapp_241219 import WhatsAppProcessor
from macho_gpt.core.logi_ai_summarizer_241219 import LogiAISummarizer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rpa_whatsapp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatsAppRPAExtractor:
    """
    MACHO-GPT WhatsApp RPA 자동화 클래스
    
    Features:
    - 자동 메시지 추출
    - AI 요약 처리
    - 보안 스텔스 기능
    - 오류 복구 메커니즘
    """
    
    def __init__(self, mode: str = "LATTICE"):
        self.mode = mode
        self.confidence_threshold = 0.90
        self.auth_file = Path("auth.json")
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        
        # 디렉토리 생성
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # 모듈 초기화
        self.whatsapp_processor = WhatsAppProcessor(mode=mode)
        self.ai_summarizer = LogiAISummarizer()
        
        # 스텔스 설정
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ]
        
        # 기본 채팅 설정
        self.default_chat_titles = [
            "MR.CHA 전용",
            "HVDC Project",
            "Samsung C&T Team",
            "물류 업무",
            "Emergency Response"
        ]
        
        logger.info(f"✅ WhatsApp RPA 초기화 완료 - Mode: {mode}")
    
    async def extract_chat_messages(self, chat_title: str = None) -> Dict[str, Any]:
        """
        WhatsApp 채팅 메시지 자동 추출
        
        Args:
            chat_title: 추출할 채팅방 제목 (기본값: MR.CHA 전용)
            
        Returns:
            dict: 추출 결과 및 메타데이터
        """
        if not chat_title:
            chat_title = self.default_chat_titles[0]
        
        logger.info(f"🔄 채팅 메시지 추출 시작 - 대상: {chat_title}")
        
        try:
            result = await self._run_extraction(chat_title)
            
            if result['status'] == 'SUCCESS':
                # AI 요약 처리
                summary_result = await self._process_ai_summary(result['messages'])
                result.update(summary_result)
                
                # 데이터 저장
                await self._save_extracted_data(result)
                
                logger.info(f"✅ 추출 완료 - 메시지 {len(result['messages'])}개")
            else:
                logger.error(f"❌ 추출 실패 - {result.get('error', '알 수 없는 오류')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 추출 프로세스 오류: {str(e)}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode,
                'timestamp': datetime.now().isoformat(),
                'next_cmds': ['/switch_mode ZERO', '/error_recovery']
            }
    
    async def _run_extraction(self, chat_title: str) -> Dict[str, Any]:
        """실제 브라우저 자동화 실행"""
        browser = None
        try:
            # Playwright 브라우저 시작
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                )
                
                # 브라우저 컨텍스트 설정
                context = await browser.new_context(
                    storage_state=str(self.auth_file) if self.auth_file.exists() else None,
                    user_agent=random.choice(self.user_agents),
                    viewport={"width": 1280, "height": 720},
                    locale="en-US",
                    timezone_id="Asia/Seoul"
                )
                
                page = await context.new_page()
                # 스텔스 설정 적용 (fallback 지원)
                if stealth_async:
                    await stealth_async(page)
                else:
                    logger.info("스텔스 모드 비활성화 - 기본 모드로 실행")
                
                # WhatsApp Web 접속
                await page.goto("https://web.whatsapp.com/", wait_until="networkidle")
                
                # 로그인 확인 (QR 코드 스캔 필요시)
                await self._handle_login(page)
                
                # 채팅방 선택
                messages = await self._extract_messages_from_chat(page, chat_title)
                
                # 인증 정보 저장
                await self._save_auth_state(context)
                
                await browser.close()
                
                return {
                    'status': 'SUCCESS',
                    'messages': messages,
                    'chat_title': chat_title,
                    'extraction_time': datetime.now().isoformat(),
                    'message_count': len(messages),
                    'confidence': self._calculate_extraction_confidence(messages)
                }
                
        except Exception as e:
            if browser:
                await browser.close()
            raise e
    
    async def _handle_login(self, page: Page) -> None:
        """로그인 처리 (QR 코드 스캔 대기)"""
        try:
            # QR 코드 존재 확인
            qr_code = await page.locator('[data-testid="qr-code"]').count()
            if qr_code > 0:
                logger.info("🔑 QR 코드 스캔 필요 - 60초 대기")
                await page.wait_for_selector('[data-testid="chats-list"]', timeout=60000)
                logger.info("✅ 로그인 완료")
            else:
                # 이미 로그인된 상태
                await page.wait_for_selector('[data-testid="chats-list"]', timeout=30000)
                logger.info("✅ 기존 세션으로 로그인")
                
        except Exception as e:
            logger.warning(f"⚠️ 로그인 처리 중 오류: {str(e)}")
            # 로그인 실패시 수동 처리 안내
            raise Exception("WhatsApp 로그인이 필요합니다. QR 코드를 스캔하세요.")
    
    async def _extract_messages_from_chat(self, page: Page, chat_title: str) -> List[str]:
        """특정 채팅방에서 메시지 추출"""
        try:
            # 채팅방 검색 및 선택
            await page.wait_for_selector('[data-testid="chat-list-search"]', timeout=30000)
            await page.fill('[data-testid="chat-list-search"]', chat_title)
            await page.wait_for_timeout(2000)
            
            # 채팅방 클릭
            chat_selector = f'[title="{chat_title}"]'
            await page.wait_for_selector(chat_selector, timeout=30000)
            await page.click(chat_selector)
            
            # 메시지 로딩 대기
            await page.wait_for_timeout(random.randint(3000, 5000))
            
            # 페이지 스크롤 (더 많은 메시지 로드)
            await self._scroll_to_load_messages(page)
            
            # 메시지 추출
            messages = await page.locator('[data-testid="conversation-panel-messages"] .message-in, [data-testid="conversation-panel-messages"] .message-out').all_text_contents()
            
            # 빈 메시지 필터링
            filtered_messages = [msg.strip() for msg in messages if msg.strip()]
            
            logger.info(f"📄 메시지 추출 완료 - {len(filtered_messages)}개")
            return filtered_messages
            
        except Exception as e:
            logger.error(f"❌ 메시지 추출 오류: {str(e)}")
            return []
    
    async def _scroll_to_load_messages(self, page: Page) -> None:
        """메시지 로딩을 위한 스크롤"""
        try:
            # 위로 스크롤하여 더 많은 메시지 로드
            for _ in range(5):
                await page.keyboard.press('PageUp')
                await page.wait_for_timeout(random.randint(1000, 2000))
            
            # 아래로 스크롤하여 최신 메시지까지
            for _ in range(3):
                await page.keyboard.press('PageDown')
                await page.wait_for_timeout(random.randint(1000, 2000))
                
        except Exception as e:
            logger.warning(f"⚠️ 스크롤 처리 중 오류: {str(e)}")
    
    async def _save_auth_state(self, context) -> None:
        """인증 상태 저장"""
        try:
            await context.storage_state(path=str(self.auth_file))
            logger.info("💾 인증 상태 저장 완료")
        except Exception as e:
            logger.warning(f"⚠️ 인증 상태 저장 실패: {str(e)}")
    
    async def _process_ai_summary(self, messages: List[str]) -> Dict[str, Any]:
        """AI 요약 처리"""
        try:
            if not messages:
                return {
                    'summary': '추출된 메시지가 없습니다.',
                    'tasks': [],
                    'urgent': [],
                    'important': [],
                    'ai_confidence': 0.0
                }
            
            # WhatsApp 메시지 파싱
            parsed_messages = self.whatsapp_processor.parse_whatsapp_text('\n'.join(messages))
            
            # AI 요약 실행
            summary_result = self.ai_summarizer.summarize_conversation(messages)
            
            # 추가 메타데이터
            extraction_data = self.whatsapp_processor.extract_summary_data(parsed_messages)
            
            return {
                'summary': summary_result.get('summary', ''),
                'tasks': summary_result.get('tasks', []),
                'urgent': summary_result.get('urgent', []),
                'important': summary_result.get('important', []),
                'ai_confidence': summary_result.get('confidence', 0.0),
                'participants': list(extraction_data.get('participants', [])),
                'message_analysis': extraction_data
            }
            
        except Exception as e:
            logger.error(f"❌ AI 요약 처리 오류: {str(e)}")
            return {
                'summary': f'AI 요약 처리 중 오류 발생: {str(e)}',
                'tasks': [],
                'urgent': [],
                'important': [],
                'ai_confidence': 0.0
            }
    
    async def _save_extracted_data(self, result: Dict[str, Any]) -> None:
        """추출된 데이터 저장"""
        try:
            # 날짜별 데이터 파일
            date_key = datetime.now().strftime("%Y-%m-%d")
            data_file = self.data_dir / f"whatsapp_data_{date_key}.json"
            
            # 기존 데이터 로드
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            else:
                existing_data = {}
            
            # 새 데이터 추가
            timestamp = datetime.now().strftime("%H:%M:%S")
            existing_data[timestamp] = {
                'chat_title': result.get('chat_title', ''),
                'summary': result.get('summary', ''),
                'tasks': result.get('tasks', []),
                'urgent': result.get('urgent', []),
                'important': result.get('important', []),
                'message_count': result.get('message_count', 0),
                'confidence': result.get('confidence', 0.0),
                'ai_confidence': result.get('ai_confidence', 0.0),
                'participants': result.get('participants', []),
                'extraction_time': result.get('extraction_time', ''),
                'mode': self.mode,
                'raw_messages': result.get('messages', [])[:50]  # 최대 50개 메시지만 저장
            }
            
            # 파일 저장
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 데이터 저장 완료 - {data_file}")
            
        except Exception as e:
            logger.error(f"❌ 데이터 저장 오류: {str(e)}")
    
    def _calculate_extraction_confidence(self, messages: List[str]) -> float:
        """추출 신뢰도 계산"""
        if not messages:
            return 0.0
        
        confidence = 0.0
        
        # 메시지 수량 점수
        if len(messages) >= 10:
            confidence += 0.4
        elif len(messages) >= 5:
            confidence += 0.2
        elif len(messages) >= 1:
            confidence += 0.1
        
        # 메시지 품질 점수
        quality_score = sum(1 for msg in messages if len(msg.strip()) > 10) / len(messages)
        confidence += quality_score * 0.3
        
        # 타임스탬프 포함 여부
        timestamp_score = sum(1 for msg in messages if any(char.isdigit() for char in msg[:20])) / len(messages)
        confidence += timestamp_score * 0.3
        
        return min(confidence, 1.0)
    
    def get_status(self) -> Dict[str, Any]:
        """RPA 상태 정보 반환"""
        return {
            'mode': self.mode,
            'confidence_threshold': self.confidence_threshold,
            'auth_file_exists': self.auth_file.exists(),
            'data_dir': str(self.data_dir),
            'logs_dir': str(self.logs_dir),
            'default_chats': self.default_chat_titles,
            'version': '3.4-mini',
            'status': 'ready'
        }

# 메인 실행 함수
async def main():
    """
    메인 실행 함수
    
    사용법:
    - python -m macho_gpt.rpa.logi_rpa_whatsapp_241219
    - 또는 직접 실행: python logi_rpa_whatsapp_241219.py
    """
    logger.info("🚀 MACHO-GPT v3.4-mini RPA 시작")
    
    # RPA 인스턴스 생성
    rpa = WhatsAppRPAExtractor(mode="LATTICE")
    
    # 상태 확인
    status = rpa.get_status()
    logger.info(f"📊 RPA 상태: {status}")
    
    # 채팅 메시지 추출
    result = await rpa.extract_chat_messages("MR.CHA 전용")
    
    # 결과 출력
    if result['status'] == 'SUCCESS':
        logger.info("✅ 추출 성공!")
        logger.info(f"📊 요약: {result.get('summary', '')}")
        logger.info(f"📋 태스크: {len(result.get('tasks', []))}개")
        logger.info(f"🚨 긴급: {len(result.get('urgent', []))}개")
        logger.info(f"⭐ 중요: {len(result.get('important', []))}개")
        
        # 추천 명령어
        print("\n🔧 추천 명령어:")
        print("- /logi_dashboard [대시보드 확인]")
        print("- /ai_summary [AI 요약 재실행]")
        print("- /export_data [데이터 내보내기]")
        
    else:
        logger.error("❌ 추출 실패")
        logger.error(f"오류: {result.get('error', '알 수 없는 오류')}")
        
        # 오류 해결 명령어
        print("\n🔧 오류 해결 명령어:")
        print("- /switch_mode ZERO [안전 모드 전환]")
        print("- /setup_auth [인증 재설정]")
        print("- /check_browser [브라우저 확인]")

if __name__ == "__main__":
    asyncio.run(main()) 