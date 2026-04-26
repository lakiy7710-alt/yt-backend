from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import requests
import re
import os

PO_TOKEN = os.getenv("PO_TOKEN")
VISITOR_DATA = os.getenv("VISITOR_DATA")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "YT backend running with PO_TOKEN + VISITOR_DATA + fallback"}

@app.get("/get_stream")
def get_stream(videoId: str):
    try:
        match = re.search(r"([a-zA-Z0-9_-]{11})", videoId)

        if not match:
            raise HTTPException(status_code=400, detail="Invalid YouTube videoId")

        actual_id = match.group(1)
        video_url = f"https://www.youtube.com/watch?v={actual_id}"

        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            }
        }

        if PO_TOKEN:
            youtube_args = {
                "player_client": ["android", "web"],
                "po_token": [f"web+{PO_TOKEN}"]
            }

            if VISITOR_DATA:
                youtube_args["visitor_data"] = [VISITOR_DATA]

            ydl_opts["extractor_args"] = {
                "youtube": youtube_args
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                stream_url = info.get("url")

                if not stream_url:
                    raise Exception("yt-dlp stream url missing")

                return {
                    "status": "success",
                    "source": "yt-dlp",
                    "videoId": actual_id,
                    "url": stream_url,
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail")
                }

        except Exception as ytdlp_error:
            print("yt-dlp failed, trying Invidious:", ytdlp_error)

            INVIDIOUS_SERVERS = [
                "https://yewtu.be",
                "https://invidious.privacydev.net",
                "https://invidious.fdn.fr",
                "https://vid.puffyan.us",
                "https://inv.tux.pizza"
            ]

            data = None
            used_server = None

            for server in INVIDIOUS_SERVERS:
                try:
                    inv_url = f"{server}/api/v1/videos/{actual_id}"
                    res = requests.get(inv_url, timeout=8)

                    if res.status_code == 200:
                        data = res.json()
                        used_server = server
                        print(f"Using Invidious: {server}")
                        break

                except Exception as e:
                    print(f"{server} failed:", e)

            if not data:
                raise Exception("All Invidious servers failed")

            formats = data.get("adaptiveFormats", []) + data.get("formatStreams", [])

            audio_links = [
                f for f in formats
                if "audio" in f.get("type", "") and f.get("url")
            ]

            if not audio_links:
                raise Exception("No audio stream found from Invidious")

            best_audio = audio_links[-1]

            return {
                "status": "success",
                "source": "invidious",
                "server": used_server,
                "videoId": actual_id,
                "url": best_audio.get("url"),
                "title": data.get("title"),
                "duration": data.get("lengthSeconds"),
                "thumbnail": data.get("videoThumbnails", [{}])[-1].get("url")
            }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stream fetch failed: {str(e)}"
        )
