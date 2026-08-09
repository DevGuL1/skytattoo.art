import io
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify

from artists.models import Artist
from core.models import SiteSetting
from portfolio.models import PortfolioItem
from dashboard.models import InstagramSyncConfig, InstagramSyncLog


class InstagramCheckerService:
    """Service for checking and importing Instagram & Facebook posts dynamically

    from the admin-configured Instagram and Facebook account URLs.
    """

    @staticmethod
    def extract_handle_from_url(url_or_handle, default="tattooskystudio"):
        """Extract handle/username from full URL or return cleaned string.

        Examples:
        - https://www.instagram.com/tattooskystudio/ -> tattooskystudio
        - https://facebook.com/my_page -> my_page
        - https://facebook.com/profile.php?id=971476806039423 -> 971476806039423
        - @my_page -> my_page
        """
        if not url_or_handle:
            return default
        clean = url_or_handle.strip().rstrip('/')
        if '://' in clean or '/' in clean:
            parsed = urllib.parse.urlparse(clean)
            qs = urllib.parse.parse_qs(parsed.query)
            if 'id' in qs and qs['id']:
                return qs['id'][0]
            path = parsed.path
            parts = [p for p in path.split('/') if p]
            if parts and parts[-1] not in ['profile.php', 'index.php']:
                return parts[-1].lstrip('@')
        return clean.lstrip('@')

    @staticmethod
    def import_single_post_url(post_url="", image_url="", caption="", source="instagram"):
        """Import a single post by direct URL or image link from Dashboard."""
        if not post_url and not image_url:
            return False, "გთხოვთ მიუთითოთ პოსტის ან სურათის ბმული."

        active_artists = list(Artist.objects.filter(is_active=True))
        matched_artist = InstagramCheckerService._find_matching_artist(caption, active_artists)

        clean_url = post_url.strip()
        post_id = slugify(clean_url.split('/')[-2] if '/' in clean_url and len(clean_url.split('/')) > 2 else clean_url) or f"post_{int(datetime.now().timestamp())}"

        # If image_url not given, try fetching og:image from post_url
        if not image_url and clean_url:
            try:
                req = urllib.request.Request(
                    clean_url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')
                    m = re.search(r'property="og:image"\s+content="([^"]+)"', html)
                    if m:
                        image_url = m.group(1).replace("&amp;", "&")
                    c_m = re.search(r'property="og:description"\s+content="([^"]+)"', html)
                    if c_m and not caption:
                        caption = c_m.group(1)
            except Exception as e:
                print(f"Error fetching og:image from {clean_url}: {e}")

        if not image_url:
            return False, "სურათის ბმული ვერ ამოიცნო. გთხოვთ პირდაპირ ჩასვათ სურათის ლინკი (Image URL)."

        try:
            img_content = InstagramCheckerService._download_image(image_url)
            if not img_content:
                return False, "სურათის გადმოწერა ვერ მოხერხდა."

            title_short = caption[:100].strip() or f"SkyTattoo {source.title()} Work"
            base_slug = slugify(f"{source}-{post_id}")
            slug = base_slug
            c = 1
            while PortfolioItem.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{c}"
                c += 1

            file_name = f"{source}_{post_id}.jpg"
            src_val = PortfolioItem.Source.FACEBOOK if source.lower() == "facebook" else PortfolioItem.Source.INSTAGRAM

            item = PortfolioItem(
                title=title_short,
                slug=slug,
                artist=matched_artist,
                description=caption,
                source=src_val,
                is_from_instagram=(source.lower() == "instagram"),
                is_from_facebook=(source.lower() == "facebook"),
                instagram_post_id=post_id if source.lower() == "instagram" else None,
                facebook_post_id=post_id if source.lower() == "facebook" else None,
                instagram_permalink=clean_url if source.lower() == "instagram" else "",
                facebook_permalink=clean_url if source.lower() == "facebook" else "",
            )
            item.image.save(file_name, ContentFile(img_content), save=False)
            item.save()

            matched_styles = InstagramCheckerService._find_matching_styles(title_or_desc, matched_artist)
            if matched_styles:
                item.styles.set(matched_styles)

            artist_msg = f" (მიენიჭა არტისტს {matched_artist.name})" if matched_artist else " (დაემატა მთლიან პორტფოლიოში)"
            return True, f"პოსტი წარმატებით შემოვიდა{artist_msg}!"
        except Exception as e:
            return False, f"შეცდომა შენახვისას: {e}"

    @staticmethod
    def run_full_sync(max_posts=50):
        """Run full sync for Instagram & Facebook using URLs configured by the admin in Dashboard."""
        config = InstagramSyncConfig.get_solo()
        log_messages = []
        total_fetched = 0
        total_created = 0

        # Step 1: Sync Instagram Studio Account from Admin Configured URL
        ig_fetched, ig_created, ig_msg = InstagramCheckerService.sync_instagram_studio(max_posts=max_posts)
        total_fetched += ig_fetched
        total_created += ig_created
        log_messages.append(ig_msg)

        # Step 2: Sync Facebook Studio Page from Admin Configured URL
        fb_fetched, fb_created, fb_msg = InstagramCheckerService.sync_facebook_studio(max_posts=max_posts)
        total_fetched += fb_fetched
        total_created += fb_created
        log_messages.append(fb_msg)

        # Step 3: Sync Artist-specific Hashtags
        artists = Artist.objects.filter(is_active=True).exclude(instagram_hashtag="")
        for artist in artists:
            a_fetched, a_created, a_msg = InstagramCheckerService.fetch_and_save_posts_for_artist(artist, max_posts=10)
            total_fetched += a_fetched
            total_created += a_created
            log_messages.append(a_msg)

        # Update Config Status
        now = timezone.now()
        config.last_synced_at = now
        config.last_status = "success"
        config.last_error_message = ""
        config.save()

        details_str = "\n".join(log_messages)

        sync_log = InstagramSyncLog.objects.create(
            status=InstagramSyncLog.Status.SUCCESS,
            posts_fetched=total_fetched,
            items_created=total_created,
            details=details_str,
        )

        return {
            "success": True,
            "posts_fetched": total_fetched,
            "items_created": total_created,
            "details": details_str,
            "log": sync_log,
        }

    @staticmethod
    def sync_instagram_studio(max_posts=50):
        """Fetch latest posts from admin-configured Instagram Account URL."""
        config = InstagramSyncConfig.get_solo()
        site_setting = SiteSetting.objects.first()

        account_url = config.instagram_account_url or (site_setting.instagram if site_setting else "") or "https://www.instagram.com/tattooskystudio/"
        handle = InstagramCheckerService.extract_handle_from_url(account_url, default="tattooskystudio")

        posts = InstagramCheckerService._query_instagram_posts(username=handle, count=max_posts)
        created_count = 0
        active_artists = list(Artist.objects.filter(is_active=True))

        for post in posts[:max_posts]:
            post_id = post.get("id")
            image_url = post.get("image_url")
            caption = post.get("caption") or f"SkyTattoo Studio Work @{handle}"
            permalink = post.get("permalink") or account_url

            if not post_id or not image_url:
                continue

            if PortfolioItem.objects.filter(instagram_post_id=post_id).exists():
                continue

            matched_artist = InstagramCheckerService._find_matching_artist(caption, active_artists)

            try:
                img_content = InstagramCheckerService._download_image(image_url)
                if not img_content:
                    continue

                title_short = caption[:100].strip() or f"SkyTattoo Work (@{handle})"
                base_slug = slugify(f"ig-{handle}-{post_id}")
                slug = base_slug
                c = 1
                while PortfolioItem.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{c}"
                    c += 1

                file_name = f"ig_{handle}_{post_id}.jpg"

                item = PortfolioItem(
                    title=title_short,
                    slug=slug,
                    artist=matched_artist,
                    description=caption,
                    source=PortfolioItem.Source.INSTAGRAM,
                    is_from_instagram=True,
                    instagram_post_id=post_id,
                    instagram_permalink=permalink,
                )
                item.image.save(file_name, ContentFile(img_content), save=False)
                item.save()

                matched_styles = InstagramCheckerService._find_matching_styles(caption, matched_artist)
                if matched_styles:
                    item.styles.set(matched_styles)

                created_count += 1
            except Exception as e:
                print(f"Error saving IG post {post_id}: {e}")

        return len(posts), created_count, f"Instagram (@{handle}): წამოღებულია {len(posts)} პოსტი, შეიქმნა {created_count} ნამუშევარი."

    @staticmethod
    def sync_facebook_studio(max_posts=50):
        """Fetch latest photos/posts from admin-configured Facebook Page URL."""
        config = InstagramSyncConfig.get_solo()
        site_setting = SiteSetting.objects.first()

        page_url = config.facebook_page_url or (site_setting.facebook if site_setting else "") or "https://www.facebook.com/tattooskystudio"
        page_handle = InstagramCheckerService.extract_handle_from_url(page_url, default="tattooskystudio")

        posts = InstagramCheckerService._query_facebook_posts(page=page_handle, count=max_posts)
        created_count = 0
        active_artists = list(Artist.objects.filter(is_active=True))

        for post in posts[:max_posts]:
            post_id = post.get("id")
            image_url = post.get("image_url")
            caption = post.get("caption") or f"SkyTattoo Facebook Page Work ({page_handle})"
            permalink = post.get("permalink") or page_url

            if not post_id or not image_url:
                continue

            if PortfolioItem.objects.filter(facebook_post_id=post_id).exists():
                continue

            matched_artist = InstagramCheckerService._find_matching_artist(caption, active_artists)

            try:
                img_content = InstagramCheckerService._download_image(image_url)
                if not img_content:
                    continue

                title_short = caption[:100].strip() or f"SkyTattoo FB Work ({page_handle})"
                base_slug = slugify(f"fb-{page_handle}-{post_id}")
                slug = base_slug
                c = 1
                while PortfolioItem.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{c}"
                    c += 1

                file_name = f"fb_{page_handle}_{post_id}.jpg"

                item = PortfolioItem(
                    title=title_short,
                    slug=slug,
                    artist=matched_artist,
                    description=caption,
                    source=PortfolioItem.Source.FACEBOOK,
                    is_from_facebook=True,
                    facebook_post_id=post_id,
                    facebook_permalink=permalink,
                )
                item.image.save(file_name, ContentFile(img_content), save=False)
                item.save()

                matched_styles = InstagramCheckerService._find_matching_styles(caption, matched_artist)
                if matched_styles:
                    item.styles.set(matched_styles)

                created_count += 1
            except Exception as e:
                print(f"Error saving FB post {post_id}: {e}")

        return len(posts), created_count, f"Facebook Page ({page_handle}): წამოღებულია {len(posts)} პოსტი, შეიქმნა {created_count} ნამუშევარი."

    @staticmethod
    def fetch_and_save_posts_for_artist(artist, max_posts=10):
        """Fetch artist specific hashtag posts."""
        posts_found = []
        created_count = 0
        hashtag = (artist.instagram_hashtag or "").strip().lstrip("#")

        if not hashtag:
            return 0, 0, f"No hashtag for {artist.name}"

        candidates = InstagramCheckerService._query_instagram_posts(hashtag=hashtag, count=max_posts)

        for post in candidates[:max_posts]:
            post_id = post.get("id")
            image_url = post.get("image_url")
            caption = post.get("caption") or f"{artist.name} tattoo work"
            permalink = post.get("permalink") or f"https://www.instagram.com/explore/tags/{hashtag}/"

            if not post_id or not image_url:
                continue

            posts_found.append(post)

            if PortfolioItem.objects.filter(instagram_post_id=post_id).exists():
                continue

            try:
                img_content = InstagramCheckerService._download_image(image_url)
                if not img_content:
                    continue

                title_short = caption[:100].strip() or f"{artist.name} Tattoo"
                base_slug = slugify(f"{artist.slug}-{post_id}")
                slug = base_slug
                c = 1
                while PortfolioItem.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{c}"
                    c += 1

                file_name = f"ig_{artist.slug}_{post_id}.jpg"

                item = PortfolioItem(
                    title=title_short,
                    slug=slug,
                    artist=artist,
                    description=caption,
                    source=PortfolioItem.Source.INSTAGRAM,
                    is_from_instagram=True,
                    instagram_post_id=post_id,
                    instagram_permalink=permalink,
                )
                item.image.save(file_name, ContentFile(img_content), save=False)
                item.save()

                matched_styles = InstagramCheckerService._find_matching_styles(caption, artist)
                if matched_styles:
                    item.styles.set(matched_styles)

                created_count += 1
            except Exception as e:
                print(f"Error saving hashtag post {post_id}: {e}")

        return len(posts_found), created_count, f"Hashtag #{hashtag}: წამოღებულია {len(posts_found)} პოსტი, შეიქმნა {created_count} ნამუშევარი ({artist.name})."

    @staticmethod
    def _find_matching_artist(caption, active_artists):
        """Match hashtag in post caption to an active artist."""
        if not caption:
            return None

        caption_lower = caption.lower()
        for artist in active_artists:
            raw_tags = (artist.instagram_hashtag or "").split(",")
            for raw_tag in raw_tags:
                tag = raw_tag.strip().lstrip("#").lower()
                if tag and (f"#{tag}" in caption_lower or tag in caption_lower):
                    return artist

            uname = (artist.instagram_username or "").strip().lstrip("@").lower()
            name_lower = artist.name.lower()

            if uname and (f"@{uname}" in caption_lower or uname in caption_lower):
                return artist
            if name_lower in caption_lower:
                return artist

        return None

    @staticmethod
    def _find_matching_styles(caption, artist=None):
        """Match hashtags or keywords in caption to TattooStyle models."""
        from portfolio.models import TattooStyle
        matched = set()

        if artist and artist.styles.exists():
            matched.update(artist.styles.all())

        if not caption:
            return list(matched)

        caption_lower = caption.lower()
        all_styles = TattooStyle.objects.all()

        for style in all_styles:
            name_clean = style.name.lower().replace(" ", "")
            slug_clean = style.slug.lower()
            if (f"#{name_clean}" in caption_lower or
                f"#{slug_clean}" in caption_lower or
                name_clean in caption_lower or
                slug_clean in caption_lower):
                matched.add(style)

        return list(matched)

    @staticmethod
    def _query_instagram_posts(username="tattooskystudio", hashtag="", count=50):
        """Query Instagram post metadata dynamically using configured account or hashtag."""
        config = InstagramSyncConfig.get_solo()
        results = []
        target = username or hashtag or "tattooskystudio"

        # 1. Meta Graph API (if token configured)
        if config.instagram_access_token:
            try:
                if config.instagram_account_id:
                    url = f"https://graph.facebook.com/v19.0/{config.instagram_account_id}/media?fields=id,caption,media_type,media_url,permalink,timestamp&access_token={config.instagram_access_token}"
                else:
                    url = f"https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,permalink,timestamp&access_token={config.instagram_access_token}"

                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    for item in data.get("data", []):
                        img_url = item.get("media_url")
                        if item.get("media_type") in ["IMAGE", "CAROUSEL_ALBUM"] and img_url:
                            results.append({
                                "id": item.get("id"),
                                "image_url": img_url,
                                "caption": item.get("caption") or f"@{target} tattoo artwork",
                                "permalink": item.get("permalink") or f"https://www.instagram.com/{target}/",
                            })
            except Exception as e:
                print(f"Meta Graph API error: {e}")

        # 2. Instagram Session ID Cookie (if sessionid configured by admin)
        if not results and config.instagram_session_id:
            try:
                url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={target}"
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "X-IG-App-ID": "936619743392459",
                        "Cookie": f"sessionid={config.instagram_session_id.strip()}"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    edges = data.get("data", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("edges", [])
                    for edge in edges:
                        node = edge.get("node", {})
                        img = node.get("display_url")
                        shortcode = node.get("shortcode")
                        captions = node.get("edge_media_to_caption", {}).get("edges", [])
                        cap = captions[0].get("node", {}).get("text", "") if captions else f"@{target} tattoo work"
                        if img:
                            results.append({
                                "id": node.get("id") or shortcode,
                                "image_url": img,
                                "caption": cap,
                                "permalink": f"https://www.instagram.com/p/{shortcode}/" if shortcode else f"https://www.instagram.com/{target}/"
                            })
            except Exception as e:
                print(f"Instagram Session Cookie fetch error: {e}")

        return results[:count]

    @staticmethod
    def _query_facebook_posts(page="tattooskystudio", count=50):
        """Query Facebook page post metadata dynamically."""
        config = InstagramSyncConfig.get_solo()
        results = []
        target = page or "tattooskystudio"

        fb_token = config.facebook_access_token or config.instagram_access_token
        fb_page_id = config.facebook_page_id or target

        # 1. Meta Graph API for Facebook Page
        if fb_token:
            try:
                # First: Fetch Page Access Token from User Accounts
                page_token = fb_token
                target_page_id = fb_page_id

                try:
                    acc_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={fb_token}"
                    req = urllib.request.Request(acc_url)
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        acc_data = json.loads(resp.read().decode('utf-8'))
                        pages = acc_data.get("data", [])
                        matched = None
                        for p in pages:
                            if p.get("id") == fb_page_id or target.lower() in p.get("name", "").lower():
                                matched = p
                                break

                        if not matched and pages:
                            # Auto-match page with 'tattoo' or 'sky' in name, or fallback to first page
                            matched = next((p for p in pages if 'tattoo' in p.get('name', '').lower() or 'sky' in p.get('name', '').lower()), pages[0])

                        if matched:
                            page_token = matched.get("access_token", fb_token)
                            target_page_id = matched.get("id", fb_page_id)
                except Exception as ex_acc:
                    print(f"Page account resolution info: {ex_acc}")

                # Query Page posts with Page Token
                posts_url = f"https://graph.facebook.com/v19.0/{target_page_id}/posts?fields=id,message,full_picture,permalink_url,created_time&access_token={page_token}"
                req = urllib.request.Request(posts_url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    for item in data.get("data", []):
                        img_url = item.get("full_picture")
                        if img_url:
                            results.append({
                                "id": item.get("id"),
                                "image_url": img_url,
                                "caption": item.get("message") or f"Facebook Post #{target}",
                                "permalink": item.get("permalink_url") or f"https://www.facebook.com/{target}/",
                            })
            except Exception as e:
                print(f"Meta Graph API Facebook error: {e}")

        return results[:count]

    @staticmethod
    def _download_image(url):
        """Download image binary content from URL."""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
