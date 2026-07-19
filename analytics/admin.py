from django.contrib import admin

from .models import DataDomain, MaturityFactor, PerformanceAlert, PerformanceRecord


@admin.register(DataDomain)
class DataDomainAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "pillar", "criteria_count", "maturity_score")
    list_editable = ("maturity_score",)
    search_fields = ("name", "pillar")


@admin.register(PerformanceRecord)
class PerformanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "year",
        "month",
        "maturity_score",
        "completion_rate",
        "response_time_hours",
        "open_tickets",
        "closed_tickets",
    )


@admin.register(MaturityFactor)
class MaturityFactorAdmin(admin.ModelAdmin):
    list_display = ("name", "impact", "weight", "is_active")
    list_filter = ("impact", "is_active")


@admin.register(PerformanceAlert)
class PerformanceAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "is_resolved", "created_at")
    list_filter = ("severity", "is_resolved")
