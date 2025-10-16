#!/usr/bin/env python3
"""
WhatsApp RPA 빠른 테스트 스크립트
--------------------------------
최신 DOM 구조 대응 기능을 빠르게 테스트합니다.
"""

import asyncio
from playwright.async_api import async_playwright

async def test_search_functionality():
    """검색 기능 테스트"""
    print("🔍 WhatsApp Web 검색 기능 테스트")
    print("=" * 40)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        try:
            # WhatsApp Web 접속
            await page.goto("https://web.whatsapp.com/")
            print("🌐 WhatsApp Web 접속 완료")
            
            # 로그인 대기
            print("⚠️ QR 코드를 스캔하여 로그인해주세요...")
            await page.wait_for_selector("#side", timeout=120000)
            print("✅ 로그인 완료!")
            
            # 1단계: 돋보기 버튼 찾기 및 클릭
            print("\n🔍 1단계: 돋보기 버튼 테스트")
            try:
                btn_selector = 'button[aria-label="Search or start new chat"]'
                await page.wait_for_selector(btn_selector, timeout=5000)
                print("✅ 돋보기 버튼 발견")
                
                await page.click(btn_selector)
                print("✅ 돋보기 버튼 클릭 성공")
                
            except Exception as e:
                print(f"❌ 돋보기 버튼 실패: {str(e)}")
                print("🔄 키보드 단축키 시도...")
                await page.keyboard.press('Control+Alt+Shift+F')
                print("✅ 키보드 단축키 실행")
            
            # 2단계: 검색창 렌더링 확인
            print("\n🔍 2단계: 검색창 렌더링 테스트")
            try:
                search_selectors = [
                    'div[title="Search input textbox"]',
                    '[role="searchbox"]',
                    'input[type="text"]'
                ]
                
                search_found = False
                for selector in search_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        print(f"✅ 검색창 발견: {selector}")
                        search_found = True
                        break
                    except:
                        continue
                
                if not search_found:
                    print("❌ 검색창을 찾을 수 없습니다")
                    return False
                
            except Exception as e:
                print(f"❌ 검색창 테스트 실패: {str(e)}")
                return False
            
            # 3단계: 검색어 입력 테스트
            print("\n🔍 3단계: 검색어 입력 테스트")
            try:
                # 검색창에 텍스트 입력
                await page.keyboard.type("test")
                await page.wait_for_timeout(2000)
                print("✅ 검색어 입력 성공")
                
                # 검색창 클리어
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(1000)
                print("✅ 검색창 클리어 성공")
                
            except Exception as e:
                print(f"❌ 검색어 입력 실패: {str(e)}")
                return False
            
            print("\n✅ 모든 테스트 통과!")
            return True
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {str(e)}")
            return False
        finally:
            await browser.close()

async def test_chat_selection():
    """채팅방 선택 테스트"""
    print("\n💬 채팅방 선택 테스트")
    print("=" * 40)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        try:
            # WhatsApp Web 접속 및 로그인
            await page.goto("https://web.whatsapp.com/")
            await page.wait_for_selector("#side", timeout=120000)
            print("✅ 로그인 완료!")
            
            # 첫 번째 채팅방 클릭 테스트
            chat_selectors = [
                '[data-testid="cell-title-text"]',
                'span[title]',
                'div[title]',
                '[role="row"]'
            ]
            
            chat_found = False
            for selector in chat_selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        await elements[0].click()
                        print(f"✅ 채팅방 선택 성공: {selector}")
                        chat_found = True
                        break
                except:
                    continue
            
            if not chat_found:
                print("❌ 채팅방을 선택할 수 없습니다")
                return False
            
            await page.wait_for_timeout(3000)
            print("✅ 채팅방 열기 성공")
            return True
            
        except Exception as e:
            print(f"❌ 채팅방 선택 테스트 실패: {str(e)}")
            return False
        finally:
            await browser.close()

async def main():
    """메인 테스트 함수"""
    print("🧪 WhatsApp RPA 빠른 테스트")
    print("=" * 50)
    
    # 검색 기능 테스트
    search_success = await test_search_functionality()
    
    if search_success:
        # 채팅방 선택 테스트
        chat_success = await test_chat_selection()
        
        print("\n📊 테스트 결과:")
        print(f"   🔍 검색 기능: {'✅ 통과' if search_success else '❌ 실패'}")
        print(f"   💬 채팅방 선택: {'✅ 통과' if chat_success else '❌ 실패'}")
        
        if search_success and chat_success:
            print("\n🎉 모든 테스트 통과! 메인 추출 스크립트를 실행할 수 있습니다.")
        else:
            print("\n⚠️ 일부 테스트 실패. 추가 디버깅이 필요합니다.")
    else:
        print("\n❌ 검색 기능 테스트 실패. 기본 기능부터 확인이 필요합니다.")

if __name__ == "__main__":
    asyncio.run(main()) 