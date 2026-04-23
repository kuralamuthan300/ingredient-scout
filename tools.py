from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import trafilatura
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def scrape_website(url: str) -> str:
    """
    Scrapes the provided URL using a headless browser with stealth settings.
    
    Args:
        url (str): The web address to scrape.
        
    Returns:
        str: The extracted text content (limited to first 4000 characters).
    """

    try :

        with Stealth().use_sync(sync_playwright()) as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            geolocation={"latitude": 12.905325, "longitude": 77.67983},
            permissions=["geolocation"],
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-IN,en;q=0.9",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

            page = context.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()

        text = trafilatura.extract(html, include_tables=True, include_links=False)
        if text:
            print(f"Scraped {len(text)} characters from {url}")
            return json.dumps({"result": str(text)})
    except Exception as e:
        return json.dumps({"error": str(e)})    

def get_product_details_blinkit(arg: str) -> str:
    """
    Searches for an item on Blinkit and returns product details.
    
    Args:
        arg (str): The name of the item to search for (e.g., 'onion').
        
    Returns:
        str: Scraped text content from the Blinkit search results page.
    """
    return scrape_website(f"https://blinkit.com/s/?q={arg.replace(' ', '+')}")

def get_product_details_zepto(arg: str) -> str:
    """
    Searches for an item on Zepto and returns product details.
    
    Args:
        arg (str): The name of the item to search for.
        
    Returns:
        str: Scraped text content from the Zepto search results page.
    """
    return scrape_website(f"https://www.zepto.com/search?query={arg.replace(' ', '+')}")

def get_product_details_bigbasket(arg: str) -> str:
    """
    Searches for an item on BigBasket and returns product details.
    
    Args:
        arg (str): The name of the item to search for.
        
    Returns:
        str: Scraped text content from the BigBasket search results page.
    """
    return scrape_website(f"https://www.bigbasket.com/ps/?q={arg.replace(' ', '+')}&nc=as")

def get_more_info_from_user(query: str) -> str:
    """
    If agent want to ask any clarification question to the user, then use this tool.
    
    Args:
        query (str): The question to ask the user.
        
    Returns:
        str: The response from the user.
    """
    return json.dumps({"result": str(input(query))})


def send_gmail(recipient: str, subject: str, body: str) -> str:
    print('SEND GMAIL STARTED')
    sender_email = os.getenv("GMAIL_UNAME") 
    app_password = os.getenv("GMAIL_PASS") 

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Gmail SMTP server settings
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        print('MAIL SENT SUCCESSFULLY')
        return json.dumps({"result": "Email sent successfully!"})
    except Exception as e:
        print(f"EMAIL SENDING FAILED {e}")
        return json.dumps({"result": f"Failed to send email: {e}"})

# Register tools in a dictionary
tools = {
    "get_product_details_blinkit": get_product_details_blinkit,
    "get_product_details_zepto": get_product_details_zepto,
    "get_product_details_bigbasket": get_product_details_bigbasket,
    "get_more_info_from_user": get_more_info_from_user,
    "send_gmail": send_gmail
}

if __name__ == "__main__":
    # Running searches one by one (sequential)
    # print("--- Searching Zepto ---")
    # print(get_product_details_zepto("onion"))
    
    # print("\n\n--- Searching Blinkit ---")
    # print(get_product_details_blinkit("onion"))
    
    # print("\n\n--- Searching BigBasket ---")
    # print(get_product_details_bigbasket("onion"))
    print(get_more_info_from_user("What is your name?"))