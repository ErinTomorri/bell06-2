import requests
import time
import json
import random
import re
from urllib.parse import urlencode, urlparse
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ComprehensiveBellAutomation:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.csrf_token = None
        self.session_data = {}
        
        # More realistic headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
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
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"⏱️  Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def extract_page_data(self, html_content):
        """Extract important data from the page including tokens and form data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for CSRF tokens
            csrf_patterns = [
                ('input[name="__RequestVerificationToken"]', 'value'),
                ('input[name="_token"]', 'value'),
                ('meta[name="csrf-token"]', 'content'),
                ('meta[name="_token"]', 'content')
            ]
            
            for selector, attr in csrf_patterns:
                element = soup.select_one(selector)
                if element and element.get(attr):
                    self.csrf_token = element.get(attr)
                    print(f"🔑 Found CSRF token: {self.csrf_token[:20]}...")
                    break
            
            # Look for JavaScript variables that might contain session data
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Look for common patterns
                    patterns = [
                        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                        r'window\.appData\s*=\s*({.*?});',
                        r'var\s+sessionData\s*=\s*({.*?});',
                        r'window\.config\s*=\s*({.*?});'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, script.string, re.DOTALL)
                        if match:
                            try:
                                data = json.loads(match.group(1))
                                self.session_data.update(data)
                                print(f"📊 Found session data: {list(data.keys())}")
                            except:
                                pass
            
            # Look for form data
            forms = soup.find_all('form')
            for form in forms:
                form_data = {}
                inputs = form.find_all('input')
                for inp in inputs:
                    name = inp.get('name')
                    value = inp.get('value', '')
                    if name:
                        form_data[name] = value
                
                if form_data:
                    print(f"📝 Found form data: {list(form_data.keys())}")
                    self.session_data.update(form_data)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error extracting page data: {e}")
            return False
    
    def get_initial_page(self):
        """Visit the main page and extract necessary data"""
        print("🌐 Getting initial page...")
        try:
            response = self.session.get('https://www.bell.ca/Bell_Internet', timeout=30)
            print(f"📄 Initial page status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Successfully loaded initial page")
                
                # Extract important data from the page
                self.extract_page_data(response.text)
                
                # Save cookies for debugging
                print(f"🍪 Cookies received: {len(self.session.cookies)} cookies")
                for cookie in self.session.cookies:
                    print(f"   - {cookie.name}: {cookie.value[:20]}...")
                
                self.random_delay(2, 4)
                return True
            else:
                print(f"❌ Failed to load initial page: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting initial page: {e}")
            return False
    
    def inspect_network_requests(self):
        """Try to understand what requests the browser makes"""
        print("🔍 Inspecting potential network requests...")
        
        # Common endpoints to check
        endpoints_to_check = [
            '/eshop/Qualification/GetIndexOfSelectedAddressHtB',
            '/api/qualification',
            '/eshop/api/qualification',
            '/Bell_Internet/api/qualification',
            '/qualification/check',
            '/eshop/qualification/validate'
        ]
        
        for endpoint in endpoints_to_check:
            try:
                url = f"https://www.bell.ca{endpoint}"
                # Try GET first
                response = self.session.get(url, timeout=10)
                if response.status_code not in [404, 403]:
                    print(f"📡 GET {endpoint}: {response.status_code} - {len(response.text)} bytes")
                    if response.text and len(response.text) > 10:
                        print(f"   Content preview: {response.text[:100]}...")
                
                # Try OPTIONS to see what methods are allowed
                response = self.session.options(url, timeout=10)
                if response.status_code == 200:
                    allowed_methods = response.headers.get('Allow', '')
                    print(f"🔧 OPTIONS {endpoint}: {allowed_methods}")
                    
            except:
                pass
    
    def make_qualification_request_v1(self):
        """Original approach with improvements"""
        print("🚀 Making qualification request (v1)...")
        
        # Update headers for AJAX
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
        
        # Add CSRF token if available
        if self.csrf_token:
            data['__RequestVerificationToken'] = self.csrf_token
        
        # Add any session data we found
        data.update(self.session_data)
        
        print(f"📤 Sending data: {data}")
        
        try:
            response = self.session.post(
                'https://www.bell.ca/eshop/Qualification/GetIndexOfSelectedAddressHtB',
                data=data,
                timeout=30
            )
            
            return self.analyze_response(response, "v1")
            
        except Exception as e:
            print(f"❌ Error in v1 request: {e}")
            return None
    
    def make_qualification_request_v2(self):
        """Try with JSON payload"""
        print("🚀 Making qualification request (v2 - JSON)...")
        
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.bell.ca/Bell_Internet',
            'Origin': 'https://www.bell.ca'
        })
        
        data = {
            'LOB': 'DSL',
            'isGigabitFibe': False,
            'IsGigabitPresaleFlow': False,
            'product': '',
        }
        
        if self.csrf_token:
            data['__RequestVerificationToken'] = self.csrf_token
        
        print(f"📤 Sending JSON: {data}")
        
        try:
            response = self.session.post(
                'https://www.bell.ca/eshop/Qualification/GetIndexOfSelectedAddressHtB',
                json=data,
                timeout=30
            )
            
            return self.analyze_response(response, "v2")
            
        except Exception as e:
            print(f"❌ Error in v2 request: {e}")
            return None
    
    def make_qualification_request_v3(self):
        """Try with additional parameters"""
        print("🚀 Making qualification request (v3 - Extended)...")
        
        self.session.headers.update({
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.bell.ca/Bell_Internet',
            'Origin': 'https://www.bell.ca'
        })
        
        # Try with more parameters that might be expected
        data = {
            'LOB': 'DSL',
            'isGigabitFibe': 'False',
            'IsGigabitPresaleFlow': 'False',
            'product': '',
            'province': 'ON',
            'language': 'en',
            'region': 'ON',
            'addressId': '',
            'postalCode': '',
            'streetNumber': '',
            'streetName': '',
            'city': '',
            'unitNumber': ''
        }
        
        if self.csrf_token:
            data['__RequestVerificationToken'] = self.csrf_token
        
        print(f"📤 Sending extended data: {data}")
        
        try:
            response = self.session.post(
                'https://www.bell.ca/eshop/Qualification/GetIndexOfSelectedAddressHtB',
                data=data,
                timeout=30
            )
            
            return self.analyze_response(response, "v3")
            
        except Exception as e:
            print(f"❌ Error in v3 request: {e}")
            return None
    
    def analyze_response(self, response, version):
        """Analyze and display response details"""
        print(f"\n📊 Response Analysis ({version}):")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Content-Length: {len(response.text)}")
        
        if response.text:
            print(f"   Content preview: {response.text[:200]}...")
            
            # Check for common patterns
            if 'error' in response.text.lower():
                print("⚠️  Response contains 'error'")
            if 'success' in response.text.lower():
                print("✅ Response contains 'success'")
            if 'blocked' in response.text.lower() or 'denied' in response.text.lower():
                print("🚫 Response indicates blocking")
            if 'captcha' in response.text.lower():
                print("🤖 CAPTCHA detected")
            
            # Try to parse as JSON
            try:
                json_data = response.json()
                print(f"📄 JSON Response: {json.dumps(json_data, indent=2)}")
                return json_data
            except:
                print("📄 Response is not valid JSON")
        else:
            print("📄 Empty response body")
        
        return response
    
    def run(self):
        """Main execution flow"""
        print("🎯 Starting Comprehensive Bell Automation")
        print("=" * 50)
        
        # Step 1: Get initial page and extract data
        if not self.get_initial_page():
            print("❌ Failed to get initial page")
            return
        
        # Step 2: Inspect network possibilities
        self.inspect_network_requests()
        
        # Step 3: Try different request approaches
        approaches = [
            self.make_qualification_request_v1,
            self.make_qualification_request_v2,
            self.make_qualification_request_v3
        ]
        
        for i, approach in enumerate(approaches, 1):
            print(f"\n{'='*20} Approach {i} {'='*20}")
            try:
                result = approach()
                if result and hasattr(result, 'status_code') and result.status_code == 200:
                    if hasattr(result, 'text') and result.text.strip():
                        print(f"✅ Approach {i} got non-empty response!")
                        break
                    else:
                        print(f"⚠️  Approach {i} got empty response")
                else:
                    print(f"❌ Approach {i} failed")
            except Exception as e:
                print(f"❌ Approach {i} error: {e}")
            
            # Small delay between approaches
            if i < len(approaches):
                self.random_delay(1, 2)
        
        print("\n" + "=" * 50)
        print("🏁 Analysis complete!")

def main():
    automation = ComprehensiveBellAutomation()
    automation.run()

if __name__ == "__main__":
    main() 