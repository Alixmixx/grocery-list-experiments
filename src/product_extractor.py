import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_products(html_content, num_products=10):
    """
    Pulls out product details from Coupang search results.
    
    Takes in HTML content and returns a list of products with their details
    like name, price, ratings, etc. Limits to specified number of products.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    
    product_cards = soup.select('li.search-product')
    product_cards = product_cards[:min(len(product_cards), num_products)]
    
    base_url = "https://www.coupang.com"
    
    for card in product_cards:
        product = {}
        
        product_id = card.get('id', '').replace('product_', '')
        if product_id:
            product['id'] = product_id
        
        name_elem = card.select_one('div.name')
        if name_elem:
            product['name'] = name_elem.text.strip()
        
        link_elem = card.select_one('a.search-product-link')
        if link_elem and link_elem.has_attr('href'):
            product['url'] = urljoin(base_url, link_elem['href'])
        
        price_elem = card.select_one('strong.price-value')
        if price_elem:
            product['price'] = price_elem.text.strip()
        
        original_price_elem = card.select_one('del.base-price')
        if original_price_elem:
            product['original_price'] = original_price_elem.text.strip()
        
        rating_elem = card.select_one('em.rating')
        if rating_elem:
            product['rating'] = rating_elem.text.strip()
        
        rating_count_elem = card.select_one('span.rating-total-count')
        if rating_count_elem:
            count_text = rating_count_elem.text.strip()
            product['rating_count'] = count_text.strip('()') if count_text else '0'
        
        img_elem = card.select_one('img.search-product-wrap-img')
        if img_elem and img_elem.has_attr('src'):
            product['image_url'] = img_elem['src']
        
        badges = []
        badge_elems = card.select('span.badge')
        for badge in badge_elems:
            badges.append(badge.text.strip())
        if badges:
            product['badges'] = badges
        
        products.append(product)
    
    return products

def save_products_to_json(products, filename):
    """
    Saves product data to a nicely formatted JSON file.
    
    Creates readable JSON with proper Korean character support.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(products)} products to {filename}")

def process_search_html(html_file_path, num_products=10):
    """
    Converts Coupang search HTML files into structured product data.
    
    Reads an HTML file, extracts product info, and saves it as JSON
    with the same name (but .json extension) in the same folder.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        products = extract_products(html_content, num_products)
        
        base_name = os.path.basename(html_file_path)
        output_name = base_name.replace('.html', '.json')
        output_path = os.path.join(os.path.dirname(html_file_path), output_name)
        
        save_products_to_json(products, output_path)
        
        return products
    
    except Exception as e:
        print(f"Error processing HTML file: {e}")
        return []

if __name__ == "__main__":
    import glob
    
    html_files = glob.glob("../output/*.html")
    
    if not html_files:
        print("No HTML files found in the output directory.")
    else:
        for html_file in html_files:
            print(f"Processing {html_file}...")
            products = process_search_html(html_file)
            print(f"Extracted {len(products)} products\n")