"""Skytattoo.art custom dashboard — a gothic control panel for the whole site."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from artists.models import Artist, Reel
from core.models import BookingRequest, ContactMessage, SiteSetting, StudioValue
from portfolio.models import PortfolioItem, TattooStyle

from . import forms as f


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return redirect(f"{reverse('dashboard:login')}?next={request.path}")
        return view(request, *args, **kwargs)

    return wrapper


def nav_counts():
    from core.models import Language, StaticString
    return {
        "count_artists": Artist.objects.count(),
        "count_portfolio": PortfolioItem.objects.count(),
        "count_styles": TattooStyle.objects.count(),
        "count_bookings_new": BookingRequest.objects.filter(status="new").count(),
        "count_messages_unread": ContactMessage.objects.filter(is_read=False).count(),
        "count_languages": Language.objects.count(),
        "count_static_strings": StaticString.objects.count(),
    }


SECTION_BY_VIEW = {
    "overview": "overview",
    "home_settings": "home",
    "about_settings": "about",
    "branding_settings": "branding",
    "contact_settings": "contact",
    "artist_list": "artists",
    "artist_create": "artists",
    "artist_edit": "artists",
    "portfolio_list": "portfolio",
    "portfolio_create": "portfolio",
    "portfolio_edit": "portfolio",
    "style_list": "styles",
    "style_create": "styles",
    "style_edit": "styles",
    "value_create": "about",
    "value_edit": "about",
    "booking_list": "bookings",
    "message_list": "messages",
    "language_list": "languages",
    "language_create": "languages",
    "language_edit": "languages",
    "static_string_list": "strings",
    "static_string_create": "strings",
    "static_string_edit": "strings",
    "instagram_checker": "instagram",
}


def dash_render(request, template, ctx=None):
    data = {**nav_counts()}
    if request.resolver_match:
        data["dashboard_section"] = SECTION_BY_VIEW.get(request.resolver_match.url_name, "")
    if ctx:
        data.update(ctx)
    return render(request, template, data)


# ---------------------------------------------------------------------------
# Login / logout
# ---------------------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard:overview")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not user.is_staff:
            messages.error(request, "This account can't access the dashboard.")
        else:
            login(request, user)
            return redirect(request.GET.get("next") or "dashboard:overview")
    return render(request, "dashboard/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("dashboard:login")


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
@staff_required
def overview(request):
    from core.models import Language, StaticString
    ctx = {
        "stats": {
            "artists": Artist.objects.count(),
            "portfolio": PortfolioItem.objects.count(),
            "styles": TattooStyle.objects.count(),
            "reels": Reel.objects.count(),
            "bookings": BookingRequest.objects.count(),
            "messages": ContactMessage.objects.count(),
            "languages": Language.objects.count(),
            "static_strings": StaticString.objects.count(),
        },
        "recent_bookings": BookingRequest.objects.select_related("artist")[:6],
        "recent_messages": ContactMessage.objects.all()[:6],
        "featured_count": PortfolioItem.objects.filter(is_featured=True).count(),
        "top_styles": TattooStyle.objects.annotate(n=Count("portfolio_items")).order_by("-n")[:5],
        "recent_items": PortfolioItem.objects.select_related("artist").prefetch_related("styles")[:6],
    }
    return dash_render(request, "dashboard/overview.html", ctx)


# ---------------------------------------------------------------------------
# Settings pages (all edit the SiteSetting singleton)
# ---------------------------------------------------------------------------
def _settings_page(request, template, title, form_specs):
    """Render/save one or more forms that all edit the SiteSetting singleton.

    ``form_specs`` is a list of (prefix, FormClass) tuples.
    """
    site = SiteSetting.load()
    built = []
    for prefix, FormClass in form_specs:
        if request.method == "POST":
            built.append((prefix, FormClass(request.POST, request.FILES, instance=site, prefix=prefix)))
        else:
            built.append((prefix, FormClass(instance=site, prefix=prefix)))

    if request.method == "POST":
        if all(form.is_valid() for _, form in built):
            for _, form in built:
                form.save()
            messages.success(request, "Changes saved.")
            return redirect(request.path)
        messages.error(request, "Please correct the highlighted fields.")

    return dash_render(request, template, {"title": title, "forms": dict(built), "site": site})


@staff_required
def home_settings(request):
    return _settings_page(
        request, "dashboard/settings_home.html", "Homepage",
        [("hero", f.HeroForm), ("sections", f.HomeSectionsForm), ("portfolio", f.PortfolioDisplayForm)],
    )


@staff_required
def about_settings(request):
    site = SiteSetting.load()
    form = f.AboutForm(request.POST or None, instance=site, prefix="about")
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "About page saved.")
        return redirect("dashboard:about_settings")
    return dash_render(
        request, "dashboard/settings_about.html",
        {"title": "About page", "form": form, "values": StudioValue.objects.all()},
    )


@staff_required
def branding_settings(request):
    return _settings_page(
        request, "dashboard/settings_generic.html", "Branding & SEO",
        [("branding", f.BrandingForm), ("seo", f.SeoForm)],
    )


@staff_required
def contact_settings(request):
    return _settings_page(
        request, "dashboard/settings_generic.html", "Contact, Social & Float Button",
        [
            ("contact", f.ContactInfoForm),
            ("social", f.SocialForm),
            ("float_button", f.FloatButtonForm),
        ],
    )


# ---------------------------------------------------------------------------
# CRUD — Artists (with reels inline)
# ---------------------------------------------------------------------------
@staff_required
def artist_list(request):
    return dash_render(request, "dashboard/artist_list.html",
                       {"artists": Artist.objects.prefetch_related("styles")})


@staff_required
def artist_edit(request, pk=None):
    artist = get_object_or_404(Artist, pk=pk) if pk else Artist()
    if request.method == "POST":
        form = f.ArtistForm(request.POST, request.FILES, instance=artist)
        formset = f.ReelFormSet(request.POST, request.FILES, instance=artist)
        social = f.SocialPostFormSet(request.POST, instance=artist)
        if form.is_valid() and formset.is_valid() and social.is_valid():
            obj = form.save()
            formset.instance = obj
            formset.save()
            social.instance = obj
            social.save()
            messages.success(request, "Artist saved.")
            return redirect("dashboard:artist_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = f.ArtistForm(instance=artist)
        formset = f.ReelFormSet(instance=artist)
        social = f.SocialPostFormSet(instance=artist)
    return dash_render(request, "dashboard/artist_form.html",
                       {"form": form, "formset": formset, "social": social,
                        "artist": artist if pk else None,
                        "cancel_url": reverse("dashboard:artist_list"),
                        "submit_label": "Save artist"})


@staff_required
def artist_delete(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    if request.method == "POST":
        artist.delete()
        messages.success(request, "Artist deleted.")
    return redirect("dashboard:artist_list")


# ---------------------------------------------------------------------------
# CRUD — Portfolio
# ---------------------------------------------------------------------------
@staff_required
def portfolio_list(request):
    return dash_render(request, "dashboard/portfolio_list.html",
                       {"items": PortfolioItem.objects.select_related("artist").prefetch_related("styles")})


@staff_required
def portfolio_edit(request, pk=None):
    item = get_object_or_404(PortfolioItem, pk=pk) if pk else PortfolioItem()
    if request.method == "POST":
        form = f.PortfolioItemForm(request.POST, request.FILES, instance=item)
        gallery = f.PortfolioImageFormSet(request.POST, request.FILES, instance=item)
        if form.is_valid() and gallery.is_valid():
            obj = form.save()
            gallery.instance = obj
            gallery.save()
            messages.success(request, "Portfolio item saved.")
            return redirect("dashboard:portfolio_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = f.PortfolioItemForm(instance=item)
        gallery = f.PortfolioImageFormSet(instance=item)
    return dash_render(request, "dashboard/portfolio_form.html",
                       {"form": form, "gallery": gallery, "item": item if pk else None,
                        "cancel_url": reverse("dashboard:portfolio_list"),
                        "submit_label": "Save portfolio item"})


@staff_required
def portfolio_delete(request, pk):
    item = get_object_or_404(PortfolioItem, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Portfolio item deleted.")
    return redirect("dashboard:portfolio_list")


# ---------------------------------------------------------------------------
# CRUD — Styles
# ---------------------------------------------------------------------------
@staff_required
def style_list(request):
    return dash_render(request, "dashboard/style_list.html",
                       {"styles": TattooStyle.objects.annotate(n=Count("portfolio_items"))})


@staff_required
def style_edit(request, pk=None):
    style = get_object_or_404(TattooStyle, pk=pk) if pk else TattooStyle()
    form = f.TattooStyleForm(request.POST or None, instance=style)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Style saved.")
        return redirect("dashboard:style_list")
    return dash_render(request, "dashboard/style_form.html", {
        "form": form,
        "style": style if pk else None,
        "cancel_url": reverse("dashboard:style_list"),
        "submit_label": "Save style",
    })


@staff_required
def style_delete(request, pk):
    style = get_object_or_404(TattooStyle, pk=pk)
    if request.method == "POST":
        style.delete()
        messages.success(request, "Style deleted.")
    return redirect("dashboard:style_list")


# ---------------------------------------------------------------------------
# CRUD — Studio values (About page cards)
# ---------------------------------------------------------------------------
@staff_required
def value_edit(request, pk=None):
    value = get_object_or_404(StudioValue, pk=pk) if pk else StudioValue()
    form = f.StudioValueForm(request.POST or None, instance=value)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Value saved.")
        return redirect("dashboard:about_settings")
    return dash_render(request, "dashboard/value_form.html", {
        "form": form,
        "value": value if pk else None,
        "cancel_url": reverse("dashboard:about_settings"),
        "submit_label": "Save value card",
    })


@staff_required
def value_delete(request, pk):
    value = get_object_or_404(StudioValue, pk=pk)
    if request.method == "POST":
        value.delete()
        messages.success(request, "Value deleted.")
    return redirect("dashboard:about_settings")


# ---------------------------------------------------------------------------
# Bookings & messages
# ---------------------------------------------------------------------------
@staff_required
def booking_list(request):
    return dash_render(request, "dashboard/booking_list.html", {
        "bookings": BookingRequest.objects.select_related("artist", "style"),
        "statuses": BookingRequest.Status.choices,
    })


@staff_required
def booking_update(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk)
    if request.method == "POST":
        status = request.POST.get("status")
        if status in dict(BookingRequest.Status.choices):
            booking.status = status
            booking.save(update_fields=["status"])
            messages.success(request, f"Booking marked '{booking.get_status_display()}'.")
    return redirect("dashboard:booking_list")


@staff_required
def booking_delete(request, pk):
    booking = get_object_or_404(BookingRequest, pk=pk)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking deleted.")
    return redirect("dashboard:booking_list")


@staff_required
def message_list(request):
    return dash_render(request, "dashboard/message_list.html",
                       {"messages_list": ContactMessage.objects.all()})


@staff_required
def message_toggle(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        msg.is_read = not msg.is_read
        msg.save(update_fields=["is_read"])
    return redirect("dashboard:message_list")


@staff_required
def message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        msg.delete()
        messages.success(request, "Message deleted.")
    return redirect("dashboard:message_list")


# ---------------------------------------------------------------------------
# CRUD — Languages
# ---------------------------------------------------------------------------
@staff_required
def language_list(request):
    from core.models import Language
    return dash_render(request, "dashboard/language_list.html",
                       {"languages": Language.objects.all()})


@staff_required
def language_edit(request, pk=None):
    from core.models import Language
    lang = get_object_or_404(Language, pk=pk) if pk else Language()
    form = f.LanguageForm(request.POST or None, instance=lang)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Language saved successfully.")
        return redirect("dashboard:language_list")
    return dash_render(request, "dashboard/language_form.html",
                       {"form": form, "lang": lang if pk else None,
                        "cancel_url": reverse("dashboard:language_list"),
                        "submit_label": "Save language"})


@staff_required
def language_delete(request, pk):
    from core.models import Language
    lang = get_object_or_404(Language, pk=pk)
    if request.method == "POST":
        if lang.is_default:
            messages.error(request, "Cannot delete the default language.")
        else:
            lang.delete()
            messages.success(request, "Language deleted.")
    return redirect("dashboard:language_list")


# ---------------------------------------------------------------------------
# CRUD — Static UI Strings
# ---------------------------------------------------------------------------
@staff_required
def static_string_list(request):
    from core.models import StaticString
    q = request.GET.get("q", "").strip()
    strings = StaticString.objects.all()
    if q:
        strings = strings.filter(key__icontains=q)
    return dash_render(request, "dashboard/static_string_list.html",
                       {"strings": strings, "q": q})


@staff_required
def static_string_edit(request, pk=None):
    from core.models import StaticString
    string_obj = get_object_or_404(StaticString, pk=pk) if pk else StaticString()
    form = f.StaticStringForm(request.POST or None, instance=string_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Static string translation saved.")
        return redirect("dashboard:static_string_list")
    return dash_render(request, "dashboard/static_string_form.html",
                       {"form": form, "string": string_obj if pk else None,
                        "cancel_url": reverse("dashboard:static_string_list"),
                        "submit_label": "Save string"})


@staff_required
def static_string_delete(request, pk):
    from core.models import StaticString
    string_obj = get_object_or_404(StaticString, pk=pk)
    if request.method == "POST":
        string_obj.delete()
        messages.success(request, "Static string translation deleted.")
    return redirect("dashboard:static_string_list")


# ---------------------------------------------------------------------------
# Instagram Checker & Sync Module
# ---------------------------------------------------------------------------
@staff_required
def instagram_checker(request):
    from dashboard.models import InstagramSyncConfig, InstagramSyncLog
    from portfolio.services.instagram_checker import InstagramCheckerService

    config = InstagramSyncConfig.get_solo()
    config_form = f.InstagramSyncConfigForm(request.POST or None, instance=config)

    if request.method == "POST":
        if "save_config" in request.POST:
            if config_form.is_valid():
                cfg = config_form.save()
                site = SiteSetting.objects.first()
                if site:
                    if cfg.instagram_account_url:
                        site.instagram = cfg.instagram_account_url
                    if cfg.facebook_page_url:
                        site.facebook = cfg.facebook_page_url
                    site.save()
                messages.success(request, "Instagram & Facebook სინქრონიზაციის პარამეტრები შენახულია.")
                return redirect("dashboard:instagram_checker")
        elif "save_artist_tags" in request.POST:
            for artist in Artist.objects.filter(is_active=True):
                ht_key = f"artist_tag_{artist.pk}"
                un_key = f"artist_username_{artist.pk}"
                if ht_key in request.POST:
                    artist.instagram_hashtag = request.POST[ht_key].strip().lstrip("#")
                if un_key in request.POST:
                    artist.instagram_username = request.POST[un_key].strip().lstrip("@")
                artist.save()
            messages.success(request, "არტისტების Instagram ჰეშტეგები და Username-ები შენახულია.")
            return redirect("dashboard:instagram_checker")
        elif "import_post" in request.POST:
            post_url = request.POST.get("post_url", "").strip()
            image_url = request.POST.get("image_url", "").strip()
            caption = request.POST.get("caption", "").strip()
            source = request.POST.get("source", "instagram").strip()
            success, msg = InstagramCheckerService.import_single_post_url(post_url=post_url, image_url=image_url, caption=caption, source=source)
            if success:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
            return redirect("dashboard:instagram_checker")

    from django.db.models import Q
    logs = InstagramSyncLog.objects.all()[:15]
    synced_items = PortfolioItem.objects.filter(
        Q(is_from_instagram=True) | Q(is_from_facebook=True)
    ).select_related("artist")[:30]
    artists_with_tags = Artist.objects.filter(is_active=True)

    return dash_render(
        request,
        "dashboard/instagram_checker.html",
        {
            "config": config,
            "config_form": config_form,
            "logs": logs,
            "synced_items": synced_items,
            "artists_with_tags": artists_with_tags,
        },
    )


@staff_required
def instagram_sync_now(request):
    from portfolio.services.instagram_checker import InstagramCheckerService

    if request.method == "POST":
        res = InstagramCheckerService.run_full_sync()
        if res.get("success"):
            messages.success(
                request,
                f"Instagram შემოწმება დასრულდა! წამოღებულია {res['posts_fetched']} პოსტი, შეიქმნა {res['items_created']} ახალი ნამუშევარი."
            )
        else:
            messages.error(request, f"შემოწმების შეცდომა: {res.get('details')}")

    return redirect("dashboard:instagram_checker")

