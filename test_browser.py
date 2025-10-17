#!/usr/bin/env python3
"""Test browser launch for WhatsApp Web"""

from playwright.sync_api import sync_playwright
import time


def test_browser():
    with sync_playwright() as p:
        print("Starting browser...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Navigating to WhatsApp Web...")
        page.goto("https://web.whatsapp.com")

        print("Browser opened. Check for QR code to scan.")
        print("Waiting 60 seconds for QR scan...")
        time.sleep(60)

        print("Closing browser...")
        browser.close()


if __name__ == "__main__":
    test_browser()
