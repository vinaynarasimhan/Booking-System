from django import forms
from django.contrib.auth import authenticate

from .models import Profile, ResourceSlot, Participant

# Bootstrap class for form inputs
form_input_class = 'form-control'


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'class': form_input_class, 'placeholder': 'LDAP username'})
        )
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(
            attrs={'class': form_input_class, 'placeholder': 'LDAP password'})
        )

    def clean(self):
        super(LoginForm, self).clean()
        try:
            u_name, pwd = self.cleaned_data["username"],\
                          self.cleaned_data["password"]
            user = authenticate(username=u_name, password=pwd)
        except Exception:
            raise forms.ValidationError(
                "Username and/or Password is not entered"
            )
        if not user:
            raise forms.ValidationError("Invalid username/password")
        return user


class ProfileForm(forms.ModelForm):
    """ profile form for students and moderators """

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'organisation',
                  'roll_number', 'position', 'guide', 'department']

    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
                    {'class': form_input_class, 'placeholder': "First Name"}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(
                    {'class': form_input_class, 'placeholder': "Last Name"}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['first_name'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'First Name'}
        )
        self.fields['last_name'].initial = user.last_name
        self.fields['last_name'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Last Name'}
        )
        self.fields['organisation'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Institute'}
        )
        self.fields['department'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': 'Department'}
        )
        self.fields['roll_number'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Roll Number'}
        )
        self.fields['position'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Position'}
        )
        self.fields['guide'].widget.attrs.update(
            {'class': form_input_class,
             'placeholder': 'Guide/Professor/Instructor'}
        )


class SlotForm(forms.ModelForm):

    class Meta:
        model = ResourceSlot
        fields = [
            "resource", "start_date_time", "end_date_time", "description"
        ]

    def __init__(self, *args, **kwargs):
        if 'resource' in kwargs:
            resource = kwargs.pop('resource')
        else:
            resource = None
        super(SlotForm, self).__init__(*args, **kwargs)
        self.fields['resource'].initial = resource
        self.fields['resource'].widget.attrs.update(
            {'class': "custom-select"}
        )
        self.fields['start_date_time'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['end_date_time'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['description'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Description'}
        )


class ParticipantForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': form_input_class})
        )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': form_input_class, "type": "email"})
        )
    class Meta:
        model = ResourceSlot
        fields = ["name", "email"]
