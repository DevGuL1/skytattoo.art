from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("", views.overview, name="overview"),

    # Site content
    path("homepage/", views.home_settings, name="home_settings"),
    path("about/", views.about_settings, name="about_settings"),
    path("branding/", views.branding_settings, name="branding_settings"),
    path("contact/", views.contact_settings, name="contact_settings"),

    # Artists
    path("artists/", views.artist_list, name="artist_list"),
    path("artists/new/", views.artist_edit, name="artist_create"),
    path("artists/<int:pk>/", views.artist_edit, name="artist_edit"),
    path("artists/<int:pk>/delete/", views.artist_delete, name="artist_delete"),

    # Portfolio
    path("portfolio/", views.portfolio_list, name="portfolio_list"),
    path("portfolio/new/", views.portfolio_edit, name="portfolio_create"),
    path("portfolio/bulk-delete/", views.portfolio_bulk_delete, name="portfolio_bulk_delete"),
    path("portfolio/<int:pk>/", views.portfolio_edit, name="portfolio_edit"),
    path("portfolio/<int:pk>/delete/", views.portfolio_delete, name="portfolio_delete"),

    # Styles
    path("styles/", views.style_list, name="style_list"),
    path("styles/new/", views.style_edit, name="style_create"),
    path("styles/<int:pk>/", views.style_edit, name="style_edit"),
    path("styles/<int:pk>/delete/", views.style_delete, name="style_delete"),

    # Studio values (About cards)
    path("values/new/", views.value_edit, name="value_create"),
    path("values/<int:pk>/", views.value_edit, name="value_edit"),
    path("values/<int:pk>/delete/", views.value_delete, name="value_delete"),

    # Bookings
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/<int:pk>/status/", views.booking_update, name="booking_update"),
    path("bookings/<int:pk>/delete/", views.booking_delete, name="booking_delete"),

    # Messages
    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:pk>/toggle/", views.message_toggle, name="message_toggle"),
    path("messages/<int:pk>/delete/", views.message_delete, name="message_delete"),

    # Languages
    path("languages/", views.language_list, name="language_list"),
    path("languages/new/", views.language_edit, name="language_create"),
    path("languages/<int:pk>/", views.language_edit, name="language_edit"),
    path("languages/<int:pk>/delete/", views.language_delete, name="language_delete"),

    # Static UI Strings
    path("strings/", views.static_string_list, name="static_string_list"),
    path("strings/new/", views.static_string_edit, name="static_string_create"),
    path("strings/<int:pk>/", views.static_string_edit, name="static_string_edit"),
    path("strings/<int:pk>/delete/", views.static_string_delete, name="static_string_delete"),

    # Instagram Sync & Checker
    path("instagram/", views.instagram_checker, name="instagram_checker"),
    path("instagram/sync/", views.instagram_sync_now, name="instagram_sync_now"),
]
