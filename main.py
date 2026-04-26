from fastapi import FastAPI, HTTPException
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "YT backend running with fallback"}

@app.get("/get_stream")
def get_stream(videoId: str):
    # Method 1: YouTube Direct with PO_TOKEN
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
            info = ydl.extract_info(f"https://youtube.com{videoId}", download=False)
            return {"url": info.get("url")}
    except Exception as e:
        print(f"YT Direct failed: {e}")
        # Method 2: Fallback to Invidious API
        try:
            # Hum ek public Invidious instance use kar rahe hain
            res = requests.get(f"https://tux.pizza{videoId}", timeout=10)
            data = res.json()
            # Sabse badhiya format uthao
            if 'formatStreams' in data and len(data['formatStreams']) > 0:
                return {"url": data['formatStreams'][-1]['url']}
            elif 'adaptiveFormats' in data:
                # Audio only format dhoondo
                audio_only = [f for f in data['adaptiveFormats'] if 'audio' in f.get('type', '')]
                if audio_only:
                    return {"url": audio_only[0]['url']}
            raise Exception("Invidious also failed")
        except Exception as inv_e:
            raise HTTPException(status_code=500, detail=f"All methods failed. YT error: {str(e)}")
