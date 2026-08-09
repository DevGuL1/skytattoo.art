import urllib.request
import json

url = "https://www.instagram.com/api/v1/users/web_profile_info/?username=tattooskystudio"
req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Referer": "https://www.instagram.com/tattooskystudio/",
    }
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        user = data.get("data", {}).get("user", {})
        print("Username:", user.get("username"))
        print("Full name:", user.get("full_name"))
        print("Biography:", user.get("biography"))
        timeline = user.get("edge_owner_to_timeline_media", {})
        edges = timeline.get("edges", [])
        print("Timeline Posts Found:", len(edges))
        
        for idx, edge in enumerate(edges[:10]):
            node = edge.get("node", {})
            shortcode = node.get("shortcode")
            display_url = node.get("display_url")
            caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
            caption = caption_edges[0]["node"]["text"] if caption_edges else ""
            print(f"[{idx+1}] Shortcode: {shortcode} | Image: {display_url[:60]}... | Caption: {caption[:60]}")

except Exception as e:
    print("Error querying web_profile_info:", e)
