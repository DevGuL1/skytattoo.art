from django import template
from django.utils import translation

register = template.Library()

# Out-of-the-box translation defaults for auto-seeded static UI texts
STATIC_TEXTS_FALLBACK = {
    "ka": {
        "Home": "მთავარი",
        "Artists": "არტისტები",
        "Portfolio": "პორტფოლიო",
        "About": "ჩვენს შესახებ",
        "Contact": "კონტაქტი",
        "Book Appointment": "ჩაწერა",
        "Meet Our Artists": "ჩვენი არტისტები",
        "View Full Portfolio": "სრული პორტფოლიო",
        "Explore": "ნავიგაცია",
        "Studio": "სტუდია",
        "Ready for your next piece?": "მზად ხართ შემდეგი ტატუსთვის?",
        "Latest Ink": "ბოლო ნამუშევრები",
        "Featured Portfolio": "რჩეული პორტფოლიო",
        "The Coven": "გუნდი",
        "Booking coming soon": "ჩაწერა მალე დაემატება",
        "Portfolio coming soon": "პორტფოლიო მალე დაემატება",
        "Your name": "სახელი",
        "Phone (optional)": "ტელეფონი (არასავალდებულო)",
        "Tell us about your idea…": "გაგვიზიარეთ თქვენი იდეა…",
        "Submit": "გაგზავნა",
        "Send message": "გაგზავნა",
        "Message": "შეტყობინება",
        "Phone": "ტელეფონი",
        "Email": "ელ-ფოსტა",
        "Subject": "თემა",
        "Our Story": "ჩვენი ისტორია",
        "About the Studio": "სტუდიის შესახებ",
        "Book a consultation with one of our artists and let's design something eternal.": "ჩაეწერეთ კონსულტაციაზე ჩვენს არტისტებთან და ერთად შევქმნათ მარადიული ხელოვნება.",
        "Your name…": "თქვენი სახელი…",
        "you@email.com": "you@email.com",
        "Describe your tattoo idea…": "აღწერეთ თქვენი ტატუს იდეა…",
        "Style": "სტილი",
        "Preferred date": "სასურველი თარიღი",
        "Select Artist": "აირჩიეთ არტისტი",
        "Select Style": "აირჩიეთ სტილი",
        "Find Us": "სად ვართ",
        "Address": "მისამართი",
        "Opening Hours": "სამუშაო საათები",
        "Book Now": "ჩაეწერე ახლავე",
        "Portfolio coming soon — check back for fresh ink.": "პორტფოლიო მალე დაემატება — თვალი ადევნეთ სიახლეებს.",
        "by": "ავტორი",
        "Cancel": "გაუქმება",
        "Book a Consultation": "კონსულტაციაზე ჩაწერა",
        "All Styles": "ყველა სტილი",
        "All": "ყველა",
        "Studio Works": "სტუდიის ნამუშევრები",
        "No work matches these filters.": "მოცემული ფილტრით ნამუშევრები ვერ მოიძებნა.",
        "Gothic Tattoo Studio · Tbilisi": "გოთიკური ტატუ სტუდია · თბილისი",
        "Gothic ink. Timeless art.": "გოთიკური მელანი. მარადიული ხელოვნება.",
        "Let's create something eternal.": "შევქმნათ რაღაც მარადიული.",
        "Gothic ink. Timeless art. — where dark artistry becomes permanent.": "გოთიკური მელანი. მარადიული ხელოვნება. — სადაც ბნელი ხელოვნება ხდება მუდმივი.",
        "tattoo artist at Skytattoo.art.": "ტატუ არტისტი Skytattoo.art-ზე.",
        "The story of Skytattoo.art — a gothic tattoo studio and the artists behind the ink.": "Skytattoo.art-ის ისტორია — გოთიკური ტატუ სტუდია და არტისტები მელნის მიღმა.",
        "Get in touch with Skytattoo.art — visit the studio, send a message or book a consultation.": "დაუკავშირდით Skytattoo.art-ს — ეწვიეთ სტუდიას, გამოგვიგზავნეთ შეტყობინება ან ჩაეწერეთ კონსულტაციაზე.",
        "Book your tattoo appointment at Skytattoo.art — choose an artist, a style and a date.": "ჩაეწერეთ ტატუზე Skytattoo.art-ზე — აირჩიეთ არტისტი, სტილი და სასურველი თარიღი.",
        "Explore the Skytattoo.art studio portfolio — blackwork, realism, minimal and gothic tattoos, filterable by style, colour and size.": "დაათვალიერეთ Skytattoo.art-ის პორტფოლიო — გოთიკური, მინიშნებითი, რეალისტური და ბლექ ვორქ ტატუები ფილტრებით.",
        "Meet the tattoo artists of Skytattoo.art — resident masters of blackwork, realism, minimal and gothic ink.": "გაიცანით Skytattoo.art-ის ტატუ არტისტები — ბლექ ვორქის, რეალიზმის და გოთიკური მელნის ოსტატები.",
        "Each artist keeps their own space — a personal profile with bio, portfolio and reels.": "თითოეულ არტისტს აქვს საკუთარი გვერდი — პირადი პროფილი ბიოგრაფიით, პორტფოლიოთი და ვიდეოებით.",
        "Tell us who you'd like to work with and what you have in mind. We'll get back to you to confirm.": "გვითხარით, რომელ არტისტთან გსურთ თანამშრომლობა და რა გაქვთ ჩაფიქრებული. ჩვენ მალე დაგიკავშირდებით დასადასტურებლად.",
        "About": "ჩვენს შესახებ",
        "Role": "როლი",
        "Back to portfolio": "პორტფოლიოში დაბრუნება",
        "Book this style": "ჩაწერა",
        "Related Work": "მსგავსი ნამუშევრები",
        "Follow the Ink": "გამოგვიყევით",
        "Social Feed": "სოციალური ქსელი",
        "Follow on Instagram": "გამოგვიყევით Instagram-ზე",
        "Follow on TikTok": "გამოგვიყევით TikTok-ზე",
        "In Motion": "მოძრაობაში",
        "Video Reels": "ვიდეოები",
        "Dashboard Login": "დეშბორდი",
        "Enter Coven": "შესვლა",
        "All rights reserved.": "ყველა უფლება დაცულია.",
        "The Team": "გუნდი",
        "Get In Touch": "დაგვიკავშირდით",
        "Send a message": "შეტყობინების გაგზავნა",
        "Visit the studio": "ეწვიეთ სტუდიას",
        "Map — add a Google Maps embed in the admin.": "რუკა — დაამატეთ Google Maps embed დეშბორდიდან.",
    },
    "ru": {
        "Home": "Главная",
        "Artists": "Мастера",
        "Portfolio": "Портфолио",
        "About": "О нас",
        "Contact": "Контакты",
        "Book Appointment": "Запись",
        "Meet Our Artists": "Наши Мастера",
        "View Full Portfolio": "Все Портфолио",
        "Explore": "Навигация",
        "Studio": "Студия",
        "Ready for your next piece?": "Готовы к новому тату?",
        "Latest Ink": "Новое",
        "Featured Portfolio": "Рекомендуемое",
        "The Coven": "Команда",
        "Booking coming soon": "Запись скоро",
        "Portfolio coming soon": "Портфолио скоро",
        "Your name": "Ваше имя",
        "Phone (optional)": "Телефон (необязательно)",
        "Tell us about your idea…": "Расскажите о вашей идее…",
        "Submit": "Отправить",
        "Send message": "Отправить",
        "Message": "Сообщение",
        "Phone": "Телефон",
        "Email": "Эл. почта",
        "Subject": "Тема",
        "Our Story": "Наша история",
        "About the Studio": "О студии",
        "Book a consultation with one of our artists and let's design something eternal.": "Запишитесь на консультацию к мастеру и давайте создадим вечное искусство.",
        "Your name…": "Ваше имя…",
        "you@email.com": "you@email.com",
        "Describe your tattoo idea…": "Опишите вашу идею для тату…",
        "Style": "Стиль",
        "Preferred date": "Желаемая дата",
        "Select Artist": "Выберите мастера",
        "Select Style": "Выберите стиль",
        "Find Us": "Где мы",
        "Address": "Адрес",
        "Opening Hours": "Часы работы",
        "Book Now": "Записаться",
        "Portfolio coming soon — check back for fresh ink.": "Портфолио скоро дополнится новыми работами.",
        "by": "мастер",
        "Cancel": "Отмена",
        "Book a Consultation": "Запись на консультацию",
        "All Styles": "Все стили",
        "All": "Все",
        "Studio Works": "Работы студии",
        "No work matches these filters.": "Нет работ по данным фильтрам.",
        "tattoo artist at Skytattoo.art.": "тату мастер на Skytattoo.art.",
        "The story of Skytattoo.art — a gothic tattoo studio and the artists behind the ink.": "История Skytattoo.art — готическая тату студия и мастера за работой.",
        "Get in touch with Skytattoo.art — visit the studio, send a message or book a consultation.": "Свяжитесь с Skytattoo.art — посетите студию, отправьте сообщение или запишитесь на консультацию.",
        "Book your tattoo appointment at Skytattoo.art — choose an artist, a style and a date.": "Запишитесь на тату на Skytattoo.art — выберите мастера, стиль и желаемую дату.",
        "Explore the Skytattoo.art studio portfolio — blackwork, realism, minimal and gothic tattoos, filterable by style, colour and size.": "Исследуйте портфолио Skytattoo.art — готические, реалистичные и блэкворк татуировки с фильтрами.",
        "Meet the tattoo artists of Skytattoo.art — resident masters of blackwork, realism, minimal and gothic ink.": "Познакомьтесь с мастерами Skytattoo.art — резидентами готического стиля, реализма и блэкворка.",
        "Each artist keeps their own space — a personal profile with bio, portfolio and reels.": "У каждого мастера свой профиль с биографией, портфолио и видеороликами.",
        "Tell us who you'd like to work with and what you have in mind. We'll get back to you to confirm.": "Напишите, с кем вы хотите работать и какую идею хотите реализовать. Мы свяжемся с вами для подтверждения.",
        "About": "О нас",
        "Role": "Роль",
        "Back to portfolio": "Назад в портфолио",
        "Book this style": "Запись",
        "Related Work": "Похожие работы",
        "Follow the Ink": "Следите за нами",
        "Social Feed": "Социальные сети",
        "Follow on Instagram": "Подписаться в Instagram",
        "Follow on TikTok": "Подписаться в TikTok",
        "In Motion": "В движении",
        "Video Reels": "Видео",
        "All rights reserved.": "Все права защищены.",
        "The Team": "Команда",
        "Get In Touch": "Связаться",
        "Send a message": "Отправить сообщение",
        "Visit the studio": "Посетить студию",
        "Map — add a Google Maps embed in the admin.": "Карта — добавьте Google Maps embed из панели.",
    }
}

