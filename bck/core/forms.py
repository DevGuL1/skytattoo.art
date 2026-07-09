from django import forms

from .models import BookingRequest, ContactMessage

# Shared Tailwind classes for the gothic form controls.
_INPUT = (
    "w-full bg-black/40 border border-neutral-700 focus:border-gold "
    "text-neutral-100 placeholder-neutral-500 rounded-md px-4 py-3 "
    "outline-none transition-colors"
)


class ContactForm(forms.ModelForm):
    # Simple honeypot: real users never fill a hidden field.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": _INPUT, "placeholder": "you@email.com"}),
            "phone": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Phone (optional)"}),
            "subject": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Subject"}),
            "message": forms.Textarea(
                attrs={"class": _INPUT, "rows": 5, "placeholder": "Tell us about your idea…"}
            ),
        }

    def __init__(self, *args, **kwargs):
        lang = kwargs.pop("language_code", "ka")
        super().__init__(*args, **kwargs)
        if lang == "ka":
            self.fields["name"].widget.attrs["placeholder"] = "თქვენი სახელი"
            self.fields["email"].widget.attrs["placeholder"] = "you@email.com"
            self.fields["phone"].widget.attrs["placeholder"] = "ტელეფონი (არასავალდებულო)"
            self.fields["subject"].widget.attrs["placeholder"] = "თემა"
            self.fields["message"].widget.attrs["placeholder"] = "გაგვიზიარეთ თქვენი იდეა…"
        elif lang == "ru":
            self.fields["name"].widget.attrs["placeholder"] = "Ваше имя"
            self.fields["email"].widget.attrs["placeholder"] = "you@email.com"
            self.fields["phone"].widget.attrs["placeholder"] = "Телефон (опционально)"
            self.fields["subject"].widget.attrs["placeholder"] = "Тема"
            self.fields["message"].widget.attrs["placeholder"] = "Расскажите о вашей идее…"

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""


class BookingForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = BookingRequest
        fields = ["name", "email", "phone", "artist", "style", "preferred_date", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": _INPUT, "placeholder": "you@email.com"}),
            "phone": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Phone"}),
            "artist": forms.Select(attrs={"class": _INPUT}),
            "style": forms.Select(attrs={"class": _INPUT}),
            "preferred_date": forms.DateInput(
                attrs={"class": _INPUT, "type": "date"}
            ),
            "description": forms.Textarea(
                attrs={"class": _INPUT, "rows": 4, "placeholder": "Describe your tattoo idea…"}
            ),
        }

    def __init__(self, *args, **kwargs):
        lang = kwargs.pop("language_code", "ka")
        super().__init__(*args, **kwargs)
        if lang == "ka":
            self.fields["name"].widget.attrs["placeholder"] = "თქვენი სახელი"
            self.fields["email"].widget.attrs["placeholder"] = "you@email.com"
            self.fields["phone"].widget.attrs["placeholder"] = "ტელეფონი"
            self.fields["description"].widget.attrs["placeholder"] = "აღწერეთ თქვენი ტატუს იდეა…"
            self.fields["artist"].empty_label = "აირჩიეთ არტისტი"
            self.fields["style"].empty_label = "აირჩიეთ სტილი"
        elif lang == "ru":
            self.fields["name"].widget.attrs["placeholder"] = "Ваше имя"
            self.fields["email"].widget.attrs["placeholder"] = "you@email.com"
            self.fields["phone"].widget.attrs["placeholder"] = "Телефон"
            self.fields["description"].widget.attrs["placeholder"] = "Опишите вашу идею для тату…"
            self.fields["artist"].empty_label = "Выберите мастера"
            self.fields["style"].empty_label = "Выберите стиль"

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""
