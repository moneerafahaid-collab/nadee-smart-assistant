from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from analytics.models import DataDomain, PerformanceRecord
from chatbot.models import KnowledgeArticle


@login_required
def home(request):
    article_count = KnowledgeArticle.objects.filter(is_active=True).count()
    domain_count = DataDomain.objects.count()
    latest = PerformanceRecord.objects.order_by("-year", "-month").first()
    return render(
        request,
        "core/home.html",
        {
            "article_count": article_count,
            "domain_count": domain_count,
            "latest": latest,
        },
    )


@login_required
def about(request):
    return render(request, "core/about.html")
