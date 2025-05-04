#!/usr/bin/env python3
"""
Coupang Product Search and Extraction Tool

This script searches for products on Coupang and extracts structured data.
"""
import os
import sys
import argparse
from coupang_search import initialize, search_item, save_search_html
from product_extractor import process_search_html

def search_and_extract(query, num_products=10, output_dir="../output"):
    """
    Performs a complete search and data extraction process.
    
    1. Initializes Coupang session
    2. Searches for the query
    3. Saves the HTML results
    4. Extracts product data to JSON
    
    Returns the path to the JSON file or None if any step fails.
    """
    print(f"Starting search for '{query}'")
    
    # Initialize session
    session = initialize()
    if not session:
        print("Failed to initialize session. Cannot continue.")
        return None
    
    # Search for product
    response = search_item(session, query)
    if not response:
        print(f"Failed to get search results for '{query}'.")
        return None
    
    # Save HTML results
    html_path = save_search_html(response, query, output_dir)
    if not html_path:
        print("Failed to save search results.")
        return None
    
    # Extract products from HTML to JSON
    products = process_search_html(html_path, num_products)
    if not products:
        print("No products extracted.")
        return None
    
    # Return the path to the JSON file (same as HTML but with .json extension)
    json_path = html_path.replace('.html', '.json')
    return json_path

def main():
    """
    Main function to parse arguments and run the search and extraction.
    """
    parser = argparse.ArgumentParser(description="Search Coupang and extract product data")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("-n", "--num-products", type=int, default=10, 
                        help="Number of products to extract (default: 10)")
    parser.add_argument("-o", "--output-dir", type=str, default="../output",
                        help="Output directory (default: ../output)")
    
    args = parser.parse_args()
    
    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run the search and extraction
    result = search_and_extract(args.query, args.num_products, args.output_dir)
    
    if result:
        print("\nSuccess! Product data extracted to:")
        print(result)
        return 0
    else:
        print("\nFailed to complete the search and extraction process.")
        return 1

if __name__ == "__main__":
    sys.exit(main())