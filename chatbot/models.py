from django.conf import settings
from django.db import models


class KnowledgeArticle(models.Model):
    class Category(models.TextChoices):
        FAQ = "faq", "أسئلة شائعة"
        GUIDE = "guide", "دليل"
        PROCEDURE = "procedure", "إجراء"
        TRAINING = "training", "دورة تدريبية"
        POLICY = "policy", "سياسة"

    title = models.CharField("العنوان", max_length=255)
    content = models.TextField("المحتوى")
    category = models.CharField(
        "التصنيف", max_length=20, choices=Category.choices, default=Category.FAQ
    )
    keywords = models.CharField(
        "كلمات مفتاحية",
        max_length=500,
        blank=True,
        help_text="مفصولة بفواصل، تساعد المساعد الذكي على إيجاد الإجابة",
    )
    source = models.CharField("المصدر", max_length=255, default="سدايا / منصة نضيء")
    is_active = models.BooleanField("نشط", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "معلومة معرفية"
        verbose_name_plural = "قاعدة المعرفة"
        ordering = ["category", "title"]

    def __str__(self):
        return self.title


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        verbose_name="المستخدم",
    )
    title = models.CharField("عنوان المحادثة", max_length=200, default="محادثة جديدة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "جلسة محادثة"
        verbose_name_plural = "جلسات المحادثة"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} — {self.user}"


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "مستخدم"
        ASSISTANT = "assistant", "المساعد"

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages", verbose_name="الجلسة"
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    related_article = models.ForeignKey(
        KnowledgeArticle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mentions",
        verbose_name="المرجع",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "الرسائل"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
