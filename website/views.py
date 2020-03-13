# Python Imports
import calendar

# Django Imports
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone
from django.forms import inlineformset_factory


# Local Imports
from .forms import LoginForm, ProfileForm, SlotForm, ParticipantForm
from .models import Profile, Resource, ResourceSlot, Participant


def _get_current_year_month():
    now = timezone.now()
    return now.month, now.year


def index(request, is_user=None):
    user = request.user
    if user.is_authenticated:
        template = "user.html"
    else:
        template = "base.html"
    month, year = _get_current_year_month()
    bookings = ResourceSlot.objects.filter(
        end_date_time__month=month, end_date_time__year=year,
        approved=True
    )
    if not user.is_anonymous and is_user:
        bookings = bookings.filter(creator=user)
    bookings = bookings.values("creator__first_name", "creator__last_name",
             "start_date_time", "end_date_time", "resource__name")
    context = {"bookings": bookings, "template": template}
    return render(request, 'index.html', context)


def user_login(request):
    user = request.user
    context = {}
    if user.is_authenticated:
        return show_bookings(request)

    next_url = request.GET.get('next')

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data
            login(request, user)
            return show_bookings(request, next_url)
        else:
            context = {"form": form}
    else:
        form = LoginForm()
        context = {"form": form}
    return render(request, 'login.html', context)


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return render(request, 'logout.html')


@login_required
def show_bookings(request, next_url=None):
    user = request.user
    if not hasattr(user, 'profile'):
        return redirect(reverse('website:profile'))
    context = {}
    resources = Resource.objects.all()
    all_slots = ResourceSlot.objects.filter(creator_id=user.id)
    upcoming_slots = all_slots.filter(end_date_time__gte=timezone.now())
    context["resources"] = resources
    context["all_slots"] = all_slots
    context["upcoming_slots"] = upcoming_slots
    return render(request, 'booking.html', context)


@login_required
def add_or_edit_profile(request):
    user = request.user
    context = {}
    try:
        profile = Profile.objects.get(user_id=user.id)
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = ProfileForm(request.POST, user=user, instance=profile)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user = user
            form_data.user.first_name = request.POST['first_name']
            form_data.user.last_name = request.POST['last_name']
            form_data.user.save()
            form_data.save()
            messages.success(request, "Profile updated successfully")
            context['form'] = form
        else:
            context['form'] = form
    else:
        form = ProfileForm(user=user, instance=profile)
        context['form'] = form
    return render(request, 'profile.html', context)


@login_required
def book_slot(request, resource_id=None):
    user = request.user
    context = {}
    try:
        resource = Resource.objects.get(id=resource_id)
    except Resource.DoesNotExist:
        resource = None
    if request.method == 'POST':
        form = SlotForm(request.POST, resource=resource)
        if form.is_valid():
            data = form.save(commit=False)
            data.creator = user
            data.save()
            messages.success(
                request, "Slot booked successfully, Waiting for approval"
            )
            return redirect(reverse("website:edit_slot", args=[data.id]))
        else:
            context['form'] = form
    else:
        form = SlotForm(resource=resource)
        context['form'] = form
    cur_month, cur_year = _get_current_year_month()
    context["month"] = cur_month
    context["year"] = cur_year
    return render(request, 'book_slot.html', context)


@login_required
def edit_slot(request, slot_id=None):
    user = request.user
    context = {}
    try:
        resource_slot = ResourceSlot.objects.get(id=slot_id)
    except Resource.DoesNotExist:
        resource_slot = None
    ParticipantFormSet = inlineformset_factory(
        ResourceSlot, Participant, ParticipantForm,
        fields='__all__', extra=0
    )
    if request.method == 'POST':
        formset = ParticipantFormSet(request.POST, instance=resource_slot)
        form = SlotForm(request.POST, instance=resource_slot)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user = user
            form_data.save()
            messages.success(request, "Slot updated successfully")
            context['form'] = form
        if formset.is_valid():
            formset.save()
        if 'add' in request.POST:
            ParticipantFormSet = inlineformset_factory(
                ResourceSlot, Participant, ParticipantForm, fields='__all__',
                extra=1
            )
        else:
            context['form'] = form
    else:
        form = SlotForm(instance=resource_slot)
        context['form'] = form
    formset = ParticipantFormSet(instance=resource_slot)
    context["formset"] = formset
    context["slot_id"] = slot_id
    cur_month, cur_year = _get_current_year_month()
    context["month"] = cur_month
    context["year"] = cur_year
    return render(request, 'book_slot.html', context)