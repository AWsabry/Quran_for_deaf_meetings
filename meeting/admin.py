from django.contrib import admin
from django.utils.html import format_html


from .models import Meeting


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'title', 'start_at', 'end_at', 'show_url')
    readonly_fields = ('channel_name', 'token', 'uid', 'show_url')

    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def show_url(self, obj):
        link = obj.get_meeting_url(self.request)
        return format_html('<a href="{}">{}</a>', link, 'GO Room')


admin.site.register(Meeting, MeetingAdmin)
