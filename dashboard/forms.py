"""Dashboard forms.

Every form derives from :class:`StyledForm` / :class:`StyledModelForm`, which
auto-applies the gothic Tailwind classes so individual widgets stay clean.
"""

from django import forms
from django.forms import inlineformset_factory

from artists.models import Artist, Reel, SocialPost
from core.models import BookingRequest, SiteSetting, StudioValue, Language, StaticString
from portfolio.models import PortfolioItem, TattooStyle

_TEXT = (
    "w-full bg-black/40 border border-neutral-700 focus:border-gold text-neutral-100 "
    "placeholder-neutral-500 rounded-md px-4 py-2.5 outline-none transition-colors"
)
_CHECK = "h-5 w-5 rounded border-neutral-600 bg-black/40 text-blood focus:ring-gold"


def _style(field):
    w = field.widget
    if isinstance(w, forms.CheckboxInput):
        w.attrs.setdefault("class", _CHECK)
    elif isinstance(w, forms.ClearableFileInput):
        w.attrs.setdefault(
            "class",
            "block w-full text-sm text-neutral-400 file:mr-4 file:py-2 file:px-4 "
            "file:rounded-md file:border-0 file:bg-blood file:text-white "
            "file:cursor-pointer hover:file:bg-bloodlight",
        )
    else:
        w.attrs.setdefault("class", _TEXT)
        if isinstance(w, forms.Textarea):
            w.attrs.setdefault("rows", 4)


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            _style(field)

    @property
    def translation_tabs(self):
        langs = getattr(self, "languages", [])
        tabs = []
        visible = list(self.visible_fields())
        
        # Standard database fields hold the base language (English)
        default_fields = []
        for field in visible:
            is_trans = False
            for lang in langs:
                if field.name.endswith(f"_{lang.code}"):
                    is_trans = True
                    break
            if not is_trans:
                default_fields.append(field)
                
        # Tab 1: English (base)
        tabs.append({
            "code": "en",
            "name": "English",
            "fields": default_fields,
            "is_default": True
        })
        
        # Custom languages (Georgian: ka, Russian: ru)
        for lang in langs:
            lang_fields = []
            for field in visible:
                if field.name.endswith(f"_{lang.code}"):
                    lang_fields.append(field)
            if lang_fields:
                tabs.append({
                    "code": lang.code,
                    "name": lang.name,
                    "fields": lang_fields,
                    "is_default": False
                })
        return tabs


