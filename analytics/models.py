from django.db import models


class DataDomain(models.Model):
    """مجال من مجالات مؤشر نضيء (14 مجالاً)."""

    name = models.CharField("المجال", max_length=200, unique=True)
    pillar = models.CharField("الركيزة", max_length=100, blank=True)
    criteria_count = models.PositiveIntegerField("عدد المعايير", default=0)
    maturity_score = models.FloatField("درجة النضج الحالية", default=0, help_text="من 0 إلى 5")
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "مجال نضيء"
        verbose_name_plural = "مجالات نضيء"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def maturity_label(self):
        score = self.maturity_score
        if score < 1:
            return "غير مطبّق"
        if score < 2:
            return "مبتدئ"
        if score < 3:
            return "نامٍ"
        if score < 4:
            return "متوسط"
        if score < 5:
            return "متقدم"
        return "متميز"


class PerformanceRecord(models.Model):
    """تقييم أداء إدارة البيانات شهرياً."""

    year = models.PositiveIntegerField("السنة")
    month = models.PositiveIntegerField("الشهر")
    completion_rate = models.FloatField("نسبة الإنجاز %", help_text="من 0 إلى 100")
    response_time_hours = models.FloatField("متوسط زمن الاستجابة (ساعة)")
    open_tickets = models.PositiveIntegerField("الطلبات المفتوحة", default=0)
    closed_tickets = models.PositiveIntegerField("الطلبات المغلقة", default=0)
    maturity_score = models.FloatField("درجة النضج", help_text="من 0 إلى 5 (6 مستويات)")
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "سجل أداء"
        verbose_name_plural = "سجلات الأداء"
        unique_together = ("year", "month")
        ordering = ["year", "month"]

    def __str__(self):
        return f"{self.year}/{self.month:02d} — نضج {self.maturity_score}"

    @property
    def maturity_label(self):
        score = self.maturity_score
        if score < 1.5:
            return "مبتدئ"
        if score < 2.5:
            return "نامٍ"
        if score < 3.5:
            return "متوسط"
        if score < 4.5:
            return "متقدم"
        return "متميز"


class MaturityFactor(models.Model):
    """عامل يؤثر على مستوى النضج أو يسبب تأخيراً."""

    class Impact(models.TextChoices):
        POSITIVE = "positive", "إيجابي"
        NEGATIVE = "negative", "سلبي"

    name = models.CharField("العامل", max_length=200)
    description = models.TextField("الوصف")
    impact = models.CharField(max_length=20, choices=Impact.choices)
    weight = models.FloatField("الوزن", default=1.0, help_text="أهمية العامل نسبياً")
    related_month = models.ForeignKey(
        PerformanceRecord,
        on_delete=models.CASCADE,
        related_name="factors",
        null=True,
        blank=True,
        verbose_name="الشهر المرتبط",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "عامل نضج"
        verbose_name_plural = "عوامل النضج"

    def __str__(self):
        return self.name


class PerformanceAlert(models.Model):
    class Severity(models.TextChoices):
        INFO = "info", "معلومة"
        WARNING = "warning", "تنبيه"
        CRITICAL = "critical", "حرج"

    title = models.CharField("العنوان", max_length=255)
    message = models.TextField("الرسالة")
    suggestion = models.TextField("اقتراح عملي")
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.WARNING
    )
    is_resolved = models.BooleanField("تمت المعالجة", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تنبيه أداء"
        verbose_name_plural = "تنبيهات الأداء"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
