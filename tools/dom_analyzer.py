#!/usr/bin/env python3
"""
WhatsApp Web DOM 구조 분석기
---------------------------
WhatsApp Web의 실제 DOM 구조를 분석하여 정확한 셀렉터를 찾습니다.
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright


class WhatsAppDOMAnalyzer:
    """WhatsApp Web DOM 구조 분석기"""

    def __init__(self):
        self.analysis_results = {}

    async def analyze_dom_structure(self):
        """WhatsApp Web의 DOM 구조를 분석"""
        print("[ANALYZE] WhatsApp Web DOM 구조 분석 시작")
        print("=" * 50)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                # WhatsApp Web 접속
                await page.goto(
                    "https://web.whatsapp.com/", wait_until="domcontentloaded"
                )
                print("[SUCCESS] WhatsApp Web 접속 완료")

                # 로그인 대기
                print("[WARNING] QR 코드를 스캔하여 로그인해주세요...")
                await page.wait_for_selector("#side", timeout=120000)
                print("[SUCCESS] 로그인 완료!")

                # DOM 구조 분석
                await self.analyze_search_elements(page)
                await self.analyze_chat_elements(page)
                await self.analyze_message_elements(page)

                # 결과 저장
                self.save_analysis_results()

            except Exception as e:
                print(f"[ERROR] 분석 중 오류: {str(e)}")
            finally:
                await browser.close()

    async def analyze_search_elements(self, page):
        """검색 관련 요소 분석"""
        print("\n[ANALYZE] 검색 요소 분석 중...")

        # 가능한 검색 셀렉터들
        search_selectors = [
            '[data-testid*="search"]',
            '[aria-label*="search" i]',
            '[title*="search" i]',
            '[placeholder*="search" i]',
            'input[type="text"]',
            'div[role="textbox"]',
            'div[contenteditable="true"]',
        ]

        search_elements = []
        for selector in search_selectors:
            try:
                elements = await page.locator(selector).all()
                for i, element in enumerate(elements):
                    try:
                        tag_name = await element.evaluate("el => el.tagName")
                        text_content = await element.text_content()
                        aria_label = await element.get_attribute("aria-label")
                        title = await element.get_attribute("title")
                        placeholder = await element.get_attribute("placeholder")
                        data_testid = await element.get_attribute("data-testid")
                        role = await element.get_attribute("role")

                        # 검색 관련 키워드가 포함된 요소만 필터링
                        search_keywords = ["search", "검색", "chat", "conversation"]
                        is_search_related = any(
                            keyword in (text_content or "").lower()
                            or keyword in (aria_label or "").lower()
                            or keyword in (title or "").lower()
                            or keyword in (placeholder or "").lower()
                            for keyword in search_keywords
                        )

                        if is_search_related:
                            search_elements.append(
                                {
                                    "selector": f"{selector}:nth-child({i+1})",
                                    "tag_name": tag_name,
                                    "text_content": text_content,
                                    "aria_label": aria_label,
                                    "title": title,
                                    "placeholder": placeholder,
                                    "data_testid": data_testid,
                                    "role": role,
                                }
                            )
                    except Exception as e:
                        continue
            except Exception:
                continue

        self.analysis_results["search_elements"] = search_elements
        print(f"[SUCCESS] 검색 요소 {len(search_elements)}개 발견")

        # 발견된 요소들 출력
        for i, element in enumerate(search_elements):
            print(f"  {i+1}. {element['selector']}")
            print(f"     [TEXT] 텍스트: {element['text_content']}")
            print(f"     [LABEL] aria-label: {element['aria_label']}")
            print(f"     [TITLE] title: {element['title']}")
            print(f"     [PLACEHOLDER] placeholder: {element['placeholder']}")
            print(f"     [ID] data-testid: {element['data_testid']}")
            print(f"     [ROLE] role: {element['role']}")
            print()

    async def analyze_chat_elements(self, page):
        """채팅방 관련 요소 분석"""
        print("[ANALYZE] 채팅방 요소 분석 중...")

        # 채팅방 목록에서 첫 번째 채팅방 찾기
        chat_selectors = [
            '[data-testid*="cell"]',
            '[role="row"]',
            '[aria-label*="chat" i]',
            '[title*="chat" i]',
            'div[role="button"]',
        ]

        chat_elements = []
        for selector in chat_selectors:
            try:
                elements = await page.locator(selector).all()
                for i, element in enumerate(elements[:5]):  # 처음 5개만 분석
                    try:
                        tag_name = await element.evaluate("el => el.tagName")
                        text_content = await element.text_content()
                        aria_label = await element.get_attribute("aria-label")
                        title = await element.get_attribute("title")
                        data_testid = await element.get_attribute("data-testid")
                        role = await element.get_attribute("role")

                        # 채팅방 관련 키워드가 포함된 요소만 필터링
                        chat_keywords = ["chat", "conversation", "message", "group"]
                        is_chat_related = any(
                            keyword in (text_content or "").lower()
                            or keyword in (aria_label or "").lower()
                            or keyword in (title or "").lower()
                            for keyword in chat_keywords
                        )

                        if is_chat_related:
                            chat_elements.append(
                                {
                                    "selector": f"{selector}:nth-child({i+1})",
                                    "tag_name": tag_name,
                                    "text_content": text_content,
                                    "aria_label": aria_label,
                                    "title": title,
                                    "data_testid": data_testid,
                                    "role": role,
                                }
                            )
                    except Exception:
                        continue
            except Exception:
                continue

        self.analysis_results["chat_elements"] = chat_elements
        print(f"[SUCCESS] 채팅방 요소 {len(chat_elements)}개 발견")

    async def analyze_message_elements(self, page):
        """메시지 관련 요소 분석"""
        print("[ANALYZE] 메시지 요소 분석 중...")

        # 메시지 패널 찾기
        message_selectors = [
            '[data-testid*="message"]',
            '[data-testid*="conversation"]',
            '[role="main"]',
            '[aria-label*="message" i]',
        ]

        message_elements = []
        for selector in message_selectors:
            try:
                elements = await page.locator(selector).all()
                for i, element in enumerate(elements[:3]):  # 처음 3개만 분석
                    try:
                        tag_name = await element.evaluate("el => el.tagName")
                        text_content = await element.text_content()
                        aria_label = await element.get_attribute("aria-label")
                        data_testid = await element.get_attribute("data-testid")
                        role = await element.get_attribute("role")

                        message_elements.append(
                            {
                                "selector": f"{selector}:nth-child({i+1})",
                                "tag_name": tag_name,
                                "text_content": (
                                    text_content[:100] + "..."
                                    if len(text_content or "") > 100
                                    else text_content
                                ),
                                "aria_label": aria_label,
                                "data_testid": data_testid,
                                "role": role,
                            }
                        )
                    except Exception:
                        continue
            except Exception:
                continue

        self.analysis_results["message_elements"] = message_elements
        print(f"[SUCCESS] 메시지 요소 {len(message_elements)}개 발견")

    def save_analysis_results(self):
        """분석 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"whatsapp_dom_analysis_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)

        print(f"\n[SAVE] 분석 결과 저장: {filename}")

        # 추천 셀렉터 생성
        self.generate_recommended_selectors()

    def generate_recommended_selectors(self):
        """분석 결과를 바탕으로 추천 셀렉터 생성"""
        print("\n[RECOMMEND] 추천 셀렉터:")
        print("=" * 30)

        # 검색 셀렉터 추천
        if self.analysis_results.get("search_elements"):
            print("[SEARCH] 검색창 셀렉터:")
            for element in self.analysis_results["search_elements"]:
                if element.get("data_testid"):
                    print(f"   - '[data-testid=\"{element['data_testid']}\"]'")
                elif element.get("aria_label"):
                    print(f"   - '[aria-label=\"{element['aria_label']}\"]'")
                elif element.get("title"):
                    print(f"   - '[title=\"{element['title']}\"]'")

        # 채팅방 셀렉터 추천
        if self.analysis_results.get("chat_elements"):
            print("\n[CHAT] 채팅방 셀렉터:")
            for element in self.analysis_results["chat_elements"]:
                if element.get("data_testid"):
                    print(f"   - '[data-testid=\"{element['data_testid']}\"]'")
                elif element.get("title"):
                    print(f"   - '[title=\"{element['title']}\"]'")


async def main():
    """메인 실행 함수"""
    print("[DOM Analyzer] WhatsApp Web DOM 구조 분석기")
    print("=" * 40)
    print("[WARNING] 이 도구는 WhatsApp Web의 실제 DOM 구조를 분석합니다.")
    print("[WARNING] QR 코드 스캔이 필요할 수 있습니다.")
    print("=" * 40)

    analyzer = WhatsAppDOMAnalyzer()
    await analyzer.analyze_dom_structure()


if __name__ == "__main__":
    asyncio.run(main())
