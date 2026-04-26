from fastapi import FastAPI, HTTPException
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "YT backend running with fallback"}

@app.get("/get_stream")
def get_stream(videoId: str):
    # BILKUL AISE HI LIKHNA: Beach mein /watch?v= hona zaroori hai
    video_url = f"https://youtube.com{videoId}"
    
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
        print(f"YT Direct failed: {e}")
        try:
            # Invidious fallback ka sahi link
            inv_url = f"https://tux.pizza{videoId}"
            res = requests.get(inv_url, timeout=10)
            data = res.json()
            if 'formatStreams' in data and len(data['formatStreams']) > 0:
                return {"url": data['formatStreams'][-1]['url']}
            raise Exception("Invidious failed")
        except Exception:
            raise HTTPException(status_code=500, detail=f"Sare method fail ho gaye: {str(e)}")
