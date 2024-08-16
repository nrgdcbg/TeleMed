from distutils.command.upload import upload
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

# Create your models here.

phone_regex = RegexValidator(
    r"^(09|\+639)\d{9}$",
    message="Phone number must begin with +639 or 09 followed by a 9 digits",
)


class AccountRequest(models.Model):
    email = models.EmailField(verbose_name="email", max_length=225)
    first_name = models.CharField(
        verbose_name="first name", max_length=225, null=True, blank=True
    )
    last_name = models.CharField(
        verbose_name="last name", max_length=225, null=True, blank=True
    )
    birthdate = models.DateField(auto_now_add=False, null=True, blank=True)
    age = models.PositiveSmallIntegerField(
        null=True,
        blank=False,
        validators=[MaxValueValidator(200), MinValueValidator(0)],
    )
    sex = models.CharField(
        max_length=1, choices=[("M", "Male"), ("F", "Female")], null=True, blank=True
    )
    contact_number = models.CharField(
        max_length=13, validators=[phone_regex], null=True, blank=True
    )
    role = models.CharField(
        verbose_name="role",
        max_length=2,
        choices=[
            ("PH", "Physician"),
            ("PA", "Patient"),
        ],
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Account Manger and Account model used to modify base User Model
# it is used to change login from username to email
class AccountManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError("Users must have an email address.")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=self.normalize_email(email), password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=225, unique=True)
    first_name = models.CharField(
        verbose_name="first name", max_length=225, null=True, blank=True
    )
    last_name = models.CharField(
        verbose_name="last name", max_length=225, null=True, blank=True
    )
    birthdate = models.DateField(auto_now_add=False, null=True, blank=True)
    age = models.PositiveSmallIntegerField(
        null=True,
        blank=False,
        validators=[MaxValueValidator(200), MinValueValidator(0)],
    )
    sex = models.CharField(
        max_length=1, choices=[("M", "Male"), ("F", "Female")], null=True, blank=True
    )
    contact_number = models.CharField(
        max_length=13, validators=[phone_regex], null=True, blank=True
    )
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    role = models.CharField(
        verbose_name="role",
        max_length=2,
        choices=[
            ("SA", "System Admin"),
            ("PH", "Physician"),
            ("PA", "Patient"),
        ],
    )
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Patient(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.account.first_name


class Physician(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)
    hospital_affiliation = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.account.first_name


class PatientConsultationRecord(models.Model):
    STATUS = {
        ("UP", "Upcoming"),
        ("DN", "Done"),
    }

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="PCR", null=True
    )
    physician = models.ForeignKey(Physician, on_delete=models.CASCADE, null=True)
    date = models.DateField(auto_now_add=False, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=200,blank=True, null=True)


class Prescription(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="prescription", null=True
    )
    physician = models.ForeignKey(
        Physician, on_delete=models.CASCADE, related_name="prescription", null=True
    )
    file = models.FileField(upload_to="prescriptions/")


class Consultation(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="consultation", null=True
    )
    physician = models.ForeignKey(
        Physician, on_delete=models.CASCADE, related_name="consultation", null=True
    )


class Document(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="documents", null=True
    )
    file = models.FileField(upload_to="documents/")

class RoomMember(models.Model):
    name = models.CharField(max_length=200)
    uid = models.CharField(max_length=200)
    room_name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
