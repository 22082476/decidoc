
import requests
from bs4 import BeautifulSoup
from datetime import date
from urllib.parse import urlparse

def get_metadata(url: str) -> dict:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string.strip() if soup.title else url
        
        # Try to find author or site name
        site_name = ""
        og_site_name = soup.find("meta", property="og:site_name")
        if og_site_name:
            site_name = og_site_name["content"]
        else:
            domain = urlparse(url).netloc
            site_name = domain.replace("www.", "")

        return {
            "title": title,
            "site_name": site_name,
            "url": url,
            "date": "n.d." # Date extraction is hard, defaulting to n.d.
        }
    except Exception as e:
        return {"url": url, "error": str(e)}

def format_apa(url: str) -> str:
    if not url.startswith("http"):
        return url
        
    meta = get_metadata(url)
    
    if "error" in meta:
        return f"[{url}]({url})"

    title = meta.get("title", url)
    site_name = meta.get("site_name", "")
    retrieved_date = date.today().strftime("%B %d, %Y")
    
    # Generic APA format for website:
    # Author/Site. (Date). Title. Retrieved [Date], from URL
    # Simplified for this context:
    # Site Name. (n.d.). *Title*. Retrieved from URL
    
    citation = ""
    if site_name:
        citation += f"{site_name}. "
    
    citation += "(n.d.). "
    citation += f"*{title}*. "
    citation += f"Retrieved from {url}"
    
    return citation
