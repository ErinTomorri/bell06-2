@ -0,0 +1,193 @@
from playwright.sync_api import sync_playwright
import random
import time

def create_stealth_context(browser):
    """Create a browser context with stealth settings and random fingerprints"""
    
    # Random user agents (real ones from different browsers)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    ]
    
    # Random viewport sizes (common screen resolutions)
    viewports = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 720}
    ]
    
    selected_ua = random.choice(user_agents)
    selected_viewport = random.choice(viewports)
    
    context = browser.new_context(
        user_agent=selected_ua,
        viewport=selected_viewport,
        # Additional stealth settings
        java_script_enabled=True,
        ignore_https_errors=True,
        # Randomize timezone
        timezone_id=random.choice(['America/New_York', 'America/Toronto', 'America/Vancouver']),
        # Random locale
        locale=random.choice(['en-US', 'en-CA']),
        # Permissions
        permissions=['geolocation']
    )
    
    print(f"🎭 Created context with UA: {selected_ua[:50]}...")
    print(f"📱 Viewport: {selected_viewport['width']}x{selected_viewport['height']}")
    
    return context

def human_like_delay(min_seconds=1, max_seconds=5):
    """Add random human-like delays"""
    delay = random.uniform(min_seconds, max_seconds)
    print(f"⏱️ Waiting {delay:.1f} seconds...")
    time.sleep(delay)

def simulate_human_behavior(page):
    """Simulate human browsing behavior"""
    print("🤖 Simulating human behavior...")
    
    # Random mouse movements
    page.mouse.move(random.randint(100, 800), random.randint(100, 600))
    time.sleep(random.uniform(0.5, 1.5))
    
    # Random scroll
    page.evaluate(f"window.scrollTo(0, {random.randint(0, 500)})")
    time.sleep(random.uniform(1, 2))
    
    # Move mouse again
    page.mouse.move(random.randint(200, 900), random.randint(200, 700))

def try_address_lookup_with_stealth(context, session_num):
    """Perform address lookup with stealth techniques"""
    page = context.new_page()
    
    try:
        print(f"\n🚀 Session {session_num}: Starting address lookup...")
        
        # Navigate with human-like behavior
        print("📍 Navigating to Bell Internet page...")
        page.goto("https://www.bell.ca/Bell_Internet")
        
        # Wait with randomization
        human_like_delay(2, 4)
        page.wait_for_load_state("networkidle")
        print("✅ Page loaded:", page.title())
        
        # Simulate human browsing
        simulate_human_behavior(page)
        human_like_delay(1, 3)
        
        # Try to find address input with multiple strategies
        print("🔍 Looking for address input fields...")
        
        # Strategy 1: By ID
        address_input = page.query_selector("#ValidationAddressHowtoBuyTopNav")
        if address_input:
            print("✅ Found address input by ID")
            
            # Human-like interaction
            address_input.scroll_into_view_if_needed()
            human_like_delay(0.5, 1.5)
            
            # Click with slight delay
            address_input.click()
            human_like_delay(0.5, 1)
            
            # Type slowly like a human
            address_input.fill("")
            time.sleep(0.3)
            
            # Type character by character with delays
            test_address = "186 Lindenshire"
            for char in test_address:
                address_input.type(char, delay=random.randint(80, 200))
            
            print(f"✅ Typed address: {test_address}")
            
            # Wait for autocomplete
            try:
                page.wait_for_selector(".pcaitem", timeout=10000)
                print("✅ Autocomplete popup appeared")
                
                # Random small delay before clicking
                human_like_delay(0.5, 1.5)
                page.click(".pcaitem.pcafirstitem")
                print("✅ Clicked first popup item")
                
                # Wait to see results
                human_like_delay(2, 4)
                
                return True
                
            except:
                print("❌ No autocomplete popup appeared")
                return False
                
        else:
            print("❌ Address input not found")
            return False
            
    except Exception as e:
        print(f"❌ Session {session_num} failed: {e}")
        return False
    finally:
        page.close()

def main():
    with sync_playwright() as p:
        # Launch browser with stealth settings
        browser = p.chromium.launch(
            headless=False,  # Set to True for production
            args=[
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        try:
            session_count = 0
            max_sessions = 5  # Try up to 5 sessions
            
            while session_count < max_sessions:
                session_count += 1
                
                # Create new stealth context for each session
                context = create_stealth_context(browser)
                
                try:
                    success = try_address_lookup_with_stealth(context, session_count)
                    
                    if success:
                        print(f"🎉 Session {session_count} completed successfully!")
                        # No break between successful sessions anymore
                    else:
                        print(f"⚠️ Session {session_count} had issues, rotating...")
                        human_like_delay(10, 20)  # Shorter delay on failure
                        
                except Exception as e:
                    print(f"💥 Session {session_count} crashed: {e}")
                    human_like_delay(15, 30)
                    
                finally:
                    # Always clean up context
                    context.close()
                    print(f"🧹 Session {session_count} context closed")
                    
        finally:
            print("🏁 All sessions completed. Press Enter to close browser...")
            input()
            browser.close()

if __name__ == "__main__":
    main()
