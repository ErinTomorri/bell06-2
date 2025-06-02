import requests
import time
import json
import random
from urllib.parse import urlencode
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AdvancedBellAutomation:
    def __init__(self, use_proxy=False, proxy_list=None):
        self.session = requests.Session()
        self.session.verify = False
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        
        # Randomize user agents
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        
        self.setup_session()
    
    def setup_session(self):
        """Setup session with random user agent and proxy if available"""
        user_agent = random.choice(self.user_agents)
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # Set proxy if available
        if self.use_proxy and self.proxy_list:
            proxy = random.choice(self.proxy_list)
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }
            print(f"Using proxy: {proxy}")
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def get_initial_page(self):
        """Visit the main page to establish session and get fresh cookies"""
        print("Getting initial page...")
        try:
            response = self.session.get('https://www.bell.ca/Bell_Internet', timeout=30)
            print(f"Initial page status: {response.status_code}")
            
            if response.status_code == 200:
                print("Successfully loaded initial page")
                self.random_delay(2, 4)
                return True
            else:
                print(f"Failed to load initial page: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error getting initial page: {e}")
            return False
    
    def extract_csrf_token(self, html_content):
        """Extract CSRF token or other required tokens from HTML"""
        # Look for common CSRF token patterns
        import re
        
        patterns = [
            r'name="__RequestVerificationToken"[^>]*value="([^"]*)"',
            r'name="_token"[^>]*value="([^"]*)"',
            r'"csrf_token":"([^"]*)"',
            r'"_token":"([^"]*)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                token = match.group(1)
                print(f"Found token: {token[:20]}...")
                return token
        
        return None
    
    def make_qualification_request(self, csrf_token=None):
        """Make the qualification request with proper headers and tokens"""
        
        # Update headers for the AJAX request
        self.session.headers.update({
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Referer': 'https://www.bell.ca/Bell_Internet',
            'Origin': 'https://www.bell.ca'
        })
        
        data = {
            'LOB': 'DSL',
            'isGigabitFibe': 'False',
            'IsGigabitPresaleFlow': 'False',
            'product': '',
        }
        
        # Add CSRF token if found
        if csrf_token:
            data['__RequestVerificationToken'] = csrf_token
        
        print("Making qualification request...")
        try:
            response = self.session.post(
                'https://www.bell.ca/eshop/Qualification/GetIndexOfSelectedAddressHtB',
                data=data,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            # Check for common error indicators
            if 'blocked' in response.text.lower() or 'denied' in response.text.lower():
                print("⚠️  Request appears to be blocked")
            
            if 'captcha' in response.text.lower():
                print("⚠️  CAPTCHA detected")
            
            print(f"Response content: {response.text}")
            return response
            
        except Exception as e:
            print(f"Error making request: {e}")
            return None
    
    def retry_with_different_approach(self):
        """Try different approaches if the first one fails"""
        approaches = [
            self.approach_with_fresh_session,
            self.approach_with_different_endpoint,
            self.approach_with_minimal_headers
        ]
        
        for i, approach in enumerate(approaches, 1):
            print(f"\n--- Trying approach {i} ---")
            try:
                result = approach()
                if result and result.status_code == 200:
                    return result
            except Exception as e:
                print(f"Approach {i} failed: {e}")
                continue
        
        return None
    
    def approach_with_fresh_session(self):
        """Create a completely fresh session"""
        print("Creating fresh session...")
        self.session.close()
        self.session = requests.Session()
        self.session.verify = False
        self.setup_session()
        
        if self.get_initial_page():
            return self.make_qualification_request()
        return None
    
    def approach_with_different_endpoint(self):
        """Try a slightly different endpoint or method"""
        print("Trying alternative endpoint...")
        # Sometimes there are multiple endpoints for the same functionality
        alternative_endpoints = [
            'https://www.bell.ca/eshop/Qualification/GetIndexOfSelectedAddressHtB',
            'https://www.bell.ca/api/qualification/address',
            'https://www.bell.ca/eshop/api/qualification'
        ]
        
        for endpoint in alternative_endpoints:
            try:
                response = self.session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    print(f"Alternative endpoint works: {endpoint}")
                    return response
            except:
                continue
        return None
    
    def approach_with_minimal_headers(self):
        """Try with minimal headers to avoid detection"""
        print("Trying with minimal headers...")
        
        # Create a new session with minimal headers
        minimal_session = requests.Session()
        minimal_session.verify = False
        minimal_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        try:
            response = minimal_session.post(
                'https://www.bell.ca/eshop/Qualification/GetIndexOfSelectedAddressHtB',
                data={
                    'LOB': 'DSL',
                    'isGigabitFibe': 'False',
                    'IsGigabitPresaleFlow': 'False',
                    'product': '',
                },
                timeout=30
            )
            return response
        except Exception as e:
            print(f"Minimal headers approach failed: {e}")
            return None
    
    def run(self):
        """Main execution flow with multiple fallback strategies"""
        print("🚀 Starting Bell automation with advanced anti-bot evasion...")
        
        # Step 1: Get initial page to establish session
        if not self.get_initial_page():
            print("❌ Failed to get initial page, trying alternative approaches...")
            response = self.retry_with_different_approach()
            if not response:
                print("❌ All approaches failed")
                return
        else:
            # Step 2: Make the qualification request
            response = self.make_qualification_request()
            
            # If first attempt fails, try alternatives
            if not response or response.status_code != 200:
                print("❌ First attempt failed, trying alternatives...")
                response = self.retry_with_different_approach()
        
        # Process the response
        if response:
            self.process_response(response)
        else:
            print("❌ All attempts failed")
    
    def process_response(self, response):
        """Process and analyze the response"""
        print(f"\n✅ Got response with status: {response.status_code}")
        
        try:
            # Try to parse as JSON
            json_response = response.json()
            print("📄 JSON Response:")
            print(json.dumps(json_response, indent=2))
            
            # Analyze the response
            if 'error' in json_response:
                print(f"⚠️  API returned error: {json_response['error']}")
            elif 'success' in json_response:
                print("✅ Request appears successful")
            
        except json.JSONDecodeError:
            print("📄 Response is not JSON, raw content:")
            print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
            
            # Check for common blocking patterns
            if any(pattern in response.text.lower() for pattern in ['blocked', 'denied', 'forbidden', 'captcha']):
                print("⚠️  Response indicates request was blocked")
            elif 'bell' in response.text.lower() and len(response.text) > 100:
                print("✅ Got substantial response from Bell")

def main():
    """Main function with configuration options"""
    print("Bell Canada Automation Tool")
    print("=" * 40)
    
    # Configuration
    use_proxy = False  # Set to True if you have proxies
    proxy_list = [
        # Add your proxy list here if needed
        # 'http://proxy1:port',
        # 'http://proxy2:port',
    ]
    
    # Create and run automation
    automation = AdvancedBellAutomation(use_proxy=use_proxy, proxy_list=proxy_list)
    automation.run()
    
    print("\n" + "=" * 40)
    print("💡 Tips for better success:")
    print("1. Use residential proxies if available")
    print("2. Add random delays between requests")
    print("3. Consider using Selenium for JavaScript-heavy sites")
    print("4. Monitor for CAPTCHA challenges")
    print("5. Respect rate limits and terms of service")

if __name__ == "__main__":
    main() 