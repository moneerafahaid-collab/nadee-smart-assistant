import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from analytics.models import DataDomain, MaturityFactor, PerformanceAlert, PerformanceRecord
from chatbot.models import KnowledgeArticle

SEED_PATH = Path(settings.BASE_DIR) / "data" / "nadee_seed.json"

PERFORMANCE = [
    (2025, 10, 68, 56, 42, 30, 2.4),
    (2025, 11, 72, 50, 38, 34, 2.7),
    (2025, 12, 78, 44, 31, 40, 3.0),
    (2026, 1, 81, 40, 28, 45, 3.2),
    (2026, 2, 76, 47, 35, 33, 3.0),
    (2026, 3, 84, 36, 22, 48, 3.5),
    (2026, 4, 87, 32, 18, 52, 3.7),
    (2026, 5, 83, 38, 25, 46, 3.6),
    (2026, 6, 89, 30, 16, 55, 3.9),
]

FACTORS = [
    (
        "اكتمال مرفقات مستويات النضج",
        "تجهيز الوثائق الداعمة يسرّع إثبات المستوى في دورة القياس الثالثة.",
        "positive",
        1.4,
    ),
    (
        "تأخر إغلاق ملاحظات جودة البيانات",
        "بقاء ملاحظات الجودة مفتوحة يخفض نضج مجال الجودة والامتثال.",
        "negative",
        1.5,
    ),
    (
        "تفعيل لجنة حوكمة البيانات",
        "وجود لجنة فعّالة يرفع نضج مجال الحوكمة ويحسّن المتابعة.",
        "positive",
        1.3,
    ),
    (
        "ضعف توحيد البيانات المرجعية",
        "اختلاف المراجع بين الأنظمة يسبب تعارضاً ويؤخر التكامل والتحليلات.",
        "negative",
        1.2,
    ),
]


class Command(BaseCommand):
    help = "تهيئة بيانات نضيء الكاملة من دليل دورة القياس الثالثة"

    def handle(self, *args, **options):
        if not SEED_PATH.exists():
            self.stderr.write(f"ملف البيانات غير موجود: {SEED_PATH}")
            return

        payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))

        if not User.objects.filter(username="employee").exists():
            User.objects.create_user(
                username="employee",
                password="Nadee@123",
                first_name="موظف",
                last_name="أمانة المنطقة",
                email="employee@amanah.local",
            )
            self.stdout.write("مستخدم تجريبي: employee / Nadee@123")

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                password="Admin@123",
                email="admin@amanah.local",
            )
            self.stdout.write("مسؤول: admin / Admin@123")

        KnowledgeArticle.objects.all().delete()
        for item in payload["articles"]:
            KnowledgeArticle.objects.create(
                title=item["title"],
                category=item["category"],
                keywords=item.get("keywords", ""),
                content=item["content"],
                source=item.get(
                    "source",
                    "المؤشر الوطني للبيانات (نضيء) — دورة القياس الثالثة / سدايا",
                ),
                is_active=True,
            )

        DataDomain.objects.all().delete()
        for idx, domain in enumerate(payload["domains"], start=1):
            DataDomain.objects.create(
                name=domain["name"],
                pillar=domain.get("pillar", ""),
                criteria_count=domain.get("criteria_count", 0),
                maturity_score=domain.get("maturity_score", 0),
                order=idx,
            )

        PerformanceRecord.objects.all().delete()
        records = [
            PerformanceRecord.objects.create(
                year=row[0],
                month=row[1],
                completion_rate=row[2],
                response_time_hours=row[3],
                open_tickets=row[4],
                closed_tickets=row[5],
                maturity_score=row[6],
                notes="مؤشرات إدارة البيانات وفق مجالات نضيء",
            )
            for row in PERFORMANCE
        ]

        MaturityFactor.objects.all().delete()
        latest = records[-1]
        for name, desc, impact, weight in FACTORS:
            MaturityFactor.objects.create(
                name=name,
                description=desc,
                impact=impact,
                weight=weight,
                related_month=latest,
            )

        PerformanceAlert.objects.all().delete()
        PerformanceAlert.objects.create(
            title="استكمال مرفقات القياس الثالث",
            message="بعض المجالات ما زالت دون المستوى المستهدف قبل دورة القياس.",
            suggestion="راجع مجالات النمذجة وحرية المعلومات أولاً وجهّز الوثائق الداعمة.",
            severity=PerformanceAlert.Severity.WARNING,
        )
        PerformanceAlert.objects.create(
            title="فرصة لتحسين التميز التشغيلي",
            message="نضج الممارسات يتحسن، ويمكن رفع نتائج التميز التشغيلي بمراقبة المؤشرات أسبوعياً.",
            suggestion="اربط لوحات ذكاء الأعمال بمؤشرات إغلاق الطلبات وجودة البيانات.",
            severity=PerformanceAlert.Severity.INFO,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"تم التحميل: {len(payload['articles'])} مادة معرفية، "
                f"{len(payload['domains'])} مجالاً، {len(records)} سجلات أداء."
            )
        )
