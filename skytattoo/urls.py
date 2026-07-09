"""URL configuration for the Skytattoo.art project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Gothic-themed admin branding.
admin.site.site_header = "Skytattoo.art — Studio Dashboard"
admin.site.site_title = "Skytattoo.art Admin"
admin.site.index_title = "Manage artists, portfolio, reels & bookings"

from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
]

# Public SEO prefix-wrapped routes
urlpatterns += i18n_patterns(
    path("artists/", include("artists.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("", include("core.urls")),
    prefix_default_language=True,
)

# Serve user-uploaded media in development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
