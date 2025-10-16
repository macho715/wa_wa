#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini WhatsApp RPA 대안 접근법
------------------------------------------
Samsung C&T Logistics · HVDC Project

DOM 변경에 대응한 대안적 접근 방법:
1. 키보드 단축키 기반 접근
2. 좌표 기반 클릭
3. 이미지 인식 기반 접근
4. 수동 모드 지원
"""

import asyncio
import time
import json
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError

class WhatsAppRPAAlternative:
    """WhatsApp RPA 대안 접근법"""
    
    def __init__(self):
        self.hvdc_chats = [
            "HVDC 물류팀",
            "[HVDC] ⚡ Project lightning ⚡",
            "Abu Dhabi Logistics",
            "Jopetwil 71 Group",
            "AGI- Wall panel-GCC Storage"
        ]
    
    async def extract_with_keyboard_shortcuts(self):
        """키보드 단축키 기반 추출"""
        print("⌨️ 키보드 단축키 기반 WhatsApp 추출")
        print("=" * 50)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # WhatsApp Web 접속
                await page.goto("https://web.whatsapp.com/")
                print("🌐 WhatsApp Web 접속 완료")
                
                # 로그인 대기
                await page.wait_for_selector("#side", timeout=120000)
                print("✅ 로그인 완료!")
                
                results = []
                for chat_title in self.hvdc_chats:
                    print(f"\n📱 채팅방 처리: {chat_title}")
                    
                    try:
                        # 방법 1: Ctrl+F로 검색
                        await page.keyboard.press("Control+f")
                        await page.wait_for_timeout(1000)
                        
                        # 검색어 입력
                        await page.keyboard.type(chat_title)
                        await page.wait_for_timeout(2000)
                        
                        # Enter로 첫 번째 결과 선택
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(3000)
                        
                        # 메시지 추출
                        messages = await self.extract_messages_alternative(page)
                        
                        result = {
                            'status': 'SUCCESS',
                            'chat_title': chat_title,
                            'messages': messages,
                            'method': 'keyboard_shortcuts',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        print(f"✅ 추출 성공: {len(messages)}개 메시지")
                        
                    except Exception as e:
                        print(f"❌ 추출 실패: {str(e)}")
                        result = {
                            'status': 'ERROR',
                            'chat_title': chat_title,
                            'error': str(e),
                            'method': 'keyboard_shortcuts',
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    results.append(result)
                    
                    # 다음 검색을 위해 Ctrl+F로 검색창 닫기
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(1000)
                
                return results
                
            except Exception as e:
                print(f"❌ 오류: {str(e)}")
                return []
            finally:
                await browser.close()
    
    async def extract_with_coordinate_click(self):
        """좌표 기반 클릭으로 추출"""
        print("🎯 좌표 기반 클릭 WhatsApp 추출")
        print("=" * 50)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            try:
                # WhatsApp Web 접속
                await page.goto("https://web.whatsapp.com/")
                await page.wait_for_selector("#side", timeout=120000)
                print("✅ 로그인 완료!")
                
                results = []
                for chat_title in self.hvdc_chats:
                    print(f"\n📱 채팅방 처리: {chat_title}")
                    
                    try:
                        # 검색창 위치 클릭 (대략적인 좌표)
                        await page.mouse.click(400, 100)  # 검색창 대략적 위치
                        await page.wait_for_timeout(1000)
                        
                        # 검색어 입력
                        await page.keyboard.type(chat_title)
                        await page.wait_for_timeout(2000)
                        
                        # 첫 번째 채팅방 클릭 (대략적 위치)
                        await page.mouse.click(400, 200)
                        await page.wait_for_timeout(3000)
                        
                        # 메시지 추출
                        messages = await self.extract_messages_alternative(page)
                        
                        result = {
                            'status': 'SUCCESS',
                            'chat_title': chat_title,
                            'messages': messages,
                            'method': 'coordinate_click',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        print(f"✅ 추출 성공: {len(messages)}개 메시지")
                        
                    except Exception as e:
                        print(f"❌ 추출 실패: {str(e)}")
                        result = {
                            'status': 'ERROR',
                            'chat_title': chat_title,
                            'error': str(e),
                            'method': 'coordinate_click',
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    results.append(result)
                
                return results
                
            except Exception as e:
                print(f"❌ 오류: {str(e)}")
                return []
            finally:
                await browser.close()
    
    async def extract_messages_alternative(self, page):
        """대안적 메시지 추출 방법"""
        messages = []
        
        # 여러 방법으로 메시지 추출 시도
        extraction_methods = [
            # 방법 1: 일반적인 메시지 셀렉터
            lambda: page.locator('[data-testid*="message"]').all_text_contents(),
            # 방법 2: 메시지 컨테이너
            lambda: page.locator('[data-testid="conversation-panel-messages"]').all_text_contents(),
            # 방법 3: 모든 텍스트 요소
            lambda: page.locator('div[role="row"]').all_text_contents(),
            # 방법 4: 스크롤 가능한 영역
            lambda: page.locator('[data-testid="scrollable-area"]').all_text_contents()
        ]
        
        for i, method in enumerate(extraction_methods):
            try:
                result = await method()
                if result and any(text.strip() for text in result):
                    messages = [text.strip() for text in result if text.strip()]
                    print(f"✅ 메시지 추출 방법 {i+1} 성공")
                    break
            except Exception as e:
                print(f"⚠️ 메시지 추출 방법 {i+1} 실패: {str(e)}")
                continue
        
        return messages
    
    async def manual_extraction_mode(self):
        """수동 추출 모드"""
        print("👤 수동 추출 모드")
        print("=" * 50)
        print("⚠️ 브라우저가 열리면 수동으로 채팅방을 선택하고 메시지를 복사하세요.")
        print("⚠️ 각 채팅방의 메시지를 복사한 후 Enter를 눌러 다음으로 진행하세요.")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto("https://web.whatsapp.com/")
                await page.wait_for_selector("#side", timeout=120000)
                print("✅ 로그인 완료!")
                
                results = []
                for chat_title in self.hvdc_chats:
                    print(f"\n📱 채팅방: {chat_title}")
                    print("⚠️ 수동으로 채팅방을 선택하고 메시지를 복사하세요.")
                    print("⚠️ 복사 완료 후 Enter를 누르세요...")
                    
                    input()  # 사용자 입력 대기
                    
                    # 클립보드에서 텍스트 가져오기
                    clipboard_text = await page.evaluate("() => navigator.clipboard.readText()")
                    
                    if clipboard_text:
                        messages = [line.strip() for line in clipboard_text.split('\n') if line.strip()]
                        result = {
                            'status': 'SUCCESS',
                            'chat_title': chat_title,
                            'messages': messages,
                            'method': 'manual',
                            'timestamp': datetime.now().isoformat()
                        }
                        print(f"✅ 수동 추출 완료: {len(messages)}개 메시지")
                    else:
                        result = {
                            'status': 'ERROR',
                            'chat_title': chat_title,
                            'error': '클립보드에서 텍스트를 가져올 수 없습니다',
                            'method': 'manual',
                            'timestamp': datetime.now().isoformat()
                        }
                        print("❌ 클립보드 텍스트 없음")
                    
                    results.append(result)
                
                return results
                
            except Exception as e:
                print(f"❌ 오류: {str(e)}")
                return []
            finally:
                await browser.close()
    
    def save_results(self, results, method_name):
        """결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/whatsapp_alternative_{method_name}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 저장: {filename}")
        return filename

