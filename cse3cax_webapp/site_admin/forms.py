from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from core.models import UserProfile, Role, Subject, LecturerExpertise

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
        choices=[('', 'Select Honorific'), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Prof', 'Prof')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={
            'invalid_choice': 'Please select a valid honorific.',
        }
    )

    class Meta:
        model = UserProfile
        fields = ['role', 'email', 'fte_percentage', 'honorific', 'first_name', 'last_name']
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
            if self.instance.pk:  # This is an existing user
                if email != self.instance.email:
                    if UserProfile.objects.filter(email=email).exists():
                        raise ValidationError("This email is already in use. Please use a different email address.")
            else:  # This is a new user
                if UserProfile.objects.filter(email=email).exists():
                    raise ValidationError("This email is already in use. Please use a different email address.")
        return email

    def clean_fte_percentage(self):
        fte = self.cleaned_data.get('fte_percentage')
        if fte is not None and (fte < 0.1 or fte > 1.0):
            raise ValidationError("FTE percentage must be between 0.1 and 1.0. Please enter a valid value.")
        return fte

class LecturerExpertiseForm(forms.ModelForm):
    expertise = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Expertise"
    )

    class Meta:
        model = LecturerExpertise
        fields = []  # No direct model fields to use in this form; expertise is handled manually

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # Store the user instance
        if user:
            # Pre-populate the form with the user's existing expertise
            self.fields['expertise'].initial = LecturerExpertise.objects.filter(user=user).values_list('subject', flat=True)

    def save(self, commit=True):
        # First, clear the existing expertise for this user
        LecturerExpertise.objects.filter(user=self.user).delete()

        # Now, add the new expertise from the form
        subjects = self.cleaned_data.get('expertise', [])
        for subject in subjects:
            LecturerExpertise.objects.create(user=self.user, subject=subject)

        return self.user  # Return the user for reference (optional)


