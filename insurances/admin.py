from django.contrib import admin

from insurances.models import Insurances


@admin.register(Insurances)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ("id", "medical", "not_leaving")
