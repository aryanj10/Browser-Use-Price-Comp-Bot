<p align="center"> <picture> <source media="(prefers-color-scheme: dark)" srcset="./static/browser-use-dark.png"> <source media="(prefers-color-scheme: light)" srcset="./static/browser-use.png"> <img alt="Browser Use Logo" src="./static/browser-use.png" width="full"> </picture> </p> <h1 align="center">Retail Price Comparison with Browser-Use 🤖</h1>
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

