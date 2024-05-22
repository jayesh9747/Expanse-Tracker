# forms.py
from django import forms
from django.contrib.auth.models import User
from apis.models import Profile

class UserForm(forms.ModelForm):
    class Meta:
        model: User
        fields: ['username', 'first_name', 'last_name', 'email'] # type: ignore

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'profile_picture', 'location', 'birth_date', 'phone_number']
