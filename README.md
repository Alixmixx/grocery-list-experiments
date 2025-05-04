# Coupang Product Search and Extraction

A tool to search for products on Coupang and extract structured data.

## Features

- Handles Coupang's complex redirect chain to establish a session
- Searches for products based on query terms
- Extracts detailed product information including:
  - Product name, ID, and URL
  - Price and original price
  - Ratings and number of reviews
  - Product images
  - Special badges (free shipping, rocket delivery, etc.)

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

Search for products and extract data as JSON:

```
python src/main.py "search query" [options]
```

Options:
- `-n, --num-products`: Number of products to extract (default: 10)
- `-o, --output-dir`: Output directory (default: ../output)

Example:
```
python src/main.py "tomato 1kg" -n 20
```

### Using the Modules

You can also use the individual modules in your own scripts:

```python
from src.coupang_search import initialize, search_item, save_search_html
from src.product_extractor import process_search_html

# Initialize a session
session = initialize()

# Search for a product
response = search_item(session, "tomato 1kg")

# Save search results
html_path = save_search_html(response, "tomato 1kg")

# Extract product information
products = process_search_html(html_path, num_products=10)
```

## Output

The tool produces two files for each search:
1. An HTML file with the raw search results
2. A JSON file with the extracted product data

Files are saved to the `output` directory by default.

## Structure

- `src/coupang_search.py`: Functions for establishing a session and searching
- `src/product_extractor.py`: Functions for extracting product data from HTML
- `src/main.py`: Command-line interface to run the complete process