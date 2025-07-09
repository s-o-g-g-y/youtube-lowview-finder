import os
import requests
from flask import Flask, render_template_string
from datetime import datetime, timedelta, timezone

API_KEY = os.environ["YOUTUBE_API_KEY"]
app = Flask(__name__)

@app.route("/")
def index():
    query = '"mein erstes video" OR "vlog deutsch" OR "neues video"'
    published_after = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat("T")

    # API-Request: Suche Videos
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&order=date&relevanceLanguage=de&regionCode=DE"
        f"&q={query}&publishedAfter={published_after}&maxResults=50&key={API_KEY}"
    )

    try:
        search_response = requests.get(search_url).json()
        print("🔍 YouTube Search API Response:", search_response)
    except Exception as e:
        return f"<h3>❌ Fehler beim Abrufen der Daten: {e}</h3>"

    videos = []

    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        title = snippet["title"]
        channel = snippet["channelTitle"]
        published = snippet["publishedAt"][:10]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # API-Request: View-Zahl prüfen
        stats_url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=statistics&id={video_id}&key={API_KEY}"
        )
        stats_response = requests.get(stats_url).json()
        print(f"▶️ Stats for {video_id}:", stats_response)

        if stats_response.get("items"):
            stats = stats_response["items"][0]["statistics"]
            view_count = int(stats.get("viewCount", "0") or "0")

            if view_count <= 10:  # zum Testen mehr zulassen
                videos.append((title, video_url, channel, published, view_count))

    # HTML-Vorlage
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Low-View Finder</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 2rem; }
            h2 { color: #333; }
            button {
                background-color: #007BFF;
                color: white;
                padding: 10px 16px;
                font-size: 16px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                margin-bottom: 20px;
            }
            button:hover { background-color: #0056b3; }
            ul { list-style-type: none; padding-left: 0; }
            li { margin-bottom: 1rem; }
            .info { color: gray; font-style: italic; }
        </style>
    </head>
    <body>
        <h2>🕵️ Neue deutsche YouTube-Videos (≤10 Aufrufe, letzte 24h)</h2>
        <form method="get" action="/">
            <button type="submit">🔁 Neu laden</button>
        </form>

        {% if videos %}
            <ul>
            {% for title, url, channel, published, views in videos %}
                <li>
                    <a href="{{ url }}" target="_blank">{{ title }}</a><br>
                    👤 {{ channel }} – 📅 {{ published }} – 👁️ {{ views }} Aufrufe
                </li>
            {% endfor %}
            </ul>
        {% else %}
            <p class="info">Keine Videos mit ≤10 Aufrufen gefunden. Versuch es später nochmal!</p>
        {% endif %}
    </body>
    </html>
    """

    return render_template_string(html, videos=videos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
