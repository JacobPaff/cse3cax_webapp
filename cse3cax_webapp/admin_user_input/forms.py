from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import UserProfile, Role
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

class UserProfileForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        to_field_name="role_id",
        empty_label="Select a role",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    email = forms.EmailField(
        validators=[EmailValidator(message="Enter a valid email address.")],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
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
        })
    )

    honorific = forms.ChoiceField(
        choices=[('', 'Select Honorific'), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Prof', 'Prof')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = UserProfile
        fields = ['role', 'email', 'fte_percentage', 'honorific', 'first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render <form> tag
        self.helper.layout = Layout(
            Field('role'),
            Field('email'),
            Field('fte_percentage'),
            Field('honorific'),
            Field('first_name'),
            Field('last_name'),
        )
        
        if self.instance.pk:
            self.fields['email'].initial = self.instance.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_fte_percentage(self):
        fte = self.cleaned_data.get('fte_percentage')
        if fte is not None and (fte < 0.1 or fte > 1.0):
            raise ValidationError("FTE must be between 0.1 and 1.0")
        return fte