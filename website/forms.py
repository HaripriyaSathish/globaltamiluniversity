"""
Website forms with strict validation.

The same rules are enforced in the browser (static/js/main.js) for instant
feedback, and here on the server so they can never be bypassed.
"""
import re

from django import forms
from django.utils import timezone

from .models import Application, ContactMessage, CourseOpening, ContactSubject

NAME_RE = re.compile(r"^[^\W\d_]+(?:(?:\. |[ .'\-])[^\W\d_]+)*\.?$")  # letters with single space . ' - (e.g. R. D'Souza)
MOBILE_RE = re.compile(r'^[6-9]\d{9}$')                                 # 10-digit Indian mobile
QUALIFICATION_RE = re.compile(r"^[A-Za-z0-9 .,()+\-/&']+$")


def clean_name_value(value, label="name"):
    value = re.sub(r'\s+', ' ', (value or '')).strip()
    if not value:
        raise forms.ValidationError(f"Please enter your {label}.")
    if not NAME_RE.match(value):
        raise forms.ValidationError("Name can contain letters only (no numbers or symbols).")
    if not 2 <= len(value) <= 60:
        raise forms.ValidationError("Name must be between 2 and 60 characters.")
    return value


def clean_mobile_value(value, required=True):
    raw = (value or '').strip()
    if not raw:
        if required:
            raise forms.ValidationError("Please enter your mobile number.")
        return ''
    if not re.fullmatch(r'[\d ]+', raw):
        raise forms.ValidationError("Mobile number can contain digits only.")
    digits = raw.replace(' ', '')
    if not MOBILE_RE.match(digits):
        raise forms.ValidationError("Enter a valid 10-digit mobile number starting with 6, 7, 8 or 9.")
    return digits


class HoneypotMixin(forms.Form):
    """Hidden field that real visitors never fill; bots usually do."""
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Spam detected.")
        return ''