async def main():
    """메인 실행 함수"""
    print("🤖 MACHO-GPT v3.4-mini WhatsApp RPA 대안 접근법")
    print("=" * 60)
    print("1. 키보드 단축키 기반")
    print("2. 좌표 기반 클릭")
    print("3. 수동 추출 모드")
    print("=" * 60)
    
    extractor = WhatsAppRPAAlternative()
    
    # 사용자 선택
    choice = input("방법을 선택하세요 (1-3): ").strip()
    
    if choice == "1":
        results = await extractor.extract_with_keyboard_shortcuts()
        extractor.save_results(results, "keyboard")
    elif choice == "2":
        results = await extractor.extract_with_coordinate_click()
        extractor.save_results(results, "coordinate")
    elif choice == "3":
        results = await extractor.manual_extraction_mode()
        extractor.save_results(results, "manual")
    else:
        print("❌ 잘못된 선택입니다.")
        return
    
    # 결과 요약
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    total_messages = sum(len(r.get('messages', [])) for r in results if r['status'] == 'SUCCESS')
    
    print(f"\n📊 결과 요약:")
    print(f"   - 성공한 채팅방: {success_count}/{len(results)}개")
    print(f"   - 총 메시지: {total_messages}개")

if __name__ == "__main__":
    asyncio.run(main()) 