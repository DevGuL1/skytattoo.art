import urllib.request
import json

def fetch_oembed(post_url):
    oembed_url = f"https://api.instagram.com/oembed?url={post_url}"
    req = urllib.request.Request(
        oembed_url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print("Title:", data.get("title"))
            print("Author:", data.get("author_name"))
            print("Thumbnail:", data.get("thumbnail_url"))
            print("HTML:", data.get("html")[:100])
            return data
    except Exception as e:
        print("oEmbed Error:", e)
        return None

# Test with a public instagram post link if any
fetch_oembed("https://www.instagram.com/p/C-X8VnOM_--/")
