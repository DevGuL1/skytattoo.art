from django.contrib import admin
from django.utils.html import format_html

from .models import Artist, Reel, SocialPost


class ReelInline(admin.TabularInline):
    model = Reel
    extra = 1
    fields = ("title", "provider", "video_url", "thumbnail", "order")


class SocialPostInline(admin.TabularInline):
    model = SocialPost
    extra = 1
    fields = ("url", "platform", "caption", "order")
    readonly_fields = ("platform",)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "role", "is_active", "order")
    list_display_links = ("thumb", "name")
    list_editable = ("is_active", "order")
    list_filter = ("is_active", "styles")
    search_fields = ("name", "role", "bio")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("styles",)
    inlines = [ReelInline, SocialPostInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "role", "tagline", "is_active", "order")}),
        ("Profile", {"fields": ("bio", "avatar", "cover_image", "styles")}),
        ("Social & contact", {"fields": ("instagram", "facebook", "tiktok", "email")}),
    )

    @admin.display(description="")
    def thumb(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;border-radius:50%;'
                'object-fit:cover;" />',
                obj.avatar.url,
            )
        return "—"


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ("__str__", "artist", "provider", "order")
    list_filter = ("provider", "artist")
    search_fields = ("title",)
