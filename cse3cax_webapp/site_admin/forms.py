# 
# Forms for Managing User Profiles and Lecturer Expertise
# ========================================================
# This file defines the forms for managing user profiles (creating or editing users) and lecturer expertise.
# The forms utilize Django's ModelForm and handle validation for fields like email and FTE percentage.
# Custom save methods ensure proper handling of user creation and expertise assignments.
#
# File: forms.py
# Author: Jacob Paff
# Revisions:
#   - 17-09-24: Initial file created by Jacob Paff. Added user profile form with role, FTE, and honorific fields.
#   - 25-09-24: Added LecturerExpertise form for managing multiple subjects a lecturer has expertise in.
#

from django import forms
from django.core.exceptions import ValidationError
from core.models import UserProfile, Role, Subject, LecturerExpertise

# Form for managing User Profiles (create/edit)
class UserProfileForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        to_field_name="role_id",
        empty_label="Select a role",
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={
            'required': 'Please select a role.',
            'invalid_choice': 'Please select a valid role.',
        }
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        }),
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.',
        }
    )

    fte_percentage = forms.FloatField(
        min_value=0.1,
        max_value=1.0,
        initial=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.05',
            'min': '0.1',
            'max': '1'
        }),
        error_messages={
            'required': 'FTE percentage is required.',
            'invalid': 'Please enter a valid number for FTE percentage.',
            'min_value': 'FTE percentage must be at least 0.1.',
            'max_value': 'FTE percentage must not exceed 1.0.',
        }
    )

    honorific = forms.ChoiceField(
        choices=[('', 'Select Honorific'), ('Mr', 'Mr'), ('Mrs', 'Mrs'),
                 ('Ms', 'Ms'), ('Dr', 'Dr'), ('Prof', 'Prof')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={
            'invalid_choice': 'Please select a valid honorific.',
        }
    )

    class Meta:
        model = UserProfile
        fields = ['role', 'email', 'fte_percentage',
                  'honorific', 'first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname'}),
        }
        error_messages = {
            'first_name': {'required': 'First name is required.'},
            'last_name': {'required': 'Last name is required.'},
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Ensure the email is unique for new users or edited users with changed email
            if self.instance.pk:  # Editing existing user
                if email != self.instance.email and UserProfile.objects.filter(email=email).exists():
                    raise ValidationError("This email is already in use. Please use a different email address.")
            else:  # Creating new user
                if UserProfile.objects.filter(email=email).exists():
                    raise ValidationError("This email is already in use. Please use a different email address.")
        return email

    def clean_fte_percentage(self):
        fte = self.cleaned_data.get('fte_percentage')
        if fte is not None and (fte < 0.0 or fte > 1.0):
            raise ValidationError("FTE percentage must be between 0.0 and 1.0. Please enter a valid value.")
        return fte

    def save(self, commit=True):
        user = super(UserProfileForm, self).save(commit=False)
        if not self.instance.pk:  # Creating new user
            user = UserProfile.objects.create_user(
                email=self.cleaned_data['email'],
                role=self.cleaned_data['role'],
                fte_percentage=self.cleaned_data['fte_percentage'],
                honorific=self.cleaned_data['honorific'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
        elif commit:  # Editing existing user
            user.save()
        return user

# Form for managing Lecturer Expertise in multiple subjects
class LecturerExpertiseForm(forms.ModelForm):
    expertise = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Expertise"
    )

    class Meta:
        model = LecturerExpertise
        fields = []  # Expertise handled manually with ModelMultipleChoiceField

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            # Pre-populate expertise with user's current subjects
            self.fields['expertise'].initial = LecturerExpertise.objects.filter(user=user).values_list('subject', flat=True)

    def save(self, commit=True):
        LecturerExpertise.objects.filter(user=self.user).delete()  # Clear existing expertise
        subjects = self.cleaned_data.get('expertise', [])
        for subject in subjects:  # Assign new expertise
            LecturerExpertise.objects.create(user=self.user, subject=subject)
        return self.user
