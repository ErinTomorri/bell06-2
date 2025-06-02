import asyncio
import json
import time
from playwright.async_api import async_playwright
from urllib.parse import urlencode

class BellPlaywrightAutomation:
    def __init__(self):
        self.page = None
        self.context = None
        self.browser = None
        self.responses = []
        
    async def setup_browser(self, headless=False):
        """Setup browser with anti-detection measures"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with anti-detection options
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Toronto',
            permissions=['geolocation'],
            geolocation={'latitude': 43.6532, 'longitude': -79.3832}  # Toronto coordinates
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        # Add stealth scripts to avoid detection
        await self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        # Set up response monitoring
        self.page.on('response', self._handle_response)
        
    async def _handle_response(self, response):
        """Monitor network responses"""
        if any(endpoint in response.url for endpoint in [
            'CheckUsersProvince',
            'GetIndexOfSelectedAddressHtB', 
            'GetAddressFromCanadaPostHtB'
        ]):
            try:
                response_data = {
                    'url': response.url,
                    'status': response.status,
                    'headers': dict(response.headers),
                    'body': await response.text() if response.status == 200 else None
                }
                self.responses.append(response_data)
                print(f"✅ Captured response from {response.url}")
                print(f"   Status: {response.status}")
                if response_data['body']:
                    print(f"   Body: {response_data['body'][:200]}...")
            except Exception as e:
                print(f"❌ Error capturing response: {e}")
    
    async def navigate_to_bell_internet(self):
        """Navigate to Bell Internet page and wait for it to load"""
        print("🌐 Navigating to Bell Internet page...")
        
        try:
            # Navigate to the page
            await self.page.goto('https://www.bell.ca/Bell_Internet', 
                                wait_until='networkidle', 
                                timeout=30000)
            
            # Wait for page to be fully loaded
            await self.page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(3)  # Additional wait for JavaScript to initialize
            
            print("✅ Successfully loaded Bell Internet page")
            return True
            
        except Exception as e:
            print(f"❌ Error navigating to Bell Internet page: {e}")
            return False
    
    async def trigger_province_check(self):
        """Trigger the province check request"""
        print("🔍 Triggering province check...")
        
        try:
            # Look for elements that might trigger the province check
            # This could be a form submission, button click, or automatic trigger
            
            # Wait for any dynamic content to load
            await asyncio.sleep(2)
            
            # Try to find and interact with elements that might trigger the request
            # Check for address input fields or qualification buttons
            address_inputs = await self.page.query_selector_all('input[type="text"]')
            
            for input_elem in address_inputs:
                placeholder = await input_elem.get_attribute('placeholder')
                if placeholder and any(keyword in placeholder.lower() for keyword in ['address', 'postal', 'street']):
                    print(f"📝 Found address input with placeholder: {placeholder}")
                    # You can interact with this input if needed
                    break
            
            # Look for qualification or check availability buttons
            buttons = await self.page.query_selector_all('button, input[type="submit"], a[role="button"]')
            
            for button in buttons:
                text_content = await button.text_content()
                if text_content and any(keyword in text_content.lower() for keyword in 
                                      ['check', 'qualify', 'availability', 'find', 'search']):
                    print(f"🔘 Found potential trigger button: {text_content}")
                    # You can click this button if needed
                    break
            
            return True
            
        except Exception as e:
            print(f"❌ Error triggering province check: {e}")
            return False
    
    async def perform_address_qualification(self, address_data=None):
        """Perform address qualification with the captured network flow"""
        print("🏠 Performing address qualification...")
        
        if not address_data:
            address_data = {
                'street_number': '186',
                'street_name': 'Lindenshire',
                'street_type': 'Ave',
                'city': 'Maple',
                'province': 'ON',
                'postal_code': 'L6A 2X4'
            }
        
        try:
            # Method 1: Try to find and fill address form
            await self._try_address_form(address_data)
            
            # Method 2: Try to trigger requests programmatically
            await self._try_programmatic_requests(address_data)
            
            # Wait for responses
            await asyncio.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Error performing address qualification: {e}")
            return False
    
    async def _try_address_form(self, address_data):
        """Try to find and fill address form on the page"""
        print("📋 Looking for address form...")
        
        try:
            # Look for address input fields
            street_input = await self.page.query_selector('input[name*="street"], input[placeholder*="street"], input[id*="street"]')
            city_input = await self.page.query_selector('input[name*="city"], input[placeholder*="city"], input[id*="city"]')
            postal_input = await self.page.query_selector('input[name*="postal"], input[placeholder*="postal"], input[id*="postal"]')
            
            if street_input:
                full_address = f"{address_data['street_number']} {address_data['street_name']} {address_data['street_type']}"
                await street_input.fill(full_address)
                print(f"✅ Filled street address: {full_address}")
            
            if city_input:
                await city_input.fill(address_data['city'])
                print(f"✅ Filled city: {address_data['city']}")
            
            if postal_input:
                await postal_input.fill(address_data['postal_code'])
                print(f"✅ Filled postal code: {address_data['postal_code']}")
            
            # Look for submit button
            submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Check"), button:has-text("Search")')
            
            if submit_button:
                await submit_button.click()
                print("✅ Clicked submit button")
                await asyncio.sleep(3)
            
        except Exception as e:
            print(f"⚠️ Could not find/fill address form: {e}")
    
    async def _try_programmatic_requests(self, address_data):
        """Try to trigger the requests programmatically using JavaScript"""
        print("🔧 Trying programmatic approach...")
        
        try:
            # Execute JavaScript to make the requests that we observed
            result = await self.page.evaluate("""
                async () => {
                    try {
                        // First request: CheckUsersProvince
                        const provinceResponse = await fetch('/eshop/Qualification/CheckUsersProvince', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: 'Province=ON&PageHirarchyCode=INTERNET_WHY_BELL'
                        });
                        
                        console.log('Province check response:', provinceResponse.status);
                        
                        // Second request: GetIndexOfSelectedAddressHtB
                        const indexResponse = await fetch('/eshop/Qualification/GetIndexOfSelectedAddressHtB', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: 'LOB=DSL&isGigabitFibe=False&IsGigabitPresaleFlow=False&product='
                        });
                        
                        console.log('Index response:', indexResponse.status);
                        
                        // Third request: GetAddressFromCanadaPostHtB
                        const addressResponse = await fetch('/eshop/Qualification/GetAddressFromCanadaPostHtB', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: 'StreetNumber=186&StreetName=Lindenshire&StreetType=Ave&StreetPreDirection=&StreetPostDirection=&SubBuilding=&City=Maple&State=ON&PostalCode=L6A+2X4&id=&isBRF=true&captcha=&makeOneLmsRequest=true'
                        });
                        
                        console.log('Address response:', addressResponse.status);
                        
                        return {
                            province: provinceResponse.status,
                            index: indexResponse.status,
                            address: addressResponse.status
                        };
                        
                    } catch (error) {
                        console.error('Error making requests:', error);
                        return { error: error.message };
                    }
                }
            """)
            
            print(f"📊 JavaScript execution result: {result}")
            
        except Exception as e:
            print(f"⚠️ Programmatic approach failed: {e}")
    
    async def wait_for_results(self, timeout=30):
        """Wait for and collect results"""
        print(f"⏳ Waiting for results (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.responses:
                break
            await asyncio.sleep(1)
        
        return self.responses
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def run_full_automation(self, headless=False, address_data=None):
        """Run the complete automation flow"""
        print("🚀 Starting Bell Internet automation with Playwright...")
        
        try:
            # Setup browser
            await self.setup_browser(headless=headless)
            
            # Navigate to Bell Internet page
            if not await self.navigate_to_bell_internet():
                return None
            
            # Trigger province check
            await self.trigger_province_check()
            
            # Perform address qualification
            await self.perform_address_qualification(address_data)
            
            # Wait for results
            results = await self.wait_for_results()
            
            # Print results
            print("\n" + "="*60)
            print("📋 AUTOMATION RESULTS")
            print("="*60)
            
            if results:
                for i, response in enumerate(results, 1):
                    print(f"\n🔍 Response {i}:")
                    print(f"   URL: {response['url']}")
                    print(f"   Status: {response['status']}")
                    if response['body']:
                        print(f"   Body: {response['body']}")
                    else:
                        print("   Body: (empty or error)")
            else:
                print("❌ No responses captured. The website might be using additional protection.")
                print("💡 Try running with headless=False to see what's happening in the browser.")
            
            return results
            
        except Exception as e:
            print(f"❌ Automation failed: {e}")
            return None
        
        finally:
            await self.cleanup()

# Standalone functions for easy usage
async def run_bell_automation(headless=True, address_data=None):
    """Run Bell automation with default settings"""
    automation = BellPlaywrightAutomation()
    return await automation.run_full_automation(headless=headless, address_data=address_data)

async def run_bell_automation_visible():
    """Run Bell automation with visible browser for debugging"""
    return await run_bell_automation(headless=False)

# Main execution
if __name__ == "__main__":
    print("🎭 Bell Internet Automation with Playwright")
    print("=" * 50)
    
    # You can customize the address data here
    custom_address = {
        'street_number': '186',
        'street_name': 'Lindenshire', 
        'street_type': 'Ave',
        'city': 'Maple',
        'province': 'ON',
        'postal_code': 'L6A 2X4'
    }
    
    # Run automation
    # Set headless=False to see the browser in action
    results = asyncio.run(run_bell_automation(headless=False, address_data=custom_address))
    
    if results:
        print(f"\n✅ Automation completed successfully! Captured {len(results)} responses.")
    else:
        print("\n❌ Automation completed but no responses were captured.")
        print("💡 This might indicate that the website has additional protection measures.") 