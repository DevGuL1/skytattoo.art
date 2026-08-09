import instaloader

L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

try:
    print("Fetching profile for tattooskystudio...")
    profile = instaloader.Profile.from_username(L.context, "tattooskystudio")
    print(f"Profile: @{profile.username} | Full Name: {profile.full_name} | Posts count: {profile.mediacount}")
    print("Bio:", profile.biography)

    posts_list = []
    for idx, post in enumerate(profile.get_posts()):
        if idx >= 10:
            break
        caption_text = post.caption or ""
        print(f"[{idx+1}] ID: {post.shortcode} | URL: {post.url} | Date: {post.date_utc}")
        print(f"     Caption: {caption_text[:80]}...")
        posts_list.append({
            "shortcode": post.shortcode,
            "url": post.url,
            "caption": caption_text,
            "date": str(post.date_utc),
        })

except Exception as e:
    print("Instaloader Error:", e)
