from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Artist(models.Model):
    """A tattoo artist with their own mini-site / profile page."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    role = models.CharField(
        max_length=120,
        blank=True,
        help_text="e.g. Resident Artist, Founder, Guest Artist",
    )
    tagline = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)

    avatar = models.ImageField(upload_to="artists/avatars/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="artists/covers/", blank=True, null=True)

    styles = models.ManyToManyField(
        "portfolio.TattooStyle", related_name="artists", blank=True
    )

    # Social / contact
    instagram = models.URLField(blank=True)
    instagram_username = models.CharField(
        max_length=60,
        blank=True,
        help_text="Instagram handle without @, e.g. avtosailor",
    )
    instagram_hashtag = models.CharField(
        max_length=60,
        blank=True,
        help_text="Hashtag for portfolio sync without #, e.g. avtosailor",
    )
    facebook = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("artists:detail", kwargs={"slug": self.slug})


class Reel(models.Model):
    """A short video (YouTube / Vimeo embed) attached to an artist."""

    class Provider(models.TextChoices):
        YOUTUBE = "youtube", "YouTube"
        VIMEO = "vimeo", "Vimeo"

    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="reels"
    )
    title = models.CharField(max_length=140, blank=True)
    provider = models.CharField(
        max_length=20, choices=Provider.choices, default=Provider.YOUTUBE
    )
    video_url = models.URLField(
        help_text="Full YouTube / Vimeo URL. The embed is generated automatically."
    )
    thumbnail = models.ImageField(upload_to="artists/reels/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title or f"Reel #{self.pk}"

    @property
    def embed_url(self):
        """Return an iframe-friendly embed URL derived from ``video_url``."""
        url = self.video_url.strip()
        if self.provider == self.Provider.YOUTUBE:
            vid = ""
            if "watch?v=" in url:
                vid = url.split("watch?v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                vid = url.split("youtu.be/")[1].split("?")[0]
            elif "/shorts/" in url:
                vid = url.split("/shorts/")[1].split("?")[0]
            elif "/embed/" in url:
                vid = url.split("/embed/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{vid}" if vid else url
        # Vimeo
        if "vimeo.com/" in url:
            vid = url.rstrip("/").split("vimeo.com/")[1].split("?")[0].split("/")[0]
            return f"https://player.vimeo.com/video/{vid}"
        return url


class SocialPost(models.Model):
    """A single Instagram post/reel or TikTok video embedded on the artist page.

    The studio just pastes a public post/video URL — the platform is detected
    automatically and rendered with the official embed script, so the widget
    always shows the current live content (a lightweight 'social proof' feed
    that needs no API keys).
    """

    class Platform(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        TIKTOK = "tiktok", "TikTok"

    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="social_posts"
    )
    url = models.URLField(
        help_text="Paste a public Instagram post/reel or TikTok video URL. "
        "The platform is detected automatically."
    )
    platform = models.CharField(
        max_length=20, choices=Platform.choices, blank=True,
        help_text="Auto-detected from the URL.",
    )
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Social post"
        verbose_name_plural = "Social feed"

    def __str__(self):
        return f"{self.get_platform_display() or 'Social'} — {self.url}"

    def save(self, *args, **kwargs):
        url = (self.url or "").lower()
        if "tiktok.com" in url:
            self.platform = self.Platform.TIKTOK
        elif "instagram.com" in url:
            self.platform = self.Platform.INSTAGRAM
        super().save(*args, **kwargs)

    @property
    def tiktok_id(self):
        """The numeric video id TikTok's embed script needs, parsed from the URL."""
        import re

        m = re.search(r"/video/(\d+)", self.url or "")
        return m.group(1) if m else ""

    @property
    def is_tiktok(self):
        return self.platform == self.Platform.TIKTOK

    @property
    def is_instagram(self):
        return self.platform == self.Platform.INSTAGRAM
