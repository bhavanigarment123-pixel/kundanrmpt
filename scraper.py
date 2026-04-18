import asyncio
import csv
import re
import time
from playwright.async_api import async_playwright

BRANDS = [
    "https://www.streakwave.com/engenius",
    "https://www.streakwave.com/fanvil",
    "https://www.streakwave.com/mikrotik",
    "https://www.streakwave.com/mimosa",
    "https://www.streakwave.com/netonix",
    "https://www.streakwave.com/readynet",
    "https://www.streakwave.com/rf-armor",
    "https://www.streakwave.com/rf-elements",
    "https://www.streakwave.com/shireen",
    "https://www.streakwave.com/teltonika",
    "https://www.streakwave.com/ubiquiti",
    "https://www.streakwave.com/yealink",
    "https://www.streakwave.com/uniview"
]

async def extract_products(page, brand_url):
    data = []
    seen = set()
    page_num = 1

    while True:
        url = f"{brand_url}?page={page_num}"
        print(f"Opening {url}")

        try:
            await page.goto(url, timeout=30000)
        except:
            print("❌ Blocked or timeout")
            break

        await page.wait_for_timeout(5000)

        content = await page.content()

        # ⚠️ Cloudflare detection
        if "Verify you are human" in content:
            print("⚠️ Blocked by Cloudflare — skipping this brand")
            break

        cards = await page.query_selector_all("div:has-text('$')")

        if not cards:
            break

        for card in cards:
            try:
                text = await card.inner_text()

                sku_match = re.search(r'\b[A-Z]{2,5}-[A-Z0-9\-]+\b', text)
                if not sku_match:
                    continue

                full_sku = sku_match.group()
                sku = full_sku.split("-", 1)[1]

                if sku in seen:
                    continue
                seen.add(sku)

                price_match = re.search(r"\$\d+[,\d]*\.?\d*", text)
                price = price_match.group() if price_match else ""

                ohio_match = re.search(r"Ohio\s*:\s*(\d+)", text)
                utah_match = re.search(r"Utah\s*:\s*(\d+)", text)

                ohio = int(ohio_match.group(1)) if ohio_match else 0
                utah = int(utah_match.group(1)) if utah_match else 0

                total = ohio + utah

                data.append([sku, price, ohio, utah, total])

            except:
                continue

        print(f"Collected so far: {len(data)}")
        page_num += 1

    return data


async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
    headless=True,
    args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled"
    ]
)

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        page = await context.new_page()

        all_data = []

        for brand in BRANDS:
            print(f"Scraping {brand}")
            data = await extract_products(page, brand)
            all_data.extend(data)

        filename = f"output_{int(time.time())}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["SKU", "Price", "Ohio", "Utah", "Total"])
            writer.writerows(all_data)

        await browser.close()

        return len(all_data)
