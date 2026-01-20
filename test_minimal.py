from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com")
        print("Page title:", page.title())
        time.sleep(10)
        print("Closing browser...")
        browser.close()

if __name__ == "__main__":
    run()
