from django.contrib import admin, messages

from website.models import Profile, Resource, ResourceSlot, Participant


class ResourceSlotAdmin(admin.ModelAdmin):
    actions = ['approve_request', 'disapprove_request']
    list_display = ["resource", "creator", "start_date_time", "end_date_time",
        "approved"
    ]
    readonly_fields = ["resource", "creator"]

    def approve_request(self, request, slots):
        for slot in slots:
            slot.set_approval_status()
        messages.add_message(
            request, messages.SUCCESS, 'Successfully approved slots'
        )

    def disapprove_request(self, request, slots):
        for slot in slots:
            slot.reset_approval_status()
        messages.add_message(
            request, messages.SUCCESS, 'Successfully disapproved slots'
        )


admin.site.register(Profile)
admin.site.register(Resource)
admin.site.register(ResourceSlot, ResourceSlotAdmin)
admin.site.register(Participant)