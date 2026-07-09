from django.contrib import admin
from django.utils.html import format_html

from .models import BookingRequest, ContactMessage, SiteSetting, StudioValue


@admin.register(StudioValue)
class StudioValueAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Branding", {"fields": ("site_name", "tagline", "about_short")}),
        ("SEO", {"fields": ("meta_description", "meta_keywords", "og_image")}),
        (
            "Contact",
            {"fields": ("address", "phone", "email", "opening_hours", "google_maps_embed")},
        ),
        ("Social", {"fields": ("facebook", "instagram", "tiktok", "youtube")}),
    )

    def has_add_permission(self, request):
        # Singleton — only ever one row.
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    list_editable = ("is_read",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "artist", "style", "preferred_date", "status", "created_at")
    list_filter = ("status", "artist", "style", "created_at")
    search_fields = ("name", "email", "phone", "description")
    list_editable = ("status",)
    autocomplete_fields = ("artist", "style")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
