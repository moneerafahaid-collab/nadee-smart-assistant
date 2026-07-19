import json

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum
from django.shortcuts import render

from .models import DataDomain, MaturityFactor, PerformanceAlert, PerformanceRecord
from .services import build_forecast, evaluate_alerts


@login_required
def dashboard(request):
    records = list(PerformanceRecord.objects.all())
    domains = list(DataDomain.objects.all())
    factors = MaturityFactor.objects.filter(is_active=True)
    forecast = build_forecast(records)
    evaluate_alerts(records)

    latest = records[-1] if records else None
    avg_maturity = (
        DataDomain.objects.aggregate(v=Avg("maturity_score"))["v"]
        or PerformanceRecord.objects.aggregate(v=Avg("maturity_score"))["v"]
        or 0
    )
    total_criteria = DataDomain.objects.aggregate(v=Sum("criteria_count"))["v"] or 0

    chart_json = json.dumps(
        {
            "labels": [f"{r.year}/{r.month:02d}" for r in records],
            "maturity": [r.maturity_score for r in records],
            "completion": [r.completion_rate for r in records],
            "response": [r.response_time_hours for r in records],
        },
        ensure_ascii=False,
    )

    return render(
        request,
        "analytics/dashboard.html",
        {
            "records": records,
            "domains": domains,
            "latest": latest,
            "alerts": PerformanceAlert.objects.filter(is_resolved=False)[:8],
            "factors": factors,
            "forecast": forecast,
            "avg_maturity": round(avg_maturity, 2),
            "total_criteria": total_criteria,
            "chart_json": chart_json,
        },
    )
