from fastapi import FastAPI
from scraper import run_scraper
import subprocess

app = FastAPI()

# 🔥 Install browser at startup (IMPORTANT)
@app.on_event("startup")
async def startup_event():
    print("Installing Playwright browser...")
    subprocess.run(["playwright", "install", "chromium"])

@app.get("/")
def home():
    return {"status": "Scraper running"}

@app.get("/run")
async def run():
    try:
        count = await run_scraper()
        return {"scraped_products": count}
    except Exception as e:
        return {"error": str(e)}
