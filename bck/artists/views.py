from django.shortcuts import get_object_or_404, render

from portfolio.models import TattooStyle

from .models import Artist


def artist_list(request):
    artists = (
        Artist.objects.filter(is_active=True).prefetch_related("styles")
    )
    return render(
        request,
        "artists/list.html",
        {"artists": artists, "styles": TattooStyle.objects.all()},
    )


def artist_detail(request, slug):
    """Personal mini-site for one artist: bio, filterable portfolio, reels."""
    artist = get_object_or_404(
        Artist.objects.prefetch_related("styles", "reels"),
        slug=slug,
        is_active=True,
    )
    items = (
        artist.portfolio_items.all()
        .prefetch_related("styles")
        .select_related("artist")
    )
    # Only show style filters that this artist actually has work in.
    styles = TattooStyle.objects.filter(portfolio_items__artist=artist).distinct()
    return render(
        request,
        "artists/detail.html",
        {"artist": artist, "items": items, "styles": styles},
    )
