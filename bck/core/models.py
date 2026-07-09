from django.core.exceptions import ValidationError
from django.db import models


class SiteSetting(models.Model):
    """Singleton holding global site + SEO configuration.

    Editable from the admin so non-developers can manage branding, social
    links and default SEO tags without touching code.
    """

    site_name = models.CharField(max_length=120, default="Skytattoo.art")
    tagline = models.CharField(
        max_length=200, blank=True, default="Gothic ink. Timeless art."
    )
    about_short = models.TextField(blank=True)

    # SEO defaults
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)
    og_image = models.ImageField(upload_to="seo/", blank=True, null=True)

    # Contact
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    email = models.EmailField(blank=True)
    opening_hours = models.TextField(blank=True)
    google_maps_embed = models.TextField(
        blank=True,
        help_text="Paste the full <iframe> embed code from Google Maps.",
    )

    # Social
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    # --- Floating Action Button ---
    show_float_button = models.BooleanField("Show Floating Contact Button", default=True)
    float_whatsapp = models.CharField("Float WhatsApp Number or Link", max_length=100, blank=True, help_text="e.g. +995599123456 or a wa.me link")
    float_facebook = models.URLField("Float Facebook Link", blank=True)
    float_instagram = models.URLField("Float Instagram Link", blank=True)
    float_email = models.EmailField("Float Email Address", blank=True)

    # --- Homepage · Hero ---
    hero_eyebrow = models.CharField(
        max_length=160, blank=True, default="Gothic Tattoo Studio · Tbilisi"
    )
    hero_title = models.CharField(max_length=80, blank=True, default="Sky")
    hero_title_accent = models.CharField(max_length=80, blank=True, default="tattoo")
    hero_subtitle = models.TextField(
        blank=True,
        default="Gothic ink. Timeless art. — where dark artistry becomes permanent. "
        "Bespoke blackwork, realism and gothic ink by resident masters.",
    )
    hero_bg = models.ImageField(
        upload_to="home/", blank=True, null=True,
        help_text="Optional hero background image (dark works best).",
    )
    hero_video = models.FileField(
        upload_to="home/", blank=True, null=True,
        help_text="Optional hero background video (MP4 format). If uploaded, it plays instead of the image.",
    )
    cta_primary_label = models.CharField(max_length=60, blank=True, default="Book Appointment")
    cta_secondary_label = models.CharField(max_length=60, blank=True, default="Meet Our Artists")

    # --- Homepage · Featured portfolio section ---
    featured_eyebrow = models.CharField(max_length=120, blank=True, default="Latest Ink")
    featured_title = models.CharField(max_length=120, blank=True, default="Featured Portfolio")
    show_featured = models.BooleanField("Show featured section", default=True)

    # --- Homepage · Artists teaser section ---
    artists_eyebrow = models.CharField(max_length=120, blank=True, default="The Coven")
    artists_title = models.CharField(max_length=120, blank=True, default="Meet Our Artists")
    show_artists_teaser = models.BooleanField("Show artists section", default=True)
    show_styles_strip = models.BooleanField("Show styles strip", default=True)

    # --- Homepage · Closing CTA band ---
    cta_band_title = models.CharField(
        max_length=160, blank=True, default="Ready for your next piece?"
    )
    cta_band_text = models.TextField(
        blank=True,
        default="Book a consultation with one of our artists and let's design something eternal.",
    )
    cta_band_label = models.CharField(max_length=60, blank=True, default="Book Appointment")

    # --- About page ---
    about_eyebrow = models.CharField(max_length=120, blank=True, default="Our Story")
    about_title = models.CharField(max_length=120, blank=True, default="About the Studio")
    about_story = models.TextField(
        blank=True,
        help_text="Full studio story shown on the About page.",
    )

    class Meta:
        verbose_name = "Site setting"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Enforce a single row.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactMessage(models.Model):
    """A message submitted through the public contact form."""

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=60, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject or 'Message'}"


class BookingRequest(models.Model):
    """An appointment / booking request from the homepage CTA or contact page."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CONFIRMED = "confirmed", "Confirmed"
        DECLINED = "declined", "Declined"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=60, blank=True)
    artist = models.ForeignKey(
        "artists.Artist",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking_requests",
    )
    style = models.ForeignKey(
        "portfolio.TattooStyle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking_requests",
    )
    preferred_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class StudioValue(models.Model):
    """A 'why choose us' value card shown on the About page."""

    title = models.CharField(max_length=120)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Studio value"
        verbose_name_plural = "Studio values"

    def __str__(self):
        return self.title


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True, help_text="e.g. ka, en, ru")
    name = models.CharField(max_length=100, help_text="e.g. ქართული, English, Русский")
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        if self.is_default:
            Language.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def load_defaults(cls):
        if not cls.objects.exists():
            cls.objects.create(code="en", name="English", is_default=True, is_active=True, order=0)
            cls.objects.create(code="ka", name="ქართული", is_default=False, is_active=True, order=1)
            cls.objects.create(code="ru", name="Русский", is_default=False, is_active=True, order=2)


class Translation(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="translations")
    object_key = models.CharField(max_length=255, db_index=True)  # e.g. "sitesetting:1:hero_title"
    text = models.TextField()

    class Meta:
        unique_together = ("language", "object_key")

    def __str__(self):
        return f"{self.language.code} -> {self.object_key}"


class StaticString(models.Model):
    key = models.CharField(max_length=255, unique=True, help_text="Original English text")

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.key
