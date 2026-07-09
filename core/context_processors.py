from .models import SiteSetting, Language


def site_settings(request):
    """Expose the singleton :class:`SiteSetting` to every template as ``site``,
    along with language information for translation purposes.
    """
    # Seed default languages if the table is empty
    Language.load_defaults()
    
    # Get active languages list
    active_langs = list(Language.objects.filter(is_active=True))
    
    # Get current active language code from Django's active translation
    from django.utils import translation
    current_lang = translation.get_language()
    if current_lang:
        current_lang = current_lang.split("-")[0]
    else:
        current_lang = "ka"
    
    return {
        "site": SiteSetting.load(),
        "active_languages": active_langs,
        "current_language": current_lang,
        "is_home": False,
    }
