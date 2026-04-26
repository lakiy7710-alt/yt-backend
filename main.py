from fastapi import FastAPI, HTTPException
import yt_dlp
import requests
import re

app = FastAPI()

@app.get("/")
def home():
    return {"status": "YT backend running with Auto-Fixer"}

@app.get("/get_stream")
def get_stream(videoId: str):
    # AUTO-FIXER: Agar puri ID ya link aaye, ye sirf 11 digit ki ID nikal lega
    actual_id = videoId
    match = re.search(r"([a-zA-Z0-9_-]{11})", videoId)
    if match:
        actual_id = match.group(1)
    
    # Ab link ekdum perfect banega
    video_url = f"https://youtube.com{actual_id}"
    print(f"DEBUG: Playing URL -> {video_url}")

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "po_token": ["web+MnjHnMDp0ZlqO8eggT9eb3zL6uzw5mlmDaXJb_Uo8LV098OD5HV3mI4isAKeJCuNuu2c9hOr4fqmZhYyNtMSZhfkZDN7lSyRZTA1_sLI78nK9hHCEboHswfV95bTB0ezSKLApCgSoYO17vIUl2cT-u3mrpprvQ5W-LE="]
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return {"url": info.get("url")}
    except Exception as e:
        print(f"YT Direct failed, trying fallback: {e}")
        try:
            # Fallback to Invidious
            inv_url = f"https://tux.pizza{actual_id}"
            res = requests.get(inv_url, timeout=10)
            data = res.json()
            if 'formatStreams' in data and len(data['formatStreams']) > 0:
                return {"url": data['formatStreams'][-1]['url']}
            raise Exception("Invidious failed")
        except Exception:
            raise HTTPException(status_code=500, detail=f"Sare method fail: {str(e)}")
