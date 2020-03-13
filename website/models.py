# Python Imports
from datetime import timedelta
from textwrap import dedent

# Django Imports
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

# Recurrence Imports
from recurrence.fields import RecurrenceField


departments = (
    ("", "Select Department"),
    ("CS", "Department of Computer Science Engineering"),
    ("EE", "Department of Electrical Engineering"),
    ("ETC", "Department of Electronics and Telecommunications Engineering"),
    ("ME", "Department of Mechanical Engineering"),
    ("AE", "Department of Aerospace Engineering"),
    ("BM", "Department of Biomedical Engineering"),
    ("CH", "Department of Chemical Engineering"),
    ("CE", "Department of Civil Engineering"),
    ("ES", "Department of Earth Sciences"),
    ("EN", "Department of Energy Science & Engineering"),
    ("EV", "Department of Environmental Science & Engineering"),
    ("GNR", "Department of Geoinformatics & Natural Resources Engineering"),
    ("IO", "Department of Industrial Engineering & Operations Research"),
    ("MM", "Department of Metallurgical Engineering & Materials Science"),
    ("MMM", "Department of Materials, Manufacturing and Modeling"),
    ("SC", "Department of Systems & Control Engineering"),
    ("TD", "Department of Technology And Development (CTARA)"),
    ("ET", "Department of Education Technology"),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20)
    organisation = models.CharField(max_length=128)
    department = models.CharField(max_length=64, choices=departments)
    position = models.CharField(max_length=64)
    guide = models.CharField(max_length=180)

    def __str__(self):
        return "Profile of {0}".format(self.user.get_full_name())


class Resource(models.Model):
    name = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=50)
    description = models.TextField()
    no_of_days_between_bookings = models.IntegerField()
    department = models.CharField(
        max_length=64, choices=departments, default=""
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_department(self):
        depts = dict(departments)
        return depts[self.department]

    def __str__(self):
        return self.name


class ResourceSlot(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date_time = models.DateTimeField(default=timezone.now)
    end_date_time = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(hours=1)
    )
    description = models.TextField()
    approved = models.BooleanField(default=False)
    recurrences = RecurrenceField()

    def get_no_of_participants(self):
        return self.participants.count()

    def clean(self):
        time_diff = self.end_date_time - self.start_date_time
        hours = divmod(time_diff.total_seconds(), 3600)[0]
        if self.start_date_time > self.end_date_time:
            raise ValidationError(
                {'start_date_time': 'Start Date cannot be greater than End date'}
            )
        if hours > 24:
            raise ValidationError(
                {'end_date_time': 'End date cannot be more than 24 hours'}
            )
        if (not self._validate_date(self.start_date_time) or
                not self._validate_date(self.start_date_time)):
            msg = 'Only current month booking is allowed'
            raise ValidationError({'start_date_time': msg})
        if not self.id:
            query = dedent("""\
                select id from website_resourceslot where %s between
                start_date_time and end_date_time and resource_id = %s
                """)
            slot = ResourceSlot.objects.raw(
                query, [self.start_date_time, self.resource.id]
            )
            if slot:
                msg = 'Slot is already booked for {0}'.format(self.resource)
                raise ValidationError({'start_date_time': msg})

    def _validate_date(self, date):
        now = timezone.now()
        return date.month == now.month and date.year == now.year

    def toggle_approval_status(self):
        if self.approved:
            self.approved = False
        else:
            self.approved = True
        self.save()

    def set_approval_status(self):
        self.approved = True
        self.save()

    def reset_approval_status(self):
        self.approved = False
        self.save()

    def __str__(self):
        return "Slot for {0}".format(self.resource.name)


class Participant(models.Model):
    slot = models.ForeignKey(
        ResourceSlot, related_name="participants",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return "{0} in slot {1}".format(
            self.name, self.slot
        )
