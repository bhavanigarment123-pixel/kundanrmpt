from fastapi import FastAPI
from scraper import run_scraper

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Scraper running"}

@app.get("/run")
async def run():
    print("🔥 /run endpoint triggered")

    try:
        count = await run_scraper()
        return {"scraped_products": count}
    except Exception as e:
        return {"error": str(e)}
