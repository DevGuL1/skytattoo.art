from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TattooStyle(models.Model):
    """A tag used to classify portfolio work and artists.

    Examples: Blackwork, Realism, Minimal, Gothic.
    """

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    description = models.TextField(blank=True)
    # Optional accent colour (hex) used for the filter chip in the UI.
    color = models.CharField(
        max_length=7,
        default="#8B0000",
        help_text="Hex colour for the filter chip, e.g. #8B0000",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Tattoo style"
        verbose_name_plural = "Tattoo styles"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PortfolioItem(models.Model):
    """A single piece of tattoo work shown in the studio portfolio."""

    class Color(models.TextChoices):
        BLACK_GREY = "black_grey", "Black & Grey"
        COLOR = "color", "Colour"

    class Size(models.TextChoices):
        SMALL = "small", "Small"
        MEDIUM = "medium", "Medium"
        LARGE = "large", "Large"

    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    image = models.ImageField(upload_to="portfolio/")
    artist = models.ForeignKey(
        "artists.Artist",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="portfolio_items",
    )
    styles = models.ManyToManyField(TattooStyle, related_name="portfolio_items", blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=20, choices=Color.choices, default=Color.BLACK_GREY
    )
    size = models.CharField(max_length=20, choices=Size.choices, default=Size.MEDIUM)
    is_featured = models.BooleanField(
        default=False, help_text="Show on the homepage featured grid."
    )
    class Source(models.TextChoices):
        MANUAL = "manual", "Manual Upload"
        INSTAGRAM = "instagram", "Instagram"
        FACEBOOK = "facebook", "Facebook"

    source = models.CharField(
        max_length=20, choices=Source.choices, default=Source.MANUAL
    )
    is_from_instagram = models.BooleanField(default=False)
    instagram_post_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True,
        help_text="Unique ID of synced Instagram post to prevent duplicates."
    )
    instagram_permalink = models.URLField(blank=True, help_text="Direct link to Instagram post.")

    is_from_facebook = models.BooleanField(default=False)
    facebook_post_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True,
        help_text="Unique ID of synced Facebook post to prevent duplicates."
    )
    facebook_permalink = models.URLField(blank=True, help_text="Direct link to Facebook post.")

    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:detail", kwargs={"slug": self.slug})

    @property
    def style_slugs(self):
        """Space-separated style slugs, used by the Isotope filter markup."""
        return " ".join(self.styles.values_list("slug", flat=True))


class PortfolioImage(models.Model):
    """Additional gallery image for a portfolio item."""

    item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )
    image = models.ImageField(upload_to="portfolio/gallery/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Portfolio gallery image"
        verbose_name_plural = "Portfolio gallery images"

    def __str__(self):
        return self.caption or f"{self.item.title} image #{self.pk}"
