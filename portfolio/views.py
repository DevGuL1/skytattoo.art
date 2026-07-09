from django.shortcuts import get_object_or_404, render

from .models import PortfolioItem, TattooStyle


def portfolio_list(request):
    """Studio portfolio with tag-based, animated filtering (Isotope)."""
    items = (
        PortfolioItem.objects.select_related("artist").prefetch_related("styles")
    )
    context = {
        "items": items,
        "styles": TattooStyle.objects.all(),
        "colors": PortfolioItem.Color.choices,
        "sizes": PortfolioItem.Size.choices,
    }
    return render(request, "portfolio/list.html", context)


def portfolio_detail(request, slug):
    item = get_object_or_404(
        PortfolioItem.objects.select_related("artist").prefetch_related("styles"),
        slug=slug,
    )
    related = (
        PortfolioItem.objects.filter(styles__in=item.styles.all())
        .exclude(pk=item.pk)
        .distinct()[:4]
    )
    return render(
        request,
        "portfolio/detail.html",
        {"item": item, "related": related},
    )
