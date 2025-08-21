import os, asyncio, sys, json, re
from typing import List, Optional, Any
from pydantic import BaseModel
from browser_use import Agent, Controller, BrowserSession
from browser_use.llm import ChatGoogle
from dotenv import load_dotenv
from browser_use.browser import BrowserProfile
from typing import get_type_hints

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# ----- Structured output we want back -----
class Product(BaseModel):
    source: str                 # "amazon" or "walmart"
    title: str
    price: float
    currency: str = "USD"
    url: Optional[str] = None   # <- change here
    rating: Optional[float] = None
    reviews: Optional[int] = None
    availability: Optional[str] = None
    shipped_and_sold_by_retailer: Optional[bool] = None

def normalize_nulls(obj: dict, model_class):
    """
    Recursively replace None/null values with safe defaults based on Pydantic type hints.
    """
    hints = get_type_hints(model_class)

    for key, typ in hints.items():
        if key not in obj:
            continue
        val = obj[key]

        # If value is a dict and the field is a BaseModel, recurse
        if isinstance(val, dict) and hasattr(typ, "__fields__"):
            normalize_nulls(val, typ)
        # If value is a list of BaseModels, recurse on each
        elif isinstance(val, list) and hasattr(typ, "__args__"):
            inner_type = typ.__args__[0]
            if hasattr(inner_type, "__fields__"):
                for item in val:
                    normalize_nulls(item, inner_type)
        else:
            # Replace None with default
            if val is None:
                if typ == str or getattr(typ, "__origin__", None) is Optional:
                    obj[key] = ""
                elif typ == float or typ == Optional[float]:
                    obj[key] = None
                elif typ == int or typ == Optional[int]:
                    obj[key] = None
                elif typ == bool or typ == Optional[bool]:
                    obj[key] = None

class CompareResult(BaseModel):
    query: str
    products: List[Product]
    cheaper_source: Optional[str] = None
    price_diff: Optional[float] = None

def build_task(query: str) -> str:
    return f"""
You are comparing retail prices for: "{query}".

Rules:
- Work ONLY on amazon.com and walmart.com. Use EACH site's search box (do NOT use Google).
- Pick the best organic match (avoid obvious Sponsored items).
- Prefer sold-by-Amazon / sold-or-fulfilled-by-Walmart when possible.
- Extract fields: title, numeric price, rating (stars), number of reviews, availability text, canonical URL.
- If you can infer it, set shipped_and_sold_by_retailer true/false.
IMPORTANT:
- Return ONLY **VALID JSON** matching this exact structure, nothing else:
{{
  "query": "...",
  "products": [
    {{
      "source":"amazon",
      "title":"...",
      "price":129.99,
      "currency":"USD",
      "url":"...",
      "rating":4.8,
      "reviews":12345,
      "availability":"In stock",
      "shipped_and_sold_by_retailer":true
    }},
    {{
      "source":"walmart",
      "title":"...",
      "price":...,
      "currency":"USD",
      "url":"...",
      "rating":...,
      "reviews":...,
      "availability":"...",
      "shipped_and_sold_by_retailer":false
    }}
  ]
}}

- Do NOT add any explanations, prose, or labels.
- Do not echo the query in text.
- Call "done" with JSON only when finished.

Steps:
1) Go to https://www.amazon.com, search the query, open the best match product page. Extract fields.
2) Go to https://www.walmart.com, search the query, open the best match product page. Extract fields.
3) Return final JSON that includes both products in the order visited.
"""

def _extract_first_json(text: str) -> Any | None:
    """
    Returns a parsed JSON object if one is found inside `text`, else None.
    Uses a simple brace-matching scan to capture the first top-level JSON object.
    """
    # Try a fast path: starts with '{' and ends with '}' (trim whitespace)
    s = text.strip()
    if s.startswith("{") and s.endswith("}"):
        try:
            return json.loads(s)
        except Exception:
            pass

    # General path: find first '{' and match braces
    start = s.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                candidate = s[start:i+1]
                try:
                    return json.loads(candidate)
                except Exception:
                    # sometimes there is trailing junk after numbers like $99.99; we'll clean price later
                    return None
    return None

def _coerce_price(v):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        # strip $ and commas; keep dot
        cleaned = re.sub(r"[^0-9.]", "", v)
        return float(cleaned) if cleaned else None
    return None

async def main(query: str):
    controller = Controller()  # don't enforce schema at the LLM level

    profile = BrowserProfile(
        stealth=True,
        allowed_domains=[
            "https://www.amazon.com", "https://www.walmart.com",
            "amazon.com", "walmart.com"
        ],
        locale="en-US",
        timezone_id="America/New_York",
    )
    session = BrowserSession(browser_profile=profile)

    llm = ChatGoogle(model="gemini-2.5-pro", temperature=0.0)
    agent = Agent(task=build_task(query), llm=llm, controller=controller, browser_session=session)

    history = await agent.run()
    final_text = history.final_result()
    
    if not final_text:
        print("No result")
        return

    obj = _extract_first_json(final_text)
    if obj is None:
        print("No JSON found in agent output:")
        print(final_text)
        return

    # Coerce price fields to float if they came as strings like "$99.99"
    try:
        for p in obj.get("products", []):
            p["price"] = _coerce_price(p.get("price"))
    except Exception:
        pass

    normalize_nulls(obj, CompareResult)
    parsed = CompareResult.model_validate(obj)

    # Enrich
    if len(parsed.products) >= 2 and all(p.price is not None for p in parsed.products[:2]):
        a, b = parsed.products[0], parsed.products[1]
        if a.price <= b.price:
            parsed.cheaper_source = a.source
            parsed.price_diff = round(b.price - a.price, 2)
        else:
            parsed.cheaper_source = b.source
            parsed.price_diff = round(a.price - b.price, 2)

    print(parsed.model_dump_json(indent=2))

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "ipad air m3 11 inch 128 gb"
    asyncio.run(main(q))
