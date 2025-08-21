<h1 align="center">Retail Price Comparison with Browser-Use 🤖</h1>
Compare products across Amazon and Walmart automatically using AI-driven browser automation. Made with Browser-Use.



## Features

- Automatically searches Amazon.com and Walmart.com for your product query.

- Picks the best organic match (avoiding sponsored listings).

- Extracts key product details:
    -  Title
    - Price (numeric)
    - Currency
    - URL
    - Rating (stars)
    - Number of reviews
    - Availability text
    - Shipped and sold by retailer (inferred)

- Compares prices and identifies the cheaper option with the price difference.

- Returns strict JSON output suitable for downstream processing.


## Installation

### Clone the repository:

```bash
git clone <repo-url> # update this
cd <folder>
```

### Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt
uvx playwright install chromium --with-deps --no-shell
```

### Add your API keys to a .env file:

```bash
GOOGLE_API_KEY=<your_google_api_key>
```

## Usage

### Run from command line:
```bash
python compare_prices.py "ipad air m3 11 inch 128 gb"
```

## Sample Output

```json
INFO     [Agent] ✅ Task completed successfully
{
  "query": "ipad air m3 11 inch 128 gb",
  "products": [
    {
      "source": "amazon",
      "title": "Apple 11-inch iPad Air (5th Generation):iPad Air (5th Gen) - with M1 chip, 10.9-inch Liquid Retina Display, 64GB, Wi-Fi 6, All-Day Battery Life - Space Gray",
      "price": 559.0,
      "currency": "USD",
      "url": "/Apple-11-inch-Liquid-Retina-Display/dp/B09V3J933W",
      "rating": 4.7,
      "reviews": 11000,
      "availability": "In stock",
      "shipped_and_sold_by_retailer": false
    },
    {
      "title": "2025 Apple 11-inch iPad Air M3, Built for Apple Intelligence, Wi-Fi 128GB - Space Gray",
      "price": 557.5,
      "currency": "USD",
      "url": "/ip/2025-Apple-11-inch-iPad-Air-M3-Built-for-Apple-Intelligence-Wi-Fi-128GB-Space-Gray/15450254481?classType=VARIANT&athbdg=L1103&from=/search",
      "rating": 4.5,
      "reviews": 296,
      "availability": "Free shipping, arrives in 3+ days",
      "shipped_and_sold_by_retailer": false
    }
  ],
  "cheaper_source": "walmart",
  "price_diff": 1.5
}
```

## How It Works

- Launches a stealth-enabled browser session via Browser-Use.

- Visits Amazon and Walmart, searches the product query, and opens the top product page.

- Extracts all required fields and normalizes prices.

- Returns a structured JSON response highlighting the cheaper source.

## Customization

- Modify build_task(query) to add more product sources or additional fields.

- Adjust LLM settings in ChatGoogle() or switch to another provider.

- Can integrate with MCP servers to extend agent capabilities.

## References & Examples

- Browser-Use GitHub: https://github.com/gregpr07/browser-use

- Documentation: https://docs.browser-use.com

- Example Prompts: Check the examples/ folder for tasks like shopping, job applications, and web automation.

