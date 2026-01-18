import os
import sys
import json
import argparse
from datetime import datetime, date
from playwright.sync_api import sync_playwright

def load_holidays(json_path):
    """Loads holidays from the JSON file."""
    try:
        with open(json_path, 'r') as f:
            holidays = json.load(f)
        return holidays
    except FileNotFoundError:
        print(f"Warning: {json_path} not found. No holidays loaded.")
        return []

def is_holiday_or_weekend(holidays):
    """Checks if today is a weekend or a holiday."""
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    # Check Weekend (5=Saturday, 6=Sunday)
    if today.weekday() >= 5:
        print(f"Today is weekend ({today.strftime('%A')}). Skipping.")
        return True
        
    # Check Holiday
    if today_str in holidays:
        print(f"Today is a holiday ({today_str}). Skipping.")
        return True
        
    return False

def run_automation(email, password, action, headless=True, dry_run=False):
    with sync_playwright() as p:
        # Launch with specific args to avoid detection/rendering issues
        browser = p.chromium.launch(headless=headless, args=["--no-sandbox", "--disable-setuid-sandbox"])
        
        # Use a standard User-Agent to avoid being blocked as a bot
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(60000) # Increase default timeout to 60s
        
        print("Navigating to Bixpe...")
        page.goto("https://worktime.bixpe.com/")
        
        # Handle Cookies if present
        try:
            if page.is_visible("text=Aceptar todas", timeout=5000):
                page.click("text=Aceptar todas")
            elif page.is_visible("text=Aceptar", timeout=5000):
                page.click("text=Aceptar")
            elif page.is_visible("button[id*='cookie']", timeout=5000):
                 page.click("button[id*='cookie']")
        except:
            pass # Ignore if no cookies found
            
        # Login
        print("Logging in...")
        try:
            # Wait explicitly for the username field with multiple potential selectors
            email_selectors = ['#UserName', 'input[name="UserName"]', 'input[type="email"]', 'input[id*="user"]']
            password_selectors = ['input[type="password"]', 'input[name="Password"]', '#Password']
            submit_selectors = ['text=INICIAR SESIÓN', 'button[type="submit"]', 'text=Entrar', 'text=Login']
            
            # Fill Email
            email_filled = False
            for selector in email_selectors:
                try:
                    if page.is_visible(selector, timeout=2000):
                        page.fill(selector, email)
                        email_filled = True
                        print(f"Filled email using: {selector}")
                        break
                except:
                    continue
            
            if not email_filled:
                print("Could not find email field. Dumping HTML snippet...")
                print(page.inner_html("body")[:500])
                raise Exception("Email field not found")

            # Fill Password
            for selector in password_selectors:
                try:
                    if page.is_visible(selector, timeout=2000):
                        page.fill(selector, password)
                        print(f"Filled password using: {selector}")
                        break
                except:
                   continue

            # Click Login
            clicked = False
            for selector in submit_selectors:
                try:
                    if page.is_visible(selector, timeout=2000):
                        page.click(selector)
                        print(f"Clicked login button: {selector}")
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                 # Last resort: press Enter
                 page.press('input[type="password"]', 'Enter')
                 print("Pressed Enter to login")
            
            # Wait for dashboard to load
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except:
                print("Warning: Network idle timeout. Proceeding...")

        except Exception as e:
            print(f"Error during login: {e}")
            print(f"Current URL: {page.url}")
            print(f"Page Title: {page.title()}")
            page.screenshot(path="error_login.png")
            # Dump HTML for debugging
            with open("debug_login.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved debug_login.html. Please verify selectors.")
            browser.close()
            sys.exit(1)

        print(f"Performing action: {action}")
        
        # Wait for potential dynamic content
        page.wait_for_timeout(3000)

        # DEBUG: Save dashboard HTML to identify buttons
        with open("dashboard_dump.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        
        try:
            target_selector = None
            
            if action == "START":
                print("Attempting to Start Journey (Green Play Button)")
                if page.is_visible("#btn-start-working"):
                     target_selector = "#btn-start-working"
                elif page.is_visible("#btn-resume-working"):
                     target_selector = "#btn-resume-working"
                elif page.is_visible(".fa-play"):
                     target_selector = ".fa-play"
                else:
                    print("Could not find Play button. Trying text fallback...")
                    target_selector = "text=Empieza"

            elif action == "PAUSE":
                print("Attempting to Pause for Lunch (Bowl Icon)")
                if page.is_visible("#btn-food-working"):
                    target_selector = "#btn-food-working"
                elif page.is_visible("#btn-pause-working"):
                    target_selector = "#btn-pause-working"
                elif page.is_visible("text=Pausa"):
                     target_selector = "text=Pausa"
                
            elif action == "RESUME":
                print("Attempting to Resume (Circular Arrow Button)")
                if page.is_visible("#btn-resume-working"):
                     target_selector = "#btn-resume-working"
                elif page.is_visible(".fa-redo"):
                    target_selector = ".fa-redo"
                elif page.is_visible(".fa-sync"):
                    target_selector = ".fa-sync"
                elif page.is_visible(".fa-rotate-right"):
                    target_selector = ".fa-rotate-right"
                elif page.is_visible("text=Reanudar"):
                    target_selector = "text=Reanudar"
                
            elif action == "END":
                print("Attempting to End Journey (Red Stop Button)")
                if page.is_visible("#btn-stop-working"):
                    target_selector = "#btn-stop-working"
                elif page.is_visible(".fa-stop"):
                    target_selector = ".fa-stop"
                elif page.is_visible("text=Finalizar"):
                    target_selector = "text=Finalizar"

            if target_selector:
                if dry_run:
                    print(f"[DRY-RUN] Would have clicked: {target_selector}")
                    # Highlight for visual confirmation
                    page.eval_on_selector(target_selector, "el => el.style.border = '5px solid red'")
                    page.wait_for_timeout(3000) # Give user time to see it
                else:
                    page.click(target_selector)
                    print(f"Clicked: {target_selector}")
                    # Wait a bit for action to record
                    page.wait_for_timeout(5000)
            else:
                 print(f"Error: No suitable button found for action {action}")
                 if not dry_run: # Don't exit on dry run, just finish
                    sys.exit(1)
            
            # Take confirmation screenshot
            screenshot_path = f"screenshot_{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Error executing action {action}: {e}")
            page.screenshot(path=f"error_{action}.png")
            sys.exit(1)

        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["START", "PAUSE", "RESUME", "END"], required=True)
    parser.add_argument("--visible", action="store_true", help="Run with visible browser for debugging")
    parser.add_argument("--force", action="store_true", help="Ignore schedule and holiday checks")
    parser.add_argument("--dry-run", action="store_true", help="Perform login/nav but do not click final action button")
    args = parser.parse_args()

    # Load holidays
    holidays_file = os.path.join(os.path.dirname(__file__), "..", "holidays.json")
    holidays = load_holidays(holidays_file)

    if not args.force:
        if is_holiday_or_weekend(holidays):
            sys.exit(0)

    # Load Schedule
    schedule_file = os.path.join(os.path.dirname(__file__), "..", "schedule.json")
    try:
        with open(schedule_file, 'r') as f:
            schedule_config = json.load(f)
    except FileNotFoundError:
        print("Warning: schedule.json not found. Using defaults.")
        schedule_config = {}

    if not args.force:
        # Validate Action for Today
        today = date.today()
        # 0-4 is Mon-Fri. 4 is Friday.
        is_friday = today.weekday() == 4
        
        day_key = "friday" if is_friday else "mon_thu"
        day_schedule = schedule_config.get(day_key, {})
        
        # Map CLI arg to JSON key
        action_map = {
            "START": "start",
            "PAUSE": "break_start",
            "RESUME": "break_end",
            "END": "end"
        }
        
        config_key = action_map.get(args.action)
        if config_key:
            if day_schedule.get(config_key) is None:
                print(f"Action {args.action} is not scheduled for today ({day_key}). Skipping.")
                sys.exit(0)
            else:
                print(f"Executing {args.action} for {day_key} (Scheduled: {day_schedule.get(config_key)})")

    email = os.environ.get("BIXPE_EMAIL")
    password = os.environ.get("BIXPE_PASSWORD")

    if not email or not password:
        # Fallback for local testing if env vars not set (remove in production!)
        email = input("Enter Bixpe Email: ") if args.visible else None
        password = input("Enter Bixpe Password: ") if args.visible else None
    
    if not email or not password:
        print("Error: BIXPE_EMAIL and BIXPE_PASSWORD environment variables must be set.")
        sys.exit(1)

    run_automation(email, password, args.action, headless=not args.visible, dry_run=args.dry_run)

