from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div
from .models import SubjectInstance, UserProfile, Subject
from core.models import LecturerExpertise

class SubjectInstanceForm(forms.ModelForm):
    assigned_lecturers = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.none(),
        label="Assigned Lecturers",
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    class Meta:
        model = SubjectInstance
        fields = ['subject', 'month', 'year', 'assigned_lecturers', 'start_date', 'enrollments']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Subject Instance Details',
                'subject',
                'month',
                'year',
                'start_date',
                'enrollments',
                'assigned_lecturers'
            ),
            Div(
                Submit('submit', 'Save', css_class='btn btn-primary'),
                css_class='text-right'
            )
        )

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        self.fields['assigned_lecturers'].widget.attrs.update({'class': 'form-control select2'})
        
        if self.instance.pk and self.instance.subject:
            self.fields['assigned_lecturers'].queryset = UserProfile.objects.filter(
                lecturerexpertise__subject=self.instance.subject
            ).distinct()
            self.initial['assigned_lecturers'] = self.instance.users.all()
        else:
            self.fields['assigned_lecturers'].queryset = UserProfile.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        assigned_lecturers = cleaned_data.get('assigned_lecturers')

        if subject and assigned_lecturers:
            valid_lecturers = UserProfile.objects.filter(
                lecturerexpertise__subject=subject
            )
            for lecturer in assigned_lecturers:
                if lecturer not in valid_lecturers:
                    self.add_error('assigned_lecturers', f"{lecturer} does not have expertise in the selected subject.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            instance.users.set(self.cleaned_data['assigned_lecturers'])
        return instance