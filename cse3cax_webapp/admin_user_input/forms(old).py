from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import UserProfile, Role, Subject, LecturerExpertise
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div

class UserProfileForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        to_field_name="role_id",
        empty_label="Select a role",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_role',  # Ensure this ID is set for our JavaScript
            'data-role': 'role-select'  # Add a data attribute for easier JavaScript selection
        })
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

    expertise = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all().order_by('subject_id'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Select the subjects this lecturer has expertise in."
    )

    class Meta:
        model = UserProfile
        fields = ['role', 'email', 'fte_percentage', 'honorific', 'first_name', 'last_name', 'expertise']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render <form> tag
        show_expertise = self.instance.pk and self.instance.role.role_id == 'Lecturer' if self.instance.pk else False
        self.helper.layout = Layout(
            Fieldset(
                'Personal Information',
                Field('role'),
                Field('email'),
                Field('fte_percentage'),
                Field('honorific'),
                Field('first_name'),
                Field('last_name'),
            ),
            Div(
                Fieldset(
                    'Expertise',
                    Field('expertise'),
                ),
                css_class='expertise-field',
                style='display: block;' if show_expertise else 'display: none;'
            )
        )
        
        if self.instance.pk:
            self.fields['email'].initial = self.instance.email
            self.fields['expertise'].initial = Subject.objects.filter(lecturerexpertise__user=self.instance)

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

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        if commit:
            user_profile.save()
            self.save_expertise(user_profile)
        return user_profile

    def save_expertise(self, user_profile):
        # Clear existing expertise
        LecturerExpertise.objects.filter(user=user_profile).delete()
        # Add new expertise
        for subject in self.cleaned_data['expertise']:
            LecturerExpertise.objects.create(user=user_profile, subject=subject)