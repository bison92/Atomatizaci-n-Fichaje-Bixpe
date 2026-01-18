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
        browser = p.chromium.launch(
            headless=headless, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled" 
            ],
            ignore_default_args=["--enable-automation"]
        )
        
        # Use a standard User-Agent to avoid being blocked as a bot
        # Also grant geolocation permissions as Bixpe might require them to show the clock-in buttons
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            permissions=['geolocation'],
            geolocation={'latitude': 41.651304749576475, 'longitude': -0.9345988765123099}, # Zaragoza
            viewport={'width': 1280, 'height': 720},
            locale='es-ES'
        )
        page = context.new_page()
        page.set_default_timeout(60000) # Increase default timeout to 60s
        
        # Capture console logs to debug JS errors
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
        
        # Capture network failures to identify sources
        page.on("requestfailed", lambda request: print(f"Request failed: {request.url} - {request.failure}"))
        
        # -------------------------------------------------------------------------
        # NETWORK INTERCEPTION: Block problematic scripts
        # 1. Block Google Maps (real script) so the app uses our Mock
        # 2. Block trackers/analytics to speed up load and avoid noise
        # -------------------------------------------------------------------------
        def block_routes(route):
            route.abort()

        # Block Maps, Analytics, Facebook, etc.
        page.route("**/*maps.googleapis.com*", block_routes)
        page.route("**/*analytics*", block_routes)
        page.route("**/*facebook*", block_routes)
        page.route("**/*cookie-script*", block_routes)
        
        # -------------------------------------------------------------------------
        # JS INJECTION: Override Geolocation API & Google Maps Mock
        # -------------------------------------------------------------------------
        page.add_init_script("""
            // 1. Mock Geolocation
            const mockLocation = {
                coords: {
                    latitude: 41.651304749576475,
                    longitude: -0.9345988765123099,
                    accuracy: 10,
                    altitude: null,
                    altitudeAccuracy: null,
                    heading: null,
                    speed: null
                },
                timestamp: Date.now()
            };
            
            navigator.geolocation.getCurrentPosition = function(success, error, options) {
                console.log("[MockGeo] App requested location. Returning Zaragoza.");
                success(mockLocation);
            };
            
            navigator.geolocation.watchPosition = function(success, error, options) {
                console.log("[MockGeo] App watching location. Returning Zaragoza.");
                success(mockLocation);
                return 42; 
            };
            
            // 2. Mock Google Maps to survive 403/Block
            window.google = window.google || {};
            window.google.maps = window.google.maps || {
                Geocoder: function() { 
                    return { 
                        geocode: function(req, cb) { 
                            console.log("[MockMaps] Geocode requested. Returning success.");
                            cb([{ geometry: { location: { lat: () => 41.65, lng: () => -0.93 } } }], 'OK'); 
                        } 
                    }; 
                },
                Map: function() { console.log("[MockMaps] Map initialized."); },
                Marker: function() {},
                LatLng: function(lat, lng) { return { lat: lat, lng: lng }; },
                Animation: {},
                MapTypeId: { ROADMAP: 'roadmap' }
            };
        """)
        # -------------------------------------------------------------------------
        # -------------------------------------------------------------------------
        # JS INJECTION: Override Geolocation API to bypass generic 403 blocks
        # This mocks the API so it returns success immediately without network check
        # -------------------------------------------------------------------------
        page.add_init_script("""
            const mockLocation = {
                coords: {
                    latitude: 41.651304749576475,
                    longitude: -0.9345988765123099,
                    accuracy: 10,
                    altitude: null,
                    altitudeAccuracy: null,
                    heading: null,
                    speed: null
                },
                timestamp: Date.now()
            };
            
            navigator.geolocation.getCurrentPosition = function(success, error, options) {
                console.log("[MockGeo] App requested location. Returning Zaragoza.");
                success(mockLocation);
            };
            
            navigator.geolocation.watchPosition = function(success, error, options) {
                console.log("[MockGeo] App watching location. Returning Zaragoza.");
                success(mockLocation);
                return 42; # Random ID
            };
        """)
        # -------------------------------------------------------------------------

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
            # HTML source confirms id="Username" and name="Username" (Case sensitive!)
            # Also type is "text", not "email".
            email_selectors = ['#Username', 'input[name="Username"]', 'input[placeholder="Email"]', '#username']
            password_selectors = ['#Password', 'input[name="Password"]', 'input[type="password"]']
            submit_selectors = ['button[type="submit"]', 'text=Iniciar sesión', 'text=INICIAR SESIÓN']
            
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
                # Screenshot for debug
                page.screenshot(path="debug_no_email.png")
                raise Exception("Email field not found. Checked: " + ", ".join(email_selectors))

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
                page.wait_for_load_state("networkidle", timeout=30000)
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

    # Selectors based on Action
    selectors = []
    if action == "START":
        selectors = [
            "#btn-start-workday", # ID confirmed from user screenshot
            ".fa-play", 
            "button[data-original-title='Empezar']",
            "text=Empezar"
        ]
    elif action == "PAUSE":
        selectors = [
            "#btn-pause-workday", # ID confirmed for "Pausa General"
            ".fa-pause", 
            ".fa-utensils", # FontAwesome 5
            ".fa-cutlery", # FontAwesome 4
            "button[data-original-title='Pausa General']",
            "button[data-original-title='Comida']"
        ]
    elif action == "RESUME":
        selectors = [
            "#btn-resume-workday", # Assumed naming convention
            ".fa-redo",
            ".fa-sync",
            ".fa-rotate-right",
            "button[data-original-title='Reanudar']"
        ]
    elif action == "END":
        selectors = [
            "#btn-stop-workday", # ID from CSS/Convention
            ".fa-stop",
            ".fa-square", 
            "button[data-original-title='Finalizar']"
        ]

    print(f"Performing action: {action}")
    
    action_button = None
    for selector in selectors:
        try:
            print(f"Looking for selector: {selector}")
            # Use strict=False to allow fuzzy matching if multiple exist, but prioritize visibility
            btn = page.locator(selector).first
            if btn.is_visible(timeout=2000):
                print(f"Found visible button: {selector}")
                action_button = btn
                break
        except Exception as e:
            print(f"Selector check failed for {selector}: {e}")
            continue

    if action_button:
        try:
            # 1. Click the main action button
            print(f"Attempting to Click: {selector}")
            action_button.click(timeout=5000)
            print(f"Clicked: {selector}")
            
            # 2. HANDLE CONFIRMATION DIALOG (SweetAlert)
            # The user reported a popup asking "Are you sure?"
            print("Checking for confirmation dialog...")
            time.sleep(2) # Short wait for animation
            
            # Look for specific confirm buttons based on the action context
            # Common text: "Sí, iniciar", "Sí, finalizar", "Sí, pausar"
            # Or generic SweetAlert selector: button.confirm
            
            confirm_selectors = [
                "button.confirm", # Generic SweetAlert confirm class
                "button:has-text('Sí, iniciar')",
                "button:has-text('Sí, finalizar')",
                "button:has-text('Sí, pausar')",
                "button:has-text('Sí, reanudar')", # Guessing reanudar
                "div.sweet-alert.visible button.confirm" # More specific
            ]
            
            confirmed = False
            for conf_sel in confirm_selectors:
                if page.locator(conf_sel).is_visible():
                    print(f"Confirmation dialog found! Clicking: {conf_sel}")
                    page.locator(conf_sel).click()
                    confirmed = True
                    print("Confirmation clicked.")
                    break
            
            if not confirmed:
                print("No confirmation dialog detected, or it auto-closed.")

            # Final check -> Screenshot after action
            page.wait_for_timeout(3000)
            page.screenshot(path=f"screenshot_{action}_{time.strftime('%Y%m%d_%H%M%S')}.png")
            return True

        except Exception as e:
            print(f"Error clicking button {selector}: {e}")
            # Try JS click as fallback if standard click fails
            try:
                print("Attempting JS click...")
                page.evaluate("el => el.click()", action_button.element_handle())
                
                # Check confirmation again after JS click
                time.sleep(2)
                if page.locator("button.confirm").is_visible():
                     page.locator("button.confirm").click()
                     print("Confirmation clicked (after JS click).")

                return True
            except Exception as js_e:
                 print(f"JS Click also failed: {js_e}")
    
    else:
        print(f"Error: No suitable button found for action {action}")
        # Debug: Dump HTML to see what's wrong
        with open(f"debug_fail_{action}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"Saved debug_fail_{action}.html with page content.")
        
        # New: Take full page screenshot on failure
        page.screenshot(path=f"error_{action}.png", full_page=True)
        sys.exit(1)
        # Wait for potential dynamic content
        page.wait_for_timeout(5000)

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

            elif action == "PAUSE":
                print("Attempting to Pause for Lunch (Bowl Icon)")
                if page.is_visible("#btn-food-working"):
                    target_selector = "#btn-food-working"
                elif page.is_visible("#btn-pause-working"):
                    target_selector = "#btn-pause-working"
                elif page.is_visible(".fa-utensils"):
                    target_selector = ".fa-utensils"
                elif page.is_visible(".fa-cutlery"):
                     target_selector = ".fa-cutlery"
                
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
                    # Only click text if it looks like a button
                    target_selector = "text=Reanudar"
                
            elif action == "END":
                print("Attempting to End Journey (Red Stop Button)")
                if page.is_visible("#btn-stop-working"):
                    target_selector = "#btn-stop-working"
                elif page.is_visible(".fa-stop"):
                    target_selector = ".fa-stop"

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
                 # Dump HTML for debugging
                 debug_file = f"debug_fail_{action}.html"
                 with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(page.content())
                 print(f"Saved {debug_file} with page content.")
                 
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

