from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import requests
import re
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PO_TOKEN = os.getenv("PO_TOKEN")  # Render se aayega

@app.get("/")
def home():
    return {"status": "YT backend running (secure version)"}

@app.get("/get_stream")
def get_stream(videoId: str):
    try:
        # STEP 1: Extract ID
        match = re.search(r"([a-zA-Z0-9_-]{11})", videoId)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid videoId")

        actual_id = match.group(1)
        video_url = f"https://www.youtube.com/watch?v={actual_id}"

        # STEP 2: yt-dlp config
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            }
        }

        # PO_TOKEN agar hai tab hi use karo
        if PO_TOKEN:
            ydl_opts["extractor_args"] = {
                "youtube": {
                    "player_client": ["android", "web"],
                    "po_token": [f"web+{PO_TOKEN}"]
                }
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                stream_url = info.get("url")
                if not stream_url:
                    raise Exception("No stream url")

                return {
                    "status": "success",
                    "source": "yt-dlp",
                    "url": stream_url,
                    "title": info.get("title")
                }

        except Exception as err:
            print("yt-dlp failed → fallback:", err)

            # STEP 3: Invidious fallback
            inv_url = f"https://inv.tux.pizza/api/v1/videos/{actual_id}"
            res = requests.get(inv_url, timeout=10)

            if res.status_code != 200:
                raise Exception("Invidious failed")

            data = res.json()

            formats = data.get("adaptiveFormats", []) + data.get("formatStreams", [])

            audio = [
                f for f in formats
                if "audio" in f.get("type", "") and f.get("url")
            ]

            if not audio:
                raise Exception("No audio stream")

            return {
                "status": "success",
                "source": "invidious",
                "url": audio[-1]["url"],
                "title": data.get("title")
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
