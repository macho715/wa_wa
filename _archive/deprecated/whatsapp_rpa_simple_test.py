#!/usr/bin/env python3
"""
WhatsApp RPA 간단 테스트 스크립트 (XPath 부분 일치 + 세션 저장)
------------------------------------------------
개선된 기능들을 간단히 테스트합니다.
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def test_xpath_partial_match():
    """XPath 부분 일치 기능 테스트"""
    print("🧪 XPath 부분 일치 기능 테스트")
    print("=" * 40)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900}
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
            
            # 돋보기 버튼 클릭
            print("\n🔍 돋보기 버튼 클릭...")
            try:
                await page.click('button[aria-label="Search or start new chat"]', timeout=5000)
                print("✅ 돋보기 버튼 클릭 성공")
            except:
                print("🔄 키보드 단축키 사용...")
                await page.keyboard.press('Control+Alt+Shift+F')
                print("✅ 키보드 단축키 성공")
            
            # 검색창 찾기
            print("\n🔍 검색창 찾기...")
            search_selectors = [
                'div[role="searchbox"]',  # ARIA 표준
                'div[contenteditable="true"]',
                'div[data-testid="search"]',
                'input[type="text"]'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    search_box = page.locator(selector).first
                    await search_box.wait_for(state="visible", timeout=10000)
                    print(f"✅ 검색창 발견: {selector}")
                    break
                except:
                    continue
            
            if not search_box:
                print("❌ 검색창을 찾을 수 없습니다")
                return False
            
            # 테스트 검색어 입력
            test_text = "HVDC"
            print(f"\n📝 검색어 입력 테스트: '{test_text}'")
            
            # type() 메서드로 입력
            try:
                print("🔄 type() 메서드로 검색어 입력...")
                await search_box.click()
                await page.wait_for_timeout(500)
                await search_box.type(test_text)
                print("✅ type() 메서드 입력 성공")
                
            except Exception as e:
                print(f"⚠️ type() 메서드 실패: {str(e)}")
                
                # 키보드 직접 입력
                try:
                    print("🔄 키보드 직접 입력 시도...")
                    await search_box.click()
                    await page.wait_for_timeout(500)
                    await page.keyboard.type(test_text)
                    print("✅ 키보드 직접 입력 성공")
                    
                except Exception as e2:
                    print(f"❌ 모든 입력 방법 실패: {str(e2)}")
                    return False
            
            # Enter 키로 검색 실행
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(3000)
            
            # XPath 부분 일치 테스트
            print(f"\n🔍 XPath 부분 일치 테스트: '{test_text}'")
            xpath_patterns = [
                f"//span[contains(@title,'{test_text}')]",
                f"//div[contains(@title,'{test_text}')]",
                f"//span[contains(text(),'{test_text}')]",
                f"//div[contains(text(),'{test_text}')]",
            ]
            
            chat_found = False
            for xpath in xpath_patterns:
                try:
                    print(f"🔍 XPath 시도: {xpath}")
                    result = page.locator(xpath).first
                    
                    # Playwright expect()로 가시성 확인
                    from playwright.async_api import expect
                    await expect(result).to_be_visible(timeout=10000)
                    
                    print(f"✅ 채팅방 발견: {xpath}")
                    chat_found = True
                    break
                    
                except Exception as e:
                    print(f"⚠️ XPath 실패: {xpath}")
                    continue
            
            if not chat_found:
                print("⚠️ XPath로 채팅방을 찾을 수 없었습니다. CSS 셀렉터로 백업 시도...")
                
                # CSS 셀렉터 백업
                css_patterns = [
                    f'span[title*="{test_text}"]',
                    f'div[title*="{test_text}"]',
                    f'[aria-label*="{test_text}"]'
                ]
                
                for css in css_patterns:
                    try:
                        print(f"🔍 CSS 시도: {css}")
                        result = page.locator(css).first
                        await result.wait_for(state="visible", timeout=5000)
                        print(f"✅ 채팅방 발견 (CSS): {css}")
                        chat_found = True
                        break
                        
                    except Exception as e:
                        print(f"⚠️ CSS 실패: {css}")
                        continue
            
            # 입력 결과 확인
            await page.wait_for_timeout(2000)
            print("✅ XPath 부분 일치 테스트 완료")
            
            # 검색창 클리어
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)
            print("✅ 검색창 클리어 완료")
            
            return chat_found
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {str(e)}")
            return False
        finally:
            await browser.close()

async def test_session_save():
    """세션 저장 기능 테스트"""
    print("\n🧪 세션 저장 기능 테스트")
    print("=" * 40)
    
    auth_file = "auth_backups/test_auth.json"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900}
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
            
            # 세션 저장
            print("💾 세션 저장 중...")
            await context.storage_state(path=auth_file)
            print("✅ 세션 저장 완료")
            
            # 세션 파일 확인
            if Path(auth_file).exists():
                print(f"✅ 세션 파일 생성 확인: {auth_file}")
                return True
            else:
                print("❌ 세션 파일이 생성되지 않았습니다")
                return False
                
        except Exception as e:
            print(f"❌ 세션 저장 테스트 중 오류: {str(e)}")
            return False
        finally:
            await browser.close()

async def main():
    """메인 테스트 함수"""
    print("🧪 WhatsApp RPA 개선 기능 테스트")
    print("=" * 50)
    
    # XPath 부분 일치 테스트
    xpath_success = await test_xpath_partial_match()
    
    # 세션 저장 테스트
    session_success = await test_session_save()
    
    print(f"\n📊 테스트 결과:")
    print(f"  XPath 부분 일치: {'✅ 성공' if xpath_success else '❌ 실패'}")
    print(f"  세션 저장: {'✅ 성공' if session_success else '❌ 실패'}")
    
    if xpath_success and session_success:
        print("\n🎉 모든 테스트 성공! 메인 추출 스크립트를 실행할 수 있습니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 추가 디버깅이 필요합니다.")

if __name__ == "__main__":
    asyncio.run(main()) 