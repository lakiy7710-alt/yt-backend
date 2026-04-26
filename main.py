from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI()

@app.get("/")
def home():
    return {"status": "YT backend running"}

@app.get("/get_stream")
def get_stream(videoId: str):
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "geo_bypass": True,
        # Niche wala hissa YouTube bot detection bypass karega
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
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={videoId}", download=False)

            stream_url = info.get("url")

            if not stream_url:
                formats = info.get("formats", [])
                audio_formats = [f for f in formats if f.get("url") and f.get("acodec") != "none"]
                if audio_formats:
                    stream_url = audio_formats[-1].get("url")

            if not stream_url:
                raise Exception("No playable audio URL found")

            return {"url": stream_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
