from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.db import IntegrityError
from agora_token_builder import RtcTokenBuilder
from django.http import JsonResponse
from multiprocessing import context
import random
import time
import json

from .forms import *
from .models import *
from .decorators import *

from django.views.decorators.csrf import csrf_exempt
from datetime import date
import re


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


# Create your views here.


@unauthenticated_user
def login_user(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        print(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login success")
                if user.role == "SA":
                    return redirect("account_requests")
                elif user.role == "PH":
                    return redirect("all_patients")
                elif user.role == "PA":
                    return redirect("all_doctors")
                else:
                    return redirect("/admin", {"user": user})
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    data = {"login_form": form}
    return render(request, "main/login.html", data)


def request_account(request):
    form = RequestAccountForm()
    if request.method == "POST":
        form = RequestAccountForm(request.POST)
        print(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.age = calculate_age(instance.birthdate)
            instance.save()

            subject = "Telemedicine App - Re: Account Request"
            data = {
                "name": f"{instance.first_name} {instance.last_name}",
                "role": instance.get_role_display(),
            }
            print("Here")
            message = get_template("main/email/request_account_sent_email.html").render(
                data
            )

            msg = EmailMessage(
                subject,
                message,
                "echart.project@gmail.com",
                to=[instance.email],
            )
            msg.content_subtype = "html"
            msg.send()

            return redirect("/request_account_sent/")
        else:
            print(form.errors)
    data = {"request_account_form": form}
    return render(request, "main/request_account.html", data)


def request_account_sent(request):
    return render(request, "main/request_account_sent.html")


# def reset_password(request):
#     return render(request)

@login_required(login_url="login")
def logout_user(request):
    logout(request)
    return redirect("/")

@login_required(login_url="login")
def account_requests(request):
    account_requests = AccountRequest.objects.all()
    data = {"account_requests": account_requests}
    return render(request, "main/account_requests.html", data)

@login_required(login_url="login")
def account_request_approve(request, pk):
    account_request = AccountRequest.objects.get(pk=pk)
    get_pass = re.search(r"\w+(?=@)", account_request.email).group()
    temp_pass = make_password(get_pass)
    # Temporary try-catch to handle a duplicate account request being accepted
    try:
        account = Account.objects.create(
            email=account_request.email,
            first_name=account_request.first_name,
            last_name=account_request.last_name,
            birthdate=account_request.birthdate,
            age=account_request.age,
            sex=account_request.sex,
            contact_number=account_request.contact_number,
            role=account_request.role,
            password=temp_pass,
        )
        account_request.delete()

        subject = "Telemedicine App - Re: Account Request"
        data = {
            "name": f"{account.first_name} {account.last_name}",
            "role": account.get_role_display(),
            "password": get_pass,
        }
        message = get_template("main/email/approve_email.html").render(data)
        msg = EmailMessage(
            subject,
            message,
            "echart.project@gmail.com",
            to=[account.email],
        )

        msg.content_subtype = "html"
        msg.send()

        if(account.role == "PA"):
            Patient.objects.create(account=account)

    except IntegrityError as e:
        return HttpResponse(
            "Accepting this creates a duplicate. Please deny this account request instead"
        )

    return redirect("/account_requests/")

@login_required(login_url="login")
def account_request_deny(request, pk):
    account_request = AccountRequest.objects.get(pk=pk)
    subject = "Telemedicine App - Re: Account Request"
    data = {
        "name": f"{account_request.first_name} {account_request.last_name}",
        "role": account_request.get_role_display(),
    }
    message = get_template("main/email/deny_email.html").render(data)
    msg = EmailMessage(
        subject,
        message,
        "echart.project@gmail.com",
        to=[account_request.email],
    )
    msg.content_subtype = "html"
    msg.send()
    account_request.delete()
    # Send email here
    return redirect("/account_requests/")

@login_required(login_url="login")
def change_is_active(request, pk):
    account = Account.objects.get(pk=pk)
    account.is_active = not account.is_active
    account.save()
    return redirect("/accounts/")

@login_required(login_url="login")
def accounts(request):
    accounts_list = Account.objects.all()
    data = {"accounts_list": accounts_list}
    return render(request, "main/accounts.html", data)

@login_required(login_url="login")
def all_doctors_page(request):
    doctors = Physician.objects.all()

    context = {"doctors": doctors}
    return render(request, "main/all_doctors.html", context)

@login_required(login_url="login")
def all_patients_page(request):
    doctor = request.user.physician
    pcr = PatientConsultationRecord.objects.filter(physician=doctor)
    pp = []
    if pcr.exists():
        for p in pcr:
            if p.patient not in pp:
                pp.append(p.patient)


    patients = Patient.objects.all()
    

    context = {"pcr": pp, "patients": patients}
    return render(request, "main/all_patients.html", context)

@login_required(login_url="login")
def patient_page(request, id):
    patient = Patient.objects.get(id=id)
    profile = request.user
    prescription_form = PrescriptionForm()
    pcr_form = PatientConsultationRecordForm()

    if request.method == "POST":
        if 'pform' in request.POST:
            prescription_form = PrescriptionForm(request.POST, request.FILES)

            if prescription_form.is_valid():
                prescription = prescription_form.save(False)
                prescription.patient = patient
                prescription.physician = profile.physician
                prescription.save()
                return redirect("patient_page", patient.id)

        elif 'pcr' in request.POST:
            pcr_form = PatientConsultationRecordForm(request.POST)

            if pcr_form.is_valid():
                pcr = pcr_form.save(False)
                pcr.patient = patient
                pcr.physician = profile.physician
                pcr.save()
                return redirect("patient_page", patient.id)

    context = {
        "patient": patient,
        "profile": profile,
        "pform": prescription_form,
        "pcr": pcr_form,
    }
    return render(request, "main/patient.html", context)

@login_required(login_url="login")
def profile_page(request):
    profile = request.user
    document_form = DocumentForm()
    doctor_form = EditPhysicianForm()
    if profile.role == "PH":
        doctor_form = EditPhysicianForm(instance=profile.physician)
        if request.method == "POST":
           doctor_form = EditPhysicianForm(request.POST, instance=profile.physician)
           if doctor_form.is_valid():
               doctor_form.save()
               return redirect("profile_page")
    elif profile.role == "PA":
        document_form = DocumentForm()
        if request.method == "POST":
           document_form = DocumentForm(request.POST, request.FILES)
           if document_form.is_valid():              
               document = document_form.save(False)
               document.patient = profile.patient
               document.save()
               return redirect("profile_page")

    #if request.method == "POST":
    #    #after being assigned onetoonefield is interchangeable
    #    if profile.role == "PH":
    #        doctor_form = EditPhysicianForm(request.POST, instance=profile.physician)
    #        if doctor_form.is_valid():
    #            doctor_form.save()
    #            return redirect("profile_page")

    #    if profile.role == "PA":       
    #        document_form = DocumentForm(request.POST, request.FILES)
    #        if document_form.is_valid():              
    #            document = document_form.save(False)
    #            document.patient = profile.patient
    #            document.save()
    #            return redirect("profile_page")

    context = {"profile": profile, "dform": document_form, "pform": doctor_form}
    return render(request, "main/profile.html", context)

@login_required(login_url="login")
def lobby(request):
    return render(request, "main/lobby.html")

@login_required(login_url="login")
def room(request):
    return render(request, "main/room.html")

@login_required(login_url="login")
def getToken(request):
    appId = "ab463b2c13cc40279dd71e7181ba55af"
    appCertificate = "74b688a4e2ab4d5895b987e4eabadcef"
    channelName = request.GET.get("channel")
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600 * 24
    currentTimeStamp = time.time()
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(
        appId, appCertificate, channelName, uid, role, privilegeExpiredTs
    )
    return JsonResponse({"token": token, "uid": uid}, safe=False)

@login_required(login_url="login")
@csrf_exempt
def createMember(request):
    data = json.loads(request.body)

    member, created = RoomMember.objects.get_or_create(
        name=data["name"], uid=data["UID"], room_name=data["room_name"]
    )

    return JsonResponse({"name": data["name"]}, safe=False)

@login_required(login_url="login")
def getMember(request):
    uid = request.GET.get("UID")
    room_name = request.GET.get("room_name")

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )

    name = member.name
    return JsonResponse({"name": member.name}, safe=False)

@login_required(login_url="login")
@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)

    member = RoomMember.objects.get(
        name=data["name"], uid=data["UID"], room_name=data["room_name"]
    )

    member.delete()

    return JsonResponse("Member was deleted", safe=False)


"""
def account_requests(request):
    req_list = Account.objects.filter(is_active = False)
    context = {'user':request.user, 'list':req_list}
    return render(request, "main/account_requests.html", context)
"""
