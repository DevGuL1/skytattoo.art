from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.conf import settings
from django.utils import translation

from artists.models import Artist
from portfolio.models import PortfolioItem, TattooStyle

from .forms import BookingForm, ContactForm


def home(request):
    """Homepage: hero, featured portfolio, artist teaser."""
    featured = (
        PortfolioItem.objects.filter(is_featured=True)
        .select_related("artist")
        .prefetch_related("styles")[:8]
    )
    if not featured:
        # Fall back to the most recent work so the grid is never empty.
        featured = (
            PortfolioItem.objects.select_related("artist")
            .prefetch_related("styles")[:8]
        )
    lang_code = translation.get_language().split("-")[0] if translation.get_language() else "ka"
    context = {
        "featured": featured,
        "artists": Artist.objects.filter(is_active=True)[:4],
        "styles": TattooStyle.objects.all(),
        "booking_form": BookingForm(language_code=lang_code),
    }
    return render(request, "core/home.html", context)


def about(request):
    from core.models import StudioValue

    values = list(StudioValue.objects.all())
    if not values:
        # Sensible defaults until the studio adds its own value cards.
        values = [
            {"title": "Bespoke Design", "text": "Every piece is drawn from scratch for you — no flash repeats, no shortcuts."},
            {"title": "Sterile & Safe", "text": "Single-use needles, hospital-grade sterilisation and a spotless private studio."},
            {"title": "Dark Craft", "text": "Blackwork, realism and gothic linework are our obsession, honed over years."},
        ]
    return render(
        request,
        "core/about.html",
        {"artists": Artist.objects.filter(is_active=True), "values": values},
    )


def contact(request):
    lang_code = translation.get_language().split("-")[0] if translation.get_language() else "ka"
    if request.method == "POST":
        form = ContactForm(request.POST, language_code=lang_code)
        if form.is_valid() and _recaptcha_ok(request):
            form.save()
            _notify(
                subject=f"[Skytattoo] Contact: {form.cleaned_data.get('subject') or 'New message'}",
                body=(
                    f"From: {form.cleaned_data['name']} <{form.cleaned_data['email']}>\n"
                    f"Phone: {form.cleaned_data.get('phone')}\n\n"
                    f"{form.cleaned_data['message']}"
                ),
            )
            messages.success(
                request, "Thank you — your message has been sent. We'll be in touch soon."
            )
            return redirect("core:contact")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm(language_code=lang_code)
    return render(
        request,
        "core/contact.html",
        {"form": form, "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY},
    )


def book(request):
    """Handle the 'Book Appointment' form (posted from the homepage/CTA)."""
    lang_code = translation.get_language().split("-")[0] if translation.get_language() else "ka"
    if request.method == "POST":
        form = BookingForm(request.POST, language_code=lang_code)
        if form.is_valid():
            booking = form.save()
            _notify(
                subject="[Skytattoo] New booking request",
                body=(
                    f"Name: {booking.name} <{booking.email}>\n"
                    f"Phone: {booking.phone}\n"
                    f"Artist: {booking.artist}\n"
                    f"Style: {booking.style}\n"
                    f"Preferred date: {booking.preferred_date}\n\n"
                    f"{booking.description}"
                ),
            )
            messages.success(
                request, "Your booking request is in. We'll confirm your appointment shortly."
            )
            return redirect("core:home")
        messages.error(request, "Please check the booking form and try again.")
        return render(request, "core/book.html", {"booking_form": form})
    return render(request, "core/book.html", {"booking_form": BookingForm(language_code=lang_code)})


def _recaptcha_ok(request):
    """Verify Google reCAPTCHA if a secret key is configured; else pass."""
    secret = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    if not secret:
        return True
    token = request.POST.get("g-recaptcha-response", "")
    if not token:
        return False
    try:
        import urllib.parse
        import urllib.request

        data = urllib.parse.urlencode(
            {"secret": secret, "response": token, "remoteip": request.META.get("REMOTE_ADDR")}
        ).encode()
        with urllib.request.urlopen(
            "https://www.google.com/recaptcha/api/siteverify", data=data, timeout=5
        ) as resp:
            import json

            return json.loads(resp.read().decode()).get("success", False)
    except Exception:
        # Don't lock users out if Google is unreachable.
        return True


def _notify(subject, body):
    """Best-effort email notification; never blocks the user on failure."""
    recipient = getattr(settings, "CONTACT_NOTIFY_EMAIL", None)
    if not recipient:
        return
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=True,
        )
    except Exception:
        pass