class TranslatableModelForm(StyledModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translatable_fields = getattr(self.Meta, "translatable_fields", [])
        if not self.translatable_fields:
            return

        from core.models import Language, Translation

        self.languages = list(Language.objects.filter(is_active=True, is_default=False))

        for field_name in self.translatable_fields:
            if field_name not in self.fields:
                continue
            orig_field = self.fields[field_name]

            for lang in self.languages:
                trans_field_name = f"{field_name}_{lang.code}"

                if isinstance(orig_field.widget, forms.Textarea):
                    self.fields[trans_field_name] = forms.CharField(
                        widget=forms.Textarea(attrs=orig_field.widget.attrs),
                        required=False,
                        label=f"{orig_field.label} ({lang.name})",
                    )
                else:
                    self.fields[trans_field_name] = forms.CharField(
                        widget=forms.TextInput(attrs=orig_field.widget.attrs),
                        required=False,
                        label=f"{orig_field.label} ({lang.name})",
                    )

                # Style the dynamic translated field
                _style(self.fields[trans_field_name])

                # Load existing translations
                if self.instance and self.instance.pk:
                    key = f"{self.instance._meta.model_name}:{self.instance.pk}:{field_name}"
                    try:
                        trans_obj = Translation.objects.get(
                            language=lang, object_key=key
                        )
                        self.initial[trans_field_name] = trans_obj.text
                    except Translation.DoesNotExist:
                        pass

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if hasattr(self, "translatable_fields") and instance.pk:
            from core.models import Translation

            for field_name in self.translatable_fields:
                for lang in self.languages:
                    trans_field_name = f"{field_name}_{lang.code}"
                    val = self.cleaned_data.get(trans_field_name)
                    key = f"{instance._meta.model_name}:{instance.pk}:{field_name}"
                    if val is not None and val.strip() != "":
                        Translation.objects.update_or_create(
                            language=lang, object_key=key, defaults={"text": val}
                        )
                    else:
                        Translation.objects.filter(
                            language=lang, object_key=key
                        ).delete()
        return instance


# --------------------------------------------------------------------------
# SiteSetting — split into logical panels, all editing the same singleton row.
# --------------------------------------------------------------------------
class BrandingForm(TranslatableModelForm):
    class Meta:
        model = SiteSetting
        fields = ["site_name", "tagline", "about_short"]
        translatable_fields = ["site_name", "tagline", "about_short"]


class HeroForm(TranslatableModelForm):
    class Meta:
        model = SiteSetting
        fields = [
            "hero_eyebrow", "hero_title", "hero_title_accent", "hero_subtitle",
            "hero_bg", "hero_video", "cta_primary_label", "cta_secondary_label",
        ]
        translatable_fields = [
            "hero_eyebrow", "hero_title", "hero_title_accent", "hero_subtitle",
            "cta_primary_label", "cta_secondary_label",
        ]


class HomeSectionsForm(TranslatableModelForm):
    class Meta:
        model = SiteSetting
        fields = [
            "featured_eyebrow", "featured_title", "show_featured",
            "artists_eyebrow", "artists_title", "show_artists_teaser",
            "show_styles_strip",
            "cta_band_title", "cta_band_text", "cta_band_label",
        ]
        translatable_fields = [
            "featured_eyebrow", "featured_title", "artists_eyebrow", "artists_title",
            "cta_band_title", "cta_band_text", "cta_band_label",
        ]


class AboutForm(TranslatableModelForm):
    class Meta:
        model = SiteSetting
        fields = ["about_eyebrow", "about_title", "about_story"]
        translatable_fields = ["about_eyebrow", "about_title", "about_story"]


class SeoForm(StyledModelForm):
    class Meta:
        model = SiteSetting
        fields = ["meta_description", "meta_keywords", "og_image"]


class ContactInfoForm(StyledModelForm):
    class Meta:
        model = SiteSetting
        fields = ["address", "phone", "email", "opening_hours", "google_maps_embed"]


class SocialForm(StyledModelForm):
    class Meta:
        model = SiteSetting
        fields = ["facebook", "instagram", "tiktok", "youtube"]


class FloatButtonForm(StyledModelForm):
    class Meta:
        model = SiteSetting
        fields = [
            "show_float_button",
            "float_whatsapp",
            "float_facebook",
            "float_instagram",
            "float_email",
        ]


# --------------------------------------------------------------------------
# Content models
# --------------------------------------------------------------------------
class ArtistForm(TranslatableModelForm):
    class Meta:
        model = Artist
        fields = [
            "name", "role", "tagline", "bio", "avatar", "cover_image", "styles",
            "instagram", "facebook", "tiktok", "email", "is_active", "order",
        ]
        widgets = {"styles": forms.CheckboxSelectMultiple}
        translatable_fields = ["role", "tagline", "bio"]


class ReelForm(StyledModelForm):
    class Meta:
        model = Reel
        fields = ["title", "provider", "video_url", "thumbnail", "order"]


ReelFormSet = inlineformset_factory(
    Artist, Reel, form=ReelForm, extra=1, can_delete=True,
)


class SocialPostForm(StyledModelForm):
    class Meta:
        model = SocialPost
        fields = ["url", "caption", "order"]
        widgets = {
            "url": forms.URLInput(attrs={
                "placeholder": "https://www.instagram.com/reel/…  or  https://www.tiktok.com/@user/video/…"
            }),
        }


SocialPostFormSet = inlineformset_factory(
    Artist, SocialPost, form=SocialPostForm, extra=1, can_delete=True,
)


class PortfolioItemForm(TranslatableModelForm):
    class Meta:
        model = PortfolioItem
        fields = [
            "title", "image", "artist", "styles", "description",
            "color", "size", "is_featured", "order",
        ]
        widgets = {"styles": forms.CheckboxSelectMultiple}
        translatable_fields = ["title", "description"]


class TattooStyleForm(TranslatableModelForm):
    class Meta:
        model = TattooStyle
        fields = ["name", "color", "description", "order"]
        widgets = {"color": forms.TextInput(attrs={"type": "color"})}
        translatable_fields = ["name", "description"]


class StudioValueForm(TranslatableModelForm):
    class Meta:
        model = StudioValue
        fields = ["title", "text", "order"]
        translatable_fields = ["title", "text"]


class BookingStatusForm(StyledModelForm):
    class Meta:
        model = BookingRequest
        fields = ["status"]


# --------------------------------------------------------------------------
# Language Forms
# --------------------------------------------------------------------------
class LanguageForm(StyledModelForm):
    class Meta:
        model = Language
        fields = ["code", "name", "is_default", "is_active", "order"]


# --------------------------------------------------------------------------
# Static String Translation Forms
# --------------------------------------------------------------------------
class StaticStringForm(TranslatableModelForm):
    class Meta:
        model = StaticString
        fields = ["key"]
        translatable_fields = ["key"]
