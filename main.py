from fastapi import FastAPI
import yt_dlp

app = FastAPI()

@app.get("/get_stream")
def get_stream(videoId: str):
    with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={videoId}", download=False)
        return {"url": info['url']}