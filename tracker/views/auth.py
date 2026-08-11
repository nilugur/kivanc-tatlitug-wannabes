from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views import View

from ..forms import ClientProfileForm, DietitianProfileForm


class RegisterClientView(View):
    def get(self, request):
        user_form = UserCreationForm()
        client_form = ClientProfileForm()

        return render(
        request,
        "tracker/register_client.html",
            {"user_form": user_form, "client_form": client_form}
    )

    def post(self, request):
        user_form = UserCreationForm(request.POST)
        client_form = ClientProfileForm(request.POST)
        if user_form.is_valid() and client_form.is_valid():
            new_user = user_form.save()
            new_client_profile = client_form.save(commit=False)
            new_client_profile.user = new_user
            new_client_profile.save()
            # user_form.save() sadece User nesnesini veritabanına kaydeder,
            # tarayıcı oturumuna (session) otomatik giriş yapmaz. login()
            # çağırmazsak "Welcome, admin!" gibi eski oturumun kullanıcısı
            # görünmeye devam eder.
            login(request, new_user)
            # kayıt başarılı olunca kullanıcı indexe yönlendirilir
            return redirect("tracker:index")
        else:
            return render(
            request,
            "tracker/register_client.html",
            {"user_form": user_form, "client_form": client_form}
        )


class RegisterDietitianView(View):
    def get(self, request):
        user_form = UserCreationForm()
        dietitian_form = DietitianProfileForm()

        return render(
        request,
        "tracker/register_dietitian.html",
        {"user_form": user_form, "dietitian_form": dietitian_form}
        )

    def post(self, request):
        user_form = UserCreationForm(request.POST)
        dietitian_form = DietitianProfileForm(request.POST)
        if user_form.is_valid() and dietitian_form.is_valid():
            new_user = user_form.save()
            new_dietitian_profile = dietitian_form.save(commit=False)
            new_dietitian_profile.user = new_user
            new_dietitian_profile.save()
            # user_form.save() sadece User nesnesini veritabanına kaydeder,
            # tarayıcı oturumuna (session) otomatik giriş yapmaz. login()
            # çağırmazsak "Welcome, admin!" gibi eski oturumun kullanıcısı
            # görünmeye devam eder.
            login(request, new_user)
            return redirect("tracker:index")
        else:
            return render(
            request,
            "tracker/register_dietitian.html",
            {"user_form": user_form, "dietitian_form": dietitian_form}
        )


class RegisterChoiceView(View):
    def get(self, request):
        return render(request, "tracker/register_choice.html", {})
