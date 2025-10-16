#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini WhatsApp RPA 수동 추출 스크립트
-----------------------------------------------
Samsung C&T Logistics · HVDC Project

기능:
- 브라우저 창이 보이는 모드로 WhatsApp Web 자동화
- QR 코드 스캔을 위한 수동 개입 가능
- 실시간 진행 상황 모니터링
- 안전한 종료 처리

실행 방법:
python whatsapp_rpa_manual_extract.py
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# MACHO-GPT 모듈 import
try:
    from macho_gpt.rpa.logi_rpa_whatsapp_241219 import WhatsAppRPAExtractor
    from macho_gpt.core.role_config import RoleConfigManager
except ImportError as e:
    print(f"❌ MACHO-GPT 모듈 import 오류: {e}")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/whatsapp_rpa_manual.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatsAppRPAManualExtractor:
    """WhatsApp RPA 수동 추출 관리자"""
    
    def __init__(self):
        self.role_config = RoleConfigManager()
        self.extractor = WhatsAppRPAExtractor(mode="LATTICE")
        
        print("✅ WhatsApp RPA 수동 추출기 초기화 완료")
    
    async def extract_with_manual_intervention(self, chat_title: str = "MR.CHA 전용"):
        """수동 개입이 가능한 추출 프로세스"""
        print(f"\n🔄 WhatsApp RPA 수동 추출 시작")
        print(f"📱 대상 채팅방: {chat_title}")
        print("=" * 60)
        
        try:
            # Playwright 브라우저를 headless=False로 실행
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                print("🌐 브라우저 시작 중...")
                browser = await p.chromium.launch(
                    headless=False,  # 브라우저 창이 보이도록 설정
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor"
                    ]
                )
                
                # 브라우저 컨텍스트 생성
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                    locale="en-US",
                    timezone_id="Asia/Seoul"
                )
                
                page = await context.new_page()
                
                # WhatsApp Web 접속
                print("📱 WhatsApp Web 접속 중...")
                await page.goto("https://web.whatsapp.com/", wait_until="networkidle")
                
                # QR 코드 스캔 안내
                print("\n📱 QR 코드 스캔 안내:")
                print("1. 브라우저 창에서 WhatsApp Web이 열렸습니다")
                print("2. 휴대폰 WhatsApp 앱을 열고 QR 코드를 스캔하세요")
                print("3. 로그인이 완료되면 자동으로 진행됩니다")
                print("4. 중단하려면 Ctrl+C를 누르세요")
                
                # 로그인 완료 대기
                try:
                    await page.wait_for_selector('[data-testid="chats-list"]', timeout=120000)  # 2분 대기
                    print("✅ 로그인 완료!")
                except Exception as e:
                    print("❌ 로그인 시간 초과 또는 오류 발생")
                    print("💡 다시 시도하거나 수동으로 로그인 후 Enter를 누르세요")
                    input("로그인 완료 후 Enter를 누르세요...")
                
                # 채팅방 검색 및 선택
                print(f"\n🔍 채팅방 검색 중: {chat_title}")
                await page.wait_for_selector('[data-testid="chat-list-search"]', timeout=30000)
                await page.fill('[data-testid="chat-list-search"]', chat_title)
                await page.wait_for_timeout(2000)
                
                # 채팅방 클릭
                chat_selector = f'[title="{chat_title}"]'
                try:
                    await page.wait_for_selector(chat_selector, timeout=30000)
                    await page.click(chat_selector)
                    print(f"✅ 채팅방 선택 완료: {chat_title}")
                except Exception as e:
                    print(f"❌ 채팅방을 찾을 수 없습니다: {chat_title}")
                    print("💡 사용 가능한 채팅방 목록:")
                    
                    # 사용 가능한 채팅방 목록 표시
                    chat_elements = await page.locator('[data-testid="cell-title-text"]').all_text_contents()
                    for i, chat in enumerate(chat_elements[:10], 1):
                        print(f"   {i}. {chat}")
                    
                    return {
                        'status': 'ERROR',
                        'error': f'Chat room not found: {chat_title}',
                        'available_chats': chat_elements[:10]
                    }
                
                # 메시지 로딩 대기
                print("📄 메시지 로딩 중...")
                await page.wait_for_timeout(3000)
                
                # 메시지 추출
                print("📄 메시지 추출 중...")
                messages = await page.locator('[data-testid="conversation-panel-messages"] .message-in, [data-testid="conversation-panel-messages"] .message-out').all_text_contents()
                
                # 빈 메시지 필터링
                filtered_messages = [msg.strip() for msg in messages if msg.strip()]
                
                print(f"✅ 메시지 추출 완료: {len(filtered_messages)}개")
                
                # 결과 저장
                result = {
                    'status': 'SUCCESS',
                    'messages': filtered_messages,
                    'chat_title': chat_title,
                    'extraction_time': datetime.now().isoformat(),
                    'message_count': len(filtered_messages),
                    'confidence': len(filtered_messages) / 100.0  # 간단한 신뢰도 계산
                }
                
                # 브라우저 종료 전 잠시 대기 (결과 확인용)
                print("\n📊 추출 결과:")
                print(f"   - 채팅방: {result['chat_title']}")
                print(f"   - 메시지 수: {result['message_count']}개")
                print(f"   - 신뢰도: {result['confidence']:.2f}")
                print(f"   - 추출 시간: {result['extraction_time']}")
                
                print("\n⏳ 10초 후 브라우저가 자동으로 종료됩니다...")
                await asyncio.sleep(10)
                
                await browser.close()
                
                return result
                
        except KeyboardInterrupt:
            print("\n⚠️ 사용자에 의해 중단되었습니다.")
            return {
                'status': 'INTERRUPTED',
                'error': 'User interrupted',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ 추출 중 오류 발생: {str(e)}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

async def main():
    """메인 실행 함수"""
    print("🤖 MACHO-GPT v3.4-mini WhatsApp RPA 수동 추출")
    print("=" * 60)
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 모드: LATTICE (OCR 및 자동화)")
    print(f"🏢 프로젝트: Samsung C&T Logistics · HVDC")
    print("=" * 60)
    
    extractor = WhatsAppRPAManualExtractor()
    
    try:
        # 기본 채팅방 추출
        result = await extractor.extract_with_manual_intervention("MR.CHA 전용")
        
        if result['status'] == 'SUCCESS':
            print("\n🎉 WhatsApp RPA 수동 추출 성공!")
            
            # 결과 파일 저장
            output_file = f"data/whatsapp_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 결과가 저장되었습니다: {output_file}")
            
        elif result['status'] == 'ERROR':
            print(f"\n❌ 추출 실패: {result.get('error', 'Unknown error')}")
            if 'available_chats' in result:
                print("💡 사용 가능한 채팅방 목록:")
                for i, chat in enumerate(result['available_chats'], 1):
                    print(f"   {i}. {chat}")
                    
        elif result['status'] == 'INTERRUPTED':
            print("\n⚠️ 사용자에 의해 중단되었습니다.")
    
    except Exception as e:
        logger.error(f"❌ 실행 중 오류 발생: {str(e)}")
        print(f"❌ 오류 발생: {str(e)}")
    
    print("\n🎉 MACHO-GPT WhatsApp RPA 수동 추출 완료")

if __name__ == "__main__":
    asyncio.run(main()) 