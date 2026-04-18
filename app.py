from fastapi import FastAPI
from scraper import run_scraper

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Scraper running"}

@app.get("/run")
async def run():
    count = await run_scraper()
    return {"message": f"Scraped {count} products"}