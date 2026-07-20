from django.shortcuts import render
from django.shortcuts import redirect 
# redirect(), HttpResponseRedirect + reverse()'ün yaptığı işi
# tek bir fonksiyonda birleştiren bir kısayol.
from django.contrib.auth.forms import UserCreationForm
from .forms import ClientProfileForm, DietitianProfileForm, MealForm, MealItemForm, ExerciseLogForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Meal, ClientProfile, DietitianProfile, ExerciseLog
from django.utils import timezone
from datetime import datetime


def calculate_calories_consumed(user, date):
    total = 0
    meals = Meal.objects.filter(user=user, date__date=date)
    for meal in meals:
        for meal_item in meal.mealitem_set.all():
            if meal_item.food:
                total += (meal_item.quantity_g / 100) * meal_item.food.calorie_per_100g

    return total


def calculate_calories_burned(user, date):
    total = 0
    exercise_logs = ExerciseLog.objects.filter(user=user, date__date=date)
    for log in exercise_logs:
        if log.exercise:
            total += (log.duration_minutes / 60) * log.exercise.calories_per_hour

    return total


def index(request):
    if request.user.is_authenticated:
        try:
            profile = ClientProfile.objects.get(user=request.user)
            index_template = "tracker/client_index.html"
            # request.GET, URL'in sonundaki ?date=... gibi parametreleri
            # tutan bir sözlük. .get("date") ile "date" anahtarını arıyoruz;
            # .get() kullanıyoruz çünkü kullanıcı hiç tarih seçmediyse
            # (URL'de ?date=... yoksa) hata vermek yerine None döndürür.
            date_param = request.GET.get("date")
            if date_param:
                # request.GET'ten gelen değer her zaman bir string'dir
                # (örn. "2026-07-16"), bir tarih nesnesi değil.
                # strptime bu string'i "%Y-%m-%d" kalıbına göre
                # (yıl-ay-gün) okuyup bir datetime nesnesine çeviriyor.
                # Sonundaki .date() ise saat kısmını atıp sadece tarihi alıyor
                # çünkü filter(date__date=...) sadece tarih (saatsiz) bekliyor.
                selected_date = datetime.strptime(date_param, "%Y-%m-%d").date()
            else:
                # Kullanıcı hiç tarih seçmediyse, varsayılan olarak bugünü göster
                selected_date = timezone.now().date()

            consumed = calculate_calories_consumed(request.user, selected_date)
            burned = calculate_calories_burned(request.user, selected_date)
            context = {"calories_consumed": consumed,
                       "calories_burned": burned,
                       "selected_date": selected_date
                       }
        except ClientProfile.DoesNotExist:
            profile = DietitianProfile.objects.get(user=request.user)
            clients = ClientProfile.objects.filter(dietitian=profile)
            index_template = "tracker/dietitian_index.html"
            context = {"clients": clients}

        return render(request, index_template, context)
    else:
        return render(request, "tracker/index.html", {})


def register_client(request):
    if request.method == "POST":
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
        user_form = UserCreationForm()
        client_form = ClientProfileForm()

    return render(
        request,
        "tracker/register_client.html",
        {"user_form": user_form, "client_form": client_form}
        )


def register_dietitian(request):
    if request.method == "POST":
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
        user_form = UserCreationForm()
        dietitian_form = DietitianProfileForm()

    return render(
        request,
        "tracker/register_dietitian.html",
        {"user_form": user_form, "dietitian_form": dietitian_form}
    )


def register_choice(request):
    return render(request, "tracker/register_choice.html", {})


@login_required
def add_meal(request):
    if request.method == "POST":
        meal_form = MealForm(request.POST)
        if meal_form.is_valid():
            new_meal = meal_form.save(commit=False)
            new_meal.user = request.user
            new_meal.save()
            return redirect("tracker:add_meal_item", meal_id=new_meal.id)

    else:
        meal_form = MealForm()

    return render(request, "tracker/add_meal.html", {"meal_form": meal_form})


@login_required
def add_meal_item(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    if request.method == "POST":
        meal_item_form = MealItemForm(request.POST)
        if meal_item_form.is_valid():
            new_meal_item = meal_item_form.save(commit=False)
            new_meal_item.meal = meal
            new_meal_item.save()
            return redirect("tracker:add_meal_item", meal_id=meal.id)

    else:
        meal_item_form = MealItemForm()

    return render(
        request,
        "tracker/add_meal_item.html", 
        {"meal_item_form": meal_item_form, "meal": meal}
        )


@login_required
def add_exercise(request):
    if request.method == "POST":
        exercise_log_form = ExerciseLogForm(request.POST)
        if exercise_log_form.is_valid():
            new_exercise = exercise_log_form.save(commit=False)
            new_exercise.user = request.user
            new_exercise.save()
            return redirect("tracker:add_exercise")

    else:
        exercise_log_form = ExerciseLogForm()

    return render(
        request,
        "tracker/add_exercise.html",
        {"exercise_log_form": exercise_log_form}
        )


@login_required
def profile(request):
    try:
        profile = ClientProfile.objects.get(user=request.user)
        profile_form = ClientProfileForm
        profile_template = "tracker/profile_client.html"

    except ClientProfile.DoesNotExist:
        profile = DietitianProfile.objects.get(user=request.user)
        profile_form = DietitianProfileForm
        profile_template = "tracker/profile_dietitian.html"

    if request.method == "POST":
        # instance=profile diyerek Django'ya "yeni bir kayıt oluşturma,
        # kullanıcının zaten var olan profilini güncelle" diyoruz.
        # instance= olmasaydı, her kaydette veritabanına ikinci bir
        # ClientProfile/DietitianProfile satırı daha eklenirdi.
        form = profile_form(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("tracker:profile")

    else:
        # Formu boş değil, kullanıcının mevcut bilgileriyle
        # (instance=profile) doldurarak gösteriyoruz.
        form = profile_form(instance=profile)

    return render(request, profile_template, {"profile_form": form})


@login_required
def client_detail(request, client_id):
    client = get_object_or_404(ClientProfile, pk=client_id)
    date_param = request.GET.get("date")
    if date_param:
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    consumed = calculate_calories_consumed(client.user, selected_date)
    burned = calculate_calories_burned(client.user, selected_date)

    return render(
        request, 
        "tracker/client_detail.html",
        {"client": client,
         "calories_consumed": consumed,
         "calories_burned": burned,
         "selected_date": selected_date}
        )
