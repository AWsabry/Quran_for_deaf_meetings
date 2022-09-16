from django.contrib import admin, messages
from django.utils.translation import ngettext


from .models import Meeting, MeetingMember


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'title', 'channel_name', 'start_at', 'end_at', 'show_url')
    readonly_fields = ('show_url', 'token', 'channel_name', 'uid')
    # exclude = ('channel_name', 'token', 'uid')
    actions = ('mark_as_finished', 'mark_as_cancelled')

    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def show_url(self, obj):
        if obj.pk:
            return obj.get_meeting_link(self.request)
        return "--"

    def mark_as_finished(self, request, queryset):
        updated = queryset.update(status='finished')
        self.message_user(request, ngettext(
            '%d meeting was successfully marked as finished.',
            '%d meetings were successfully marked as finished.',
            updated,
        ) % updated, messages.SUCCESS)
    mark_as_finished.short_description = 'Mark Meeting As Finished'

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, ngettext(
            '%d meeting was successfully marked as cancelled.',
            '%d meetings were successfully marked as cancelled.',
            updated,
        ) % updated, messages.SUCCESS)
    mark_as_cancelled.short_description = 'Mark Meeting As Cancelled'


admin.site.register(MeetingMember)
admin.site.register(Meeting, MeetingAdmin)
