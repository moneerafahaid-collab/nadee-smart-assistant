"""خدمات تحليل أداء إدارة البيانات ونسبة النضج."""

from __future__ import annotations

from .models import PerformanceAlert, PerformanceRecord


def build_forecast(records: list[PerformanceRecord]) -> dict:
    if len(records) < 2:
        return {
            "next_maturity": None,
            "trend": "غير كافٍ",
            "message": "يلزم سجلّان شهريان على الأقل لتوقع الأداء القادم.",
        }

    recent = records[-3:]
    deltas = [
        recent[i].maturity_score - recent[i - 1].maturity_score
        for i in range(1, len(recent))
    ]
    avg_delta = sum(deltas) / len(deltas)
    next_maturity = max(0.0, min(5.0, recent[-1].maturity_score + avg_delta))

    if avg_delta > 0.05:
        trend = "تصاعدي"
        message = "الأداء يتجه للتحسن. استمر في معالجة العوامل السلبية المفتوحة."
    elif avg_delta < -0.05:
        trend = "تنازلي"
        message = "يوجد تراجع متوقع. راجع التنبيهات والعوامل المؤثرة فوراً."
    else:
        trend = "مستقر"
        message = "مستوى النضج مستقر. ركّز على رفع نسبة الإنجاز وتقليل زمن الاستجابة."

    return {
        "next_maturity": round(next_maturity, 2),
        "trend": trend,
        "message": message,
        "avg_delta": round(avg_delta, 2),
    }


def evaluate_alerts(records: list[PerformanceRecord]) -> None:
    """ينشئ تنبيهات عملية عند انخفاض المؤشرات."""
    if not records:
        return

    latest = records[-1]
    existing_titles = set(
        PerformanceAlert.objects.filter(is_resolved=False).values_list("title", flat=True)
    )

    candidates = []

    if latest.maturity_score < 3.0:
        candidates.append(
            (
                "انخفاض مستوى نضج إدارة البيانات",
                f"درجة النضج الحالية {latest.maturity_score} وهي دون المستوى المستهدف (3.0).",
                "فعّل خطة تحسين تتضمن تدريب الفريق ومراجعة جودة البيانات أسبوعياً.",
                PerformanceAlert.Severity.CRITICAL,
            )
        )

    if latest.completion_rate < 75:
        candidates.append(
            (
                "نسبة إنجاز منخفضة",
                f"نسبة الإنجاز لهذا الشهر {latest.completion_rate}%.",
                "أعد ترتيب أولويات الطلبات المفتوحة ووزّع المهام حسب الأولوية.",
                PerformanceAlert.Severity.WARNING,
            )
        )

    if latest.response_time_hours > 48:
        candidates.append(
            (
                "تأخير في زمن الاستجابة",
                f"متوسط زمن الاستجابة {latest.response_time_hours} ساعة.",
                "فعّل مسار تصعيد سريع للطلبات الحرجة وراجع الاختناقات التشغيلية.",
                PerformanceAlert.Severity.WARNING,
            )
        )

    if latest.open_tickets > latest.closed_tickets:
        candidates.append(
            (
                "تراكم الطلبات المفتوحة",
                f"المفتوح {latest.open_tickets} مقابل المغلق {latest.closed_tickets}.",
                "خصّص ساعات إغلاق يومية وحدّث حالة كل طلب قبل نهاية الأسبوع.",
                PerformanceAlert.Severity.INFO,
            )
        )

    for title, message, suggestion, severity in candidates:
        if title not in existing_titles:
            PerformanceAlert.objects.create(
                title=title,
                message=message,
                suggestion=suggestion,
                severity=severity,
            )
