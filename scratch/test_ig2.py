import urllib.request
import re

url = "https://www.instagram.com/tattooskystudio/"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
})

with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

urls = re.findall(r'https?:\\?/\\?/[^"\'\s>]+', html)
media_urls = []
for u in urls:
    clean = u.replace("\\/", "/").replace("\\u0026", "&").replace("&amp;", "&").split('\\"')[0].split('"')[0]
    if ("scontent" in clean or "fbcdn" in clean or "/v/t" in clean or "instagram" in clean) and not clean.endswith(".js") and not clean.endswith(".css") and not clean.endswith(".gif") and "rsrc.php" not in clean:
        if clean not in media_urls:
            media_urls.append(clean)

print("REAL Instagram Media URLs found:", len(media_urls))
for idx, u in enumerate(media_urls[:20]):
    print(f"[{idx+1}] {u[:120]}")
