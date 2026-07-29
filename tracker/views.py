from django.shortcuts import render
from django.shortcuts import redirect
# redirect(), HttpResponseRedirect + reverse()'ün yaptığı işi
# tek bir fonksiyonda birleştiren bir kısayol.
from django.contrib.auth.forms import UserCreationForm
from .forms import ClientProfileForm, DietitianProfileForm, MealItemForm, ExerciseLogForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Meal, ClientProfile, DietitianProfile, ExerciseLog, MealItem, Food, Exercise
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
import requests
from django.conf import settings


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


def calculate_weekly_calories_consumed(user, date):
    week_ago = date - timedelta(days=7)
    weekly_data = MealItem.objects.filter(meal__user=user, meal__date__date__gte=week_ago,  meal__date__date__lte=date)
    total = 0
    for items in weekly_data:
        if items.food:
            total += (items.quantity_g / 100) * items.food.calorie_per_100g

    return total


def calculate_weekly_calories_burned(user, date):
    week_ago = date - timedelta(days=7)
    weekly_data = ExerciseLog.objects.filter(user=user, date__date__gte=week_ago, date__date__lte=date)
    total = 0
    for items in weekly_data:
        if items.exercise:
            total += (items.duration_minutes / 60) * items.exercise.calories_per_hour

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
            breakfast = MealItem.objects.filter(meal__user=request.user, meal__meal_type="B", meal__date__date=selected_date)
            lunch = MealItem.objects.filter(meal__user=request.user, meal__meal_type="L", meal__date__date=selected_date)
            dinner = MealItem.objects.filter(meal__user=request.user, meal__meal_type="D", meal__date__date=selected_date)
            snack = MealItem.objects.filter(meal__user=request.user, meal__meal_type="S", meal__date__date=selected_date)
            exercises = ExerciseLog.objects.filter(user=request.user, date__date=selected_date)
            weekly_consumed = calculate_weekly_calories_consumed(request.user, selected_date)
            weekly_burned = calculate_weekly_calories_burned(request.user, selected_date)

            context = {"calories_consumed": consumed,
                       "calories_burned": burned,
                       "selected_date": selected_date,
                       "breakfast": breakfast,
                       "lunch": lunch,
                       "dinner": dinner,
                       "snack": snack,
                       "exercises": exercises,
                       "weekly_consumed": weekly_consumed,
                       "weekly_burned": weekly_burned
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
def add_meal_item(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    items = meal.mealitem_set.all()
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
        {"meal_item_form": meal_item_form, "meal": meal, "items": items}
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

    today = timezone.now().date()
    today_exercises = ExerciseLog.objects.filter(user=request.user, date__date=today)

    return render(
        request,
        "tracker/add_exercise.html",
        {"exercise_log_form": exercise_log_form, "today_exercises": today_exercises}
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
    try:
        profile = DietitianProfile.objects.get(user=request.user)

    except DietitianProfile.DoesNotExist:
        raise PermissionDenied

    if profile != client.dietitian:
        raise PermissionDenied

    date_param = request.GET.get("date")
    if date_param:
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    consumed = calculate_calories_consumed(client.user, selected_date)
    burned = calculate_calories_burned(client.user, selected_date)
    breakfast = MealItem.objects.filter(meal__user=client.user, meal__meal_type="B", meal__date__date=selected_date)
    lunch = MealItem.objects.filter(meal__user=client.user, meal__meal_type="L", meal__date__date=selected_date)
    dinner = MealItem.objects.filter(meal__user=client.user, meal__meal_type="D", meal__date__date=selected_date)
    snack = MealItem.objects.filter(meal__user=client.user, meal__meal_type="S", meal__date__date=selected_date)
    exercises = ExerciseLog.objects.filter(user=client.user, date__date=selected_date)

    return render(
        request,
        "tracker/client_detail.html",
        {"client": client,
         "calories_consumed": consumed,
         "calories_burned": burned,
         "selected_date": selected_date,
         "breakfast": breakfast,
         "lunch": lunch,
         "dinner": dinner,
         "snack": snack,
         "exercises": exercises}
        )


@login_required
def meal_log(request):
    selected_date = timezone.now().date()
    breakfast_items = MealItem.objects.filter(meal__user=request.user, meal__meal_type="B", meal__date__date=selected_date)
    lunch_items = MealItem.objects.filter(meal__user=request.user, meal__meal_type="L", meal__date__date=selected_date)
    dinner_items = MealItem.objects.filter(meal__user=request.user, meal__meal_type="D", meal__date__date=selected_date)
    snack_items = MealItem.objects.filter(meal__user=request.user, meal__meal_type="S", meal__date__date=selected_date)
    foods = Food.objects.all()
    return render(
        request,
        "tracker/meal_log.html",
        {"breakfast_items": breakfast_items, "lunch_items": lunch_items, "dinner_items": dinner_items, "snack_items": snack_items, "foods": foods}
        )


@login_required
def meal_log_add(request, meal_type):
    selected_date = timezone.now().date()
    # get_or_create: bugün, bu kullanıcı için, bu meal_type'ta zaten bir
    # Meal var mı diye bakar. Varsa onu getirir yoksa yeni bir tane
    # oluşturur. Bunu kullanmasaydık kullanıcı aynı öğüne (örn. Lunch)
    # birden fazla kez "+ Add" dediğinde her seferinde yeni, tekrarlayan
    # bir Meal kaydı oluşurdu.
    # İki değişkene atama yapıyoruz çünkü get_or_create her zaman iki
    # değer döndürür: bulunan/oluşturulan nesnenin kendisi (meal) ve
    # bu nesnenin yeni mi oluşturulduğunu yoksa zaten var mı olduğunu
    # söyleyen bir True/False değeri (created). Biz created'i şu an
    # kullanmıyoruz ama Python'a iki değişkenle karşılamamız gerekiyor.
    meal, created = Meal.objects.get_or_create(user=request.user, meal_type=meal_type, date=selected_date)
    return redirect("tracker:add_meal_item", meal_id=meal.id)


@login_required
def search_food(request):
    # request.GET, URL'in ?query=... kısmındaki veriyi taşır
    # JavaScript tarafında fetch ile bu URL'e istek atarken kullanıcının arama
    # kutusuna yazdığı kelimeyi buradan okuyoruz .get() kullanıyoruz
    # çünkü query hiç gönderilmemişse hata vermek yerine None döner.
    query = request.GET.get("query")
    # icontains: food_name alanında, aranan kelimeyi İÇEREN (tam eşleşme
    # değil) kayıtları, büyük/küçük harf FARKETMEDEN bulur
    # Önce kendi veritabanımızda arıyoruz, USDA API'sine sadece
    # burada hiç sonuç bulunamazsa gideceğiz (aşağıdaki if not food_list)
    results = Food.objects.filter(food_name__icontains=query)
    food_list = []
    for food in results:
        food_list.append({"id": food.id, "name": food.food_name, "calories": food.calorie_per_100g})

    if not food_list:
        response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", params={"query": query, "api_key": settings.USDA_API_KEY})
        data = response.json()
        results = data["foods"]
        for food in results:
            for nutrient in food["foodNutrients"]:
                if nutrient["nutrientName"] == "Energy":
                    calories = nutrient["value"]

            food_list.append({"usda_id": food["fdcId"], "name": food["description"], "calories": calories})

    return JsonResponse({"results": food_list})


@login_required
def create_food_from_usda(request):
    name = request.POST.get("name")
    calories = request.POST.get("calories")
    new_food = Food.objects.create(food_name=name, calorie_per_100g=calories)

    return JsonResponse({"id": new_food.id})


@login_required
def search_exercise(request):
    query = request.GET.get("query")
    results = Exercise.objects.filter(exercise_name__icontains=query)
    exercise_list = []
    for exercise in results:
        exercise_list.append({"id": exercise.id, "name": exercise.exercise_name, "calories": exercise.calories_per_hour})

    return JsonResponse({"results": exercise_list})


@login_required
def delete_meal_item(request, meal_item_id):
    deleted_item = get_object_or_404(MealItem, pk=meal_item_id)
    if deleted_item.meal.user != request.user:
        raise PermissionDenied
    deleted_item.delete()

    return redirect("tracker:meal_log")


@login_required
def delete_exercise(request, exercise_id):
    deleted_item = get_object_or_404(ExerciseLog, pk=exercise_id)
    if deleted_item.user != request.user:
        raise PermissionDenied
    deleted_item.delete()

    return redirect("tracker:add_exercise")

