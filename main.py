from fastapi import FastAPI, HTTPException
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "YT backend running with fallback"}

@app.get("/get_stream")
def get_stream(videoId: str):
    # Method 1: YouTube Direct (with PO_TOKEN)
    ydl_opts = {
        "format": "bestaudio/best",
        "extractor_args": {"youtube": {
            "player_client": ["android", "web"],
            "po_token": ["web+MnjHnMDp0ZlqO8eggT9eb3zL6uzw5mlmDaXJb_Uo8LV098OD5HV3mI4isAKeJCuNuu2c9hOr4fqmZhYyNtMSZhfkZDN7lSyRZTA1_sLI78nK9hHCEboHswfV95bTB0ezSKLApCgSoYO17vIUl2cT-u3mrpprvQ5W-LE="]
        }},
        "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://youtube.com{videoId}", download=False)
            return {"url": info.get("url")}
    except Exception:
        # Method 2: Fallback to Invidious API (Agar YouTube block kare)
        try:
            res = requests.get(f"https://snopyta.org{videoId}")
            stream_url = res.json()['formatStreams'][0]['url']
            return {"url": stream_url}
        except:
            raise HTTPException(status_code=500, detail="Sare raaste band hain bhai!")