class ApplicationForm(HoneypotMixin, forms.ModelForm):
    program = forms.ModelChoiceField(queryset=CourseOpening.objects.none(),
                                     error_messages={'required': "Please select a program.",
                                                     'invalid_choice': "Please select a valid program."})
    year_of_passing = forms.CharField(max_length=4,
                                      error_messages={'required': "Please enter your year of passing."})
    consent = forms.BooleanField(error_messages={'required': "Please agree to be contacted by the admissions team."})

    class Meta:
        model = Application
        fields = ['full_name', 'email', 'phone', 'program', 'qualification', 'year_of_passing', 'goals', 'consent']
        widgets = {'goals': forms.Textarea(attrs={'rows': 4})}
        error_messages = {
            'full_name': {'required': "Please enter your full name."},
            'email': {'required': "Please enter your email address.", 'invalid': "Please enter a valid email address."},
            'phone': {'required': "Please enter your mobile number."},
            'qualification': {'required': "Please enter your highest qualification."},
        }

    def __init__(self, *args, section=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only courses that are visible and not closed can be chosen
        self.fields['program'].queryset = (CourseOpening.objects.filter(is_active=True)
                                           .exclude(status=CourseOpening.CLOSED))
        self.fields['goals'].max_length = 1000

        # Browser-side hints (main.js uses data-rule for live validation)
        attrs = {
            'full_name': {'data-rule': 'name', 'autocomplete': 'name', 'maxlength': 60},
            'email': {'data-rule': 'email', 'autocomplete': 'email', 'maxlength': 254},
            'phone': {'data-rule': 'mobile', 'autocomplete': 'tel-national', 'inputmode': 'numeric', 'maxlength': 10},
            'program': {'data-rule': 'required', 'data-msg': 'Please select a program.'},
            'qualification': {'data-rule': 'qualification', 'maxlength': 100},
            'year_of_passing': {'data-rule': 'year', 'inputmode': 'numeric', 'maxlength': 4},
            'goals': {'data-rule': 'goals', 'maxlength': 1000},
            'consent': {'data-rule': 'checked'},
        }
        for name, a in attrs.items():
            self.fields[name].widget.attrs.update(a)

        if section:  # labels/placeholders come from admin
            for name, label, placeholder in [
                ('full_name', section.name_label, section.name_placeholder),
                ('email', section.email_label, section.email_placeholder),
                ('phone', section.phone_label, section.phone_placeholder),
                ('program', section.program_label, section.program_placeholder),
                ('qualification', section.qualification_label, section.qualification_placeholder),
                ('year_of_passing', section.year_label, section.year_placeholder),
                ('goals', section.goals_label, section.goals_placeholder),
            ]:
                self.fields[name].label = label
                self.fields[name].widget.attrs['placeholder'] = placeholder
            self.fields['program'].empty_label = section.program_placeholder or '---------'
            self.fields['consent'].label = section.consent_text

    def clean_full_name(self):
        return clean_name_value(self.cleaned_data.get('full_name'), "full name")

    def clean_phone(self):
        return clean_mobile_value(self.cleaned_data.get('phone'))

    def clean_qualification(self):
        value = re.sub(r'\s+', ' ', self.cleaned_data.get('qualification') or '').strip()
        if not QUALIFICATION_RE.match(value) or not re.search(r'[A-Za-z]', value):
            raise forms.ValidationError("Use letters and numbers only, e.g. Higher Secondary or B.Sc.")
        if not 2 <= len(value) <= 100:
            raise forms.ValidationError("Qualification must be between 2 and 100 characters.")
        return value

    def clean_year_of_passing(self):
        value = (self.cleaned_data.get('year_of_passing') or '').strip()
        max_year = timezone.localdate().year + 1
        if not re.fullmatch(r'\d{4}', value):
            raise forms.ValidationError("Year must be 4 digits, e.g. 2026.")
        year = int(value)
        if not 1950 <= year <= max_year:
            raise forms.ValidationError(f"Enter a year between 1950 and {max_year}.")
        return year

    def clean_goals(self):
        value = (self.cleaned_data.get('goals') or '').strip()
        if len(value) > 1000:
            raise forms.ValidationError("Please keep this under 1000 characters.")
        return value


class ContactForm(HoneypotMixin, forms.ModelForm):
    subject = forms.ModelChoiceField(queryset=ContactSubject.objects.none(),
                                     error_messages={'required': "Please select a subject.",
                                                     'invalid_choice': "Please select a valid subject."})

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4})}
        error_messages = {
            'name': {'required': "Please enter your name."},
            'email': {'required': "Please enter your email address.", 'invalid': "Please enter a valid email address."},
            'message': {'required': "Please enter your message."},
        }

    def __init__(self, *args, section=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = ContactSubject.objects.filter(is_active=True)
        attrs = {
            'name': {'data-rule': 'name', 'autocomplete': 'name', 'maxlength': 60},
            'email': {'data-rule': 'email', 'autocomplete': 'email', 'maxlength': 254},
            'phone': {'data-rule': 'mobile-optional', 'autocomplete': 'tel-national', 'inputmode': 'numeric', 'maxlength': 10},
            'subject': {'data-rule': 'required', 'data-msg': 'Please select a subject.'},
            'message': {'data-rule': 'message', 'maxlength': 1000},
        }
        for name, a in attrs.items():
            self.fields[name].widget.attrs.update(a)
        if section:
            for name, placeholder in [
                ('name', section.name_placeholder),
                ('email', section.email_placeholder),
                ('phone', section.phone_placeholder),
                ('message', section.message_placeholder),
            ]:
                self.fields[name].widget.attrs['placeholder'] = placeholder
            self.fields['subject'].empty_label = section.subject_placeholder or '---------'

    def clean_name(self):
        return clean_name_value(self.cleaned_data.get('name'))

    def clean_phone(self):
        return clean_mobile_value(self.cleaned_data.get('phone'), required=False)

    def clean_message(self):
        value = (self.cleaned_data.get('message') or '').strip()
        if len(value) < 10:
            raise forms.ValidationError("Please write at least 10 characters.")
        if len(value) > 1000:
            raise forms.ValidationError("Please keep your message under 1000 characters.")
        return value
