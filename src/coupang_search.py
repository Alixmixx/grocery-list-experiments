import requests
import os

def initialize():
    """
    Creates a browser-like session to interact with Coupang.
    
    Handles complex redirect chains and cookies to establish a valid session.
    Returns a session object that can be used for searches.
    """
    print("Attempting to initialize session...")
    session = requests.Session()

    from urllib.parse import urlparse, parse_qs, urlunparse

    initial_url = "https://link.coupang.com/re/SAGOOGLEPCHOME"
    initial_params = {
        "spec": "10304902",
        "lptag": "coupang",
        "network": "g",
        "gad_source": "1",
        "gbraid": "0AAAAAC3fSoqGUMwyvcgLOeYP1KiZRflKb",
        "gclid": "EAIaIQobChMI64b_oZyJjQMVQRB7Bx2ifSaVEAAYASAAEgIfM_D_BwE"
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host': 'link.coupang.com',
        'Referer': 'https://www.google.com/',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    }

    current_url = initial_url
    current_params = initial_params
    max_hops = 15

    try:
        for hop in range(max_hops):
            print(f"\nHop {hop+1}/{max_hops}: Requesting URL: {current_url}")

            response = session.get(
                current_url,
                params=current_params,
                headers=headers,
                timeout=15,
                allow_redirects=False
            )

            print(f"  Status Code: {response.status_code}")

            if response.is_redirect or response.is_permanent_redirect:
                location = response.headers.get('Location')
                if not location:
                    print("  ERROR: Redirect status but no Location header found.")
                    return None

                print(f"  Redirecting to: {location}")

                parsed_location = urlparse(location)

                current_url = location if parsed_location.scheme else urlunparse(urlparse(response.url)._replace(path=parsed_location.path, query=parsed_location.query, fragment=parsed_location.fragment))
                current_params = parse_qs(parsed_location.query)
                headers['Referer'] = response.url
                headers['Host'] = parsed_location.netloc if parsed_location.netloc else headers.get('Host')

            elif response.ok:
                print(f"\nSuccessfully reached final URL: {response.url}")
                print(f"Final Status Code: {response.status_code}")
                print("Session initialized with cookies.")
                return session

            else:
                print(f"  ERROR: Received non-redirect/non-success status: {response.status_code}")
                response.raise_for_status()
                return None

        print(f"\nERROR: Exceeded maximum manual hops ({max_hops}) without reaching a final page.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error during initialization: {e}")
        if isinstance(e, requests.exceptions.TooManyRedirects):
             print("  This error occurred even with manual redirect handling, check the printed hop details.")
        return None

def search_item(session, query):
    """
    Searches for products on Coupang.
    
    Takes an active session and search query, returns the HTML response
    containing search results that can be parsed for product info.
    """
    if not session:
        print("Error: Invalid session object provided.")
        return None
    if not query:
        print("Error: Search query cannot be empty.")
        return None

    search_url = "https://www.coupang.com/np/search"
    search_params = {
        "component": "",
        "q": query,
        "channel": "user"
    }

    referer_url = "https://www.coupang.com/"

    search_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host': 'www.coupang.com',
        'Referer': referer_url,
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    }

    print(f"\nSearching for: '{query}'")
    print(f"Referer: {referer_url}")

    try:
        response = session.get(
            search_url,
            params=search_params,
            headers=search_headers,
            timeout=15
        )
        response.raise_for_status()
        print(f"Search successful! Status Code: {response.status_code}")
        return response

    except requests.exceptions.RequestException as e:
        print(f"Error during search request: {e}")
        return None

def save_search_html(response, query, output_dir="../output"):
    """
    Saves search results HTML to a file.
    
    Creates a sanitized filename based on the search query.
    """
    if not response:
        print(f"No response to save.")
        return None
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Sanitize the query for filename
    safe_query = "".join(c if c.isalnum() else "_" for c in query).strip("_")
    filename = f"{output_dir}/coupang_search_{safe_query}.html"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved search results HTML to: {filename}")
        return filename
    except IOError as e:
        print(f"Error saving HTML file '{filename}': {e}")
        return None