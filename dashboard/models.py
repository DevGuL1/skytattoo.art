from django.db import models


class InstagramSyncConfig(models.Model):
    """Global configuration for Instagram automatic sync and checker."""

    instagram_account_url = models.URLField(
        default="https://www.instagram.com/tattooskystudio/",
        verbose_name="Instagram ანგარიშის ბმული",
        help_text="სტუდიის ოფიციალური Instagram გვერდი (მაგ: https://www.instagram.com/tattooskystudio/)"
    )
    facebook_page_url = models.URLField(
        default="https://www.facebook.com/tattooskystudio",
        verbose_name="Facebook გვერდის ბმული",
        help_text="სტუდიის ოფიციალური Facebook გვერდი (მაგ: https://www.facebook.com/tattooskystudio)"
    )
    instagram_access_token = models.CharField(
        max_length=500, blank=True,
        verbose_name="Instagram / Meta Access Token",
        help_text="Meta / Instagram Graph API Access Token (User or Page Access Token)"
    )
    facebook_access_token = models.CharField(
        max_length=500, blank=True,
        verbose_name="Facebook Page Access Token",
        help_text="Facebook Page Access Token (თუ განსხვავდება Instagram-ის ტოკენისგან)"
    )
    instagram_account_id = models.CharField(
        max_length=100, blank=True,
        verbose_name="Instagram Business Account ID",
        help_text="მაგ: 17841400000000000 (Meta Graph API-სთვის)"
    )
    facebook_page_id = models.CharField(
        max_length=100, blank=True,
        verbose_name="Facebook Page ID",
        help_text="მაგ: 100987654321000 (Facebook Graph API-სთვის)"
    )
    instagram_session_id = models.CharField(
        max_length=200, blank=True,
        verbose_name="Instagram Session ID (Cookie Fallback)",
        help_text="Instagram-ის sessionid კუკი შეზღუდვების გვერდის ავლით წამოსაღებად"
    )
    is_auto_sync_enabled = models.BooleanField(
        default=True,
        verbose_name="ავტომატური შემოწმება ჩართულია",
        help_text="თუ ჩართულია, სკრიპტი ყოველდღიურად ან მითითებულ ინტერვალში შეამოწმებს პოსტებს."
    )
    sync_interval_hours = models.PositiveIntegerField(
        default=24,
        verbose_name="შემოწმების ინტერვალი (საათებში)",
        help_text="მაგ. 24 (ყოველდღე) ან 48 (ყოველ 2 დღეში)"
    )
    last_synced_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="ბოლო შემოწმების თარიღი"
    )
    last_status = models.CharField(
        max_length=50, default="idle",
        verbose_name="ბოლო სტატუსი"
    )
    last_error_message = models.TextField(blank=True, verbose_name="ბოლო შეცდომის შეტყობინება")

    class Meta:
        verbose_name = "Instagram სინქრონიზაციის კონფიგურაცია"
        verbose_name_plural = "Instagram სინქრონიზაციის კონფიგურაცია"

    def __str__(self):
        return f"Instagram Config (ინტერვალი: {self.sync_interval_hours}სთ)"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class InstagramSyncLog(models.Model):
    """Log entry for each Instagram check/sync run."""

    class Status(models.TextChoices):
        SUCCESS = "success", "წარმატებული"
        FAILED = "failed", "შეცდომა"
        WARNING = "warning", "გაფრთხილება"

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="თარიღი")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SUCCESS,
        verbose_name="სტატუსი"
    )
    posts_fetched = models.PositiveIntegerField(default=0, verbose_name="წამოღებული პოსტები")
    items_created = models.PositiveIntegerField(default=0, verbose_name="შექმნილი ნამუშევრები")
    details = models.TextField(blank=True, verbose_name="დეტალები / ლოგი")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Instagram შემოწმების ლოგი"
        verbose_name_plural = "Instagram შემოწმების ლოგები"

    def __str__(self):
        return f"Sync [{self.get_status_display()}] - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

