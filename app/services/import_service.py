import asyncio
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

_EXTRA_OPTS = {
    "extract_flat": True,
    "quiet": True,
    "no_warnings": True,
}


def _extract_thumbnail(entry: dict) -> Optional[str]:
    thumb = entry.get("thumbnail")
    if thumb:
        return thumb
    thumbs = entry.get("thumbnails")
    if thumbs and isinstance(thumbs, list) and len(thumbs) > 0:
        url = thumbs[0].get("url")
        if url:
            return url
    vid = entry.get("id", "")
    if vid:
        return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
    return None


def _fetch_list(url: str, max_results: int = 50) -> List[Dict]:
    import yt_dlp
    with yt_dlp.YoutubeDL({**_EXTRA_OPTS, "playlistend": max_results}) as ydl: # type: ignore
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                return []
            uploader = info.get("uploader", info.get("channel", ""))
            entries = info.get("entries") or []
            return [
                {
                    "video_id": e["id"],
                    "titulo": e.get("title", "Sin título"),
                    "canal_autor": e.get("channel", e.get("uploader", uploader)),
                    "miniatura_url": _extract_thumbnail(e),
                }
                for e in entries if e and e.get("id")
            ]
        except Exception as e:
            logger.error(f"yt-dlp error en {url}: {e}")
            return []


class YouTubeImporter:
    async def get_channel_videos(self, channel_url: str, max_results: int = 50) -> List[Dict]:
        return await asyncio.to_thread(_fetch_list, channel_url, max_results)

    async def get_playlist_videos(self, playlist_url: str, max_results: int = 50) -> List[Dict]:
        return await asyncio.to_thread(_fetch_list, playlist_url, max_results)

    async def preview(self, url: str) -> dict:
        """Returns video list + metadata without importing."""
        videos = await asyncio.to_thread(_fetch_list, url, 50)
        return {
            "url": url,
            "total": len(videos),
            "videos": videos,
        }
