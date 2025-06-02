from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set headless=True to hide browser
    context = browser.new_context()
    page = context.new_page()

    # Go to Bell's address lookup page
    page.goto("https://www.bell.ca/Bell_Internet")

    # Wait until page loads completely
    page.wait_for_load_state("networkidle")
    print("Page loaded:", page.title())

    # Wait a bit more for any dynamic content to load
    page.wait_for_timeout(3000)
    print("Waited 3 seconds for dynamic content")

    # Try to find and interact with the address input field with better debugging:
    
    # First, let's see what address input fields are available
    print("🔍 Looking for address input fields...")
    
    # Check if the specific ID exists
    address_input = page.query_selector("#ValidationAddressHowtoBuyTopNav")
    if address_input:
        print("✅ Found address input by ID")
        try:
            # Scroll to the element to make sure it's visible
            address_input.scroll_into_view_if_needed()
            print("✅ Scrolled to address input")
            
            # Click on the input field
            address_input.click()
            print("✅ Clicked address input")
            
            # Clear any existing text and type new address
            address_input.fill("")
            address_input.type("186 Lindenshire", delay=100)
            print("✅ Typed address: 186 Lindenshire")
            
            # Wait for autocomplete popup
            try:
                page.wait_for_selector(".pcaitem", timeout=10000)
                print("✅ Autocomplete popup appeared")
                
                # Click the first popup item
                page.click(".pcaitem.pcafirstitem")
                print("✅ Clicked first popup item")
                
            except:
                print("❌ No autocomplete popup appeared")
                
        except Exception as e:
            print(f"❌ Error interacting with address input: {e}")
    else:
        print("❌ Address input with ID not found, trying other methods...")
        
        # Try to find any input with placeholder "Enter your address"
        placeholder_input = page.query_selector("input[placeholder*='address' i]")
        if placeholder_input:
            print("✅ Found address input by placeholder")
            try:
                placeholder_input.scroll_into_view_if_needed()
                placeholder_input.click()
                placeholder_input.fill("186 Lindenshire")
                print("✅ Used placeholder method")
            except Exception as e:
                print(f"❌ Placeholder method failed: {e}")
        else:
            print("❌ No address input found by placeholder either")
            
            # List all input fields for debugging
            all_inputs = page.query_selector_all("input")
            print(f"🔍 Found {len(all_inputs)} input fields on the page:")
            for i, inp in enumerate(all_inputs):
                try:
                    input_id = inp.get_attribute("id") or "no-id"
                    input_placeholder = inp.get_attribute("placeholder") or "no-placeholder"
                    input_name = inp.get_attribute("name") or "no-name"
                    input_type = inp.get_attribute("type") or "no-type"
                    print(f"  Input {i+1}: id='{input_id}', placeholder='{input_placeholder}', name='{input_name}', type='{input_type}'")
                except:
                    print(f"  Input {i+1}: Could not read attributes")

    # Keep browser open to see the result
    input("Press Enter to close browser...")

    browser.close()
