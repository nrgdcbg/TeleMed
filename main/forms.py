from pickle import TRUE
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button
from crispy_bootstrap5.bootstrap5 import FloatingField
from django.forms import *
from django.forms.widgets import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import *


class RequestAccountForm(ModelForm):
    class Meta:
        model = AccountRequest
        fields = [
            "email",
            "first_name",
            "last_name",
            "birthdate",
            "sex",
            "contact_number",
            "role",
        ]
        widgets = {
            "first_name": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "fname",
                    "placeholder": "First Name",
                    "required": True,
                }
            ),
            "last_name": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "lname",
                    "placeholder": "Last Name",
                    "required": True,
                }
            ),
            "email": EmailInput(
                attrs={
                    "type": "email",
                    "class": "form-control",
                    "id": "email",
                    "placeholder": "Email Address",
                    "required": True,
                }
            ),
            "birthdate": DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "id": "birthdate",
                    "placeholder": "mm/dd/yyyy",
                    "required": True,
                }
            ),
            "sex": Select(
                attrs={
                    "class": "form-select",
                    "id": "sex",
                    "placeholder": "Sex",
                    "required": True,
                }
            ),
            "contact_number": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "contact_no",
                    "placeholder": "Contact Number",
                    "required": True,
                }
            ),
            "role": Select(
                attrs={
                    "class": "form-select",
                    "id": "role",
                    "placeholder": "Role",
                    "required": True,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),
            Row(
                Column("email", css_class="col-md-6"),
                Column("contact_number", css_class="col-md-6"),
            ),
            Row(
                Column("birthdate", css_class="col-md-4"),
                Column("sex", css_class="col-md-4"),
                Column("role", css_class="col-md-4"),
            ),
            Submit("submit", "Submit"),
        )


# # class CreateUserForm(UserCreationForm):
# #     class Meta:
# #         model = AuthUser
# #         fields = ['first_name','last_name','username', 'email', 'password1', 'password2', 'user_type', 'address', 'birthdate', 'contact_no']

# class EditUserForm(UserChangeForm):
#     class Meta:
#         model = AuthUser
#         fields = ['first_name','last_name','username', 'email', 'password1', 'password2', 'user_type', 'address', 'birthdate', 'contact_no']

class EditPhysicianForm(ModelForm):
    class Meta:
        model = Physician
        fields = ['specialization', 'hospital_affiliation']


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ["file"]


class PrescriptionForm(ModelForm):
    class Meta:
        model = Prescription
        fields = ["file"]


class PatientConsultationRecordForm(ModelForm):
    class Meta:
        model = PatientConsultationRecord
        fields = ["date", "status"]
        widgets = {
            "date": DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "id": "birthdate",
                    "placeholder": "mm/dd/yyyy",
                    "required": True,
                }
            ),
        }
