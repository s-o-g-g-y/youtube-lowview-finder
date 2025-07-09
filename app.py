import os
import requests
from flask import Flask, render_template_string
from datetime import datetime, timedelta

API_KEY = os.environ["YOUTUBE_API_KEY"]

app = Flask(__name__)

@app.route("/")
def index():
    query = '"mein erstes video" OR "vlog deutsch" OR "neues video"'
    published_after = (datetime.utcnow() - timedelta(hours=24)).isoformat("T") + "Z"

    search_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&order=date&relevanceLanguage=de&regionCode=DE"
        f"&q={query}&publishedAfter={published_after}&maxResults=20&key={API_KEY}"
    )

    search_response = requests.get(search_url).json()
    videos = []

    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        title = snippet["title"]
        channel = snippet["channelTitle"]
        published = snippet["publishedAt"][:10]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Video View Count holen
        stats_url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=statistics&id={video_id}&key={API_KEY}"
        )
        stats_response = requests.get(stats_url).json()

        if stats_response.get("items"):
            stats = stats_response["items"][0]["statistics"]
            view_count = int(stats.get("viewCount", 0))

            if view_count <= 1:
                videos.append((title, video_url, channel, published, view_count))

    html = """
    <h2>🕵️ Neue deutsche YouTube-Videos (0–1 Aufruf, letzte 24h)</h2>
    <ul>
    {% for title, url, channel, published, views in videos %}
        <li>
            <a href="{{ url }}" target="_blank">{{ title }}</a><br>
            👤 {{ channel }} – 📅 {{ published }} – 👁️ {{ views }} Aufrufe
        </li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, videos=videos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