@register.simple_tag(takes_context=True)
def db_trans(context, obj, field_name):
    """Fetches translations dynamically based on active language prefix.
    The database original fields hold English (en).
    """
    if not obj:
        return ""
    if not hasattr(obj, field_name):
        return ""
        
    lang_code = translation.get_language()
    if lang_code:
        lang_code = lang_code.split("-")[0]
    else:
        lang_code = "ka"
        
    # If English (base), return the original field value directly
    if lang_code == "en":
        return getattr(obj, field_name, "")
        
    # Query Translation
    key = f"{obj._meta.model_name}:{obj.pk}:{field_name}"
    try:
        from core.models import Translation
        trans_obj = Translation.objects.get(language__code=lang_code, object_key=key)
        return trans_obj.text
    except Exception:
        # Fallback to base English text
        return getattr(obj, field_name, "")


@register.simple_tag(takes_context=True)
def static_trans(context, text):
    """Translates static UI text keys, auto-registering new ones in the database.
    The English key acts as the base text.
    """
    if not text:
        return ""
        
    lang_code = translation.get_language()
    if lang_code:
        lang_code = lang_code.split("-")[0]
    else:
        lang_code = "ka"

    # Auto-register this static key in the database if it doesn't exist
    from core.models import StaticString
    try:
        string_obj, created = StaticString.objects.get_or_create(key=text)
    except Exception:
        # Fallback if DB is not ready / during migrations
        string_obj = None

    # If English, return original text key
    if lang_code == "en":
        return text

    # Try to load translation from database Translation table
    if string_obj:
        key = f"staticstring:{string_obj.pk}:key"
        try:
            from core.models import Translation
            trans_obj = Translation.objects.get(language__code=lang_code, object_key=key)
            if trans_obj.text.strip():
                return trans_obj.text
        except Exception:
            pass

    # Fallback to local hardcoded dictionary
    lang_dict = STATIC_TEXTS_FALLBACK.get(lang_code, {})
    translated = lang_dict.get(text)
    if translated:
        if string_obj:
            try:
                from core.models import Language, Translation
                lang = Language.objects.filter(code=lang_code).first()
                if lang:
                    key = f"staticstring:{string_obj.pk}:key"
                    Translation.objects.get_or_create(
                        language=lang,
                        object_key=key,
                        defaults={"text": translated},
                    )
            except Exception:
                pass
        return translated
        
    # Fallback to the key text itself (English)
    return text


@register.simple_tag(takes_context=True)
def translate_url(context, lang_code):
    """Translates the current request path into the target language code prefix."""
    request = context.get("request")
    if not request:
        return ""
    from django.urls import translate_url as dj_translate_url
    path = request.get_full_path()
    try:
        return dj_translate_url(path, lang_code)
    except Exception:
        return path
