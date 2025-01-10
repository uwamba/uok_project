from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import MonitoringLog
from django.urls import reverse
from django.utils.html import format_html

@admin.register(MonitoringLog)
class MonitoringLogAdmin(admin.ModelAdmin):
    list_display = ('test', 'activity_type', 'timestamp')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'test__name')
    readonly_fields = ('screenshot_preview',)

    def screenshot_preview(self, obj):
        if obj.screenshot:
            return f'<img src="{obj.screenshot.url}" style="max-height: 200px;">'
        return "No screenshot available"
    
    screenshot_preview.allow_tags = True
    screenshot_preview.short_description = "Screenshot"
    def monitor_link(self, obj):
        url = reverse('monitor_candidate', args=[obj.user.id])
        return format_html('<a href="{}" target="_blank">Monitor</a>', url)

    monitor_link.short_description = "Monitor Candidate"

