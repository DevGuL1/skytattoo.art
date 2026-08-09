from django.contrib import admin
from django.utils.html import format_html

from .models import PortfolioImage, PortfolioItem, TattooStyle


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 3


@admin.register(TattooStyle)
class TattooStyleAdmin(admin.ModelAdmin):
    list_display = ("swatch", "name", "slug", "order")
    list_display_links = ("swatch", "name")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    @admin.display(description="")
    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;height:16px;width:16px;border-radius:3px;'
            'background:{};border:1px solid #333;"></span>',
            obj.color,
        )


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "artist", "color", "size", "is_featured", "order")
    list_display_links = ("thumb", "title")
    list_editable = ("is_featured", "order")
    list_filter = ("is_featured", "color", "size", "styles", "artist")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("artist",)
    filter_horizontal = ("styles",)
    inlines = [PortfolioImageInline]

    @admin.display(description="")
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:44px;width:44px;object-fit:cover;'
                'border-radius:4px;" />',
                obj.image.url,
            )
        return "—"
