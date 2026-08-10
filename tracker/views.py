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


from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import (
    calculate_calories_consumed,
    calculate_calories_burned,
    calculate_weekly_calories_consumed,
    calculate_weekly_calories_burned,
    get_selected_date,
    get_daily_breakdown,
)


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if ClientProfile.objects.filter(user=request.user).exists():
                profile = ClientProfile.objects.get(user=request.user)
                index_template = "tracker/client_index.html"
                selected_date = get_selected_date(request)
                consumed = calculate_calories_consumed(request.user, selected_date)
                burned = calculate_calories_burned(request.user, selected_date)
                daily_data = get_daily_breakdown(request.user, selected_date)
                weekly_consumed = calculate_weekly_calories_consumed(request.user, selected_date)
                weekly_burned = calculate_weekly_calories_burned(request.user, selected_date)

                context = {"calories_consumed": consumed,
                           "calories_burned": burned,
                           "selected_date": selected_date,
                           "breakfast": daily_data["breakfast"],
                           "lunch": daily_data["lunch"],
                           "dinner": daily_data["dinner"],
                           "snack": daily_data["snack"],
                           "exercises": daily_data["exercises"],
                           "weekly_consumed": weekly_consumed,
                           "weekly_burned": weekly_burned
                           }
            else:
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


class AddMealItemView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        # setup, Django'nun her istekten önce (get/post çağrılmadan önce)
        # otomatik çalıştırdığı özel bir metod. Hem get hem post metodunun
        # ihtiyaç duyduğu ortak hazırlığı burada bir kere yapıyoruz, tekrar
        # tekrar yazmamak için.

        # View'ın kendi orijinal setup mantığını (örn. self.request atamasını)
        # önce çalıştırıyoruz, sonra kendi ek satırlarımızı ekliyoruz.
        super().setup(request, *args, **kwargs)
        # kwargs, URL'den gelen parametreleri (meal_id gibi) sözlük olarak
        # taşıyor. self.meal'e atıyoruz (sade "meal" değil) çünkü bu bilgiye
        # get ve post metodlarından da erişmemiz gerekiyor — setup bittiğinde
        # yerel bir değişken (meal) silinirdi, ama self'e bağlanan bir değer,
        # aynı örneğin (instance) tüm metodlarında kalıcı olarak erişilebilir.

        # setup metodunda, URL'den gelen parametreler (meal_id gibi)
        # doğrudan meal_id diye bir parametre olarak değil
        # kwargs (keyword arguments) adlı bir sözlüğün içinde geliyor.
        # Bu setup'ın genel amaçlı bir metod olması yüzünden
        self.meal = get_object_or_404(Meal, pk=kwargs["meal_id"])
        self.items = self.meal.mealitem_set.all()

    def get(self, request, meal_id):
        meal_item_form = MealItemForm()
        return render(request, "tracker/add_meal_item.html", {"meal_item_form": meal_item_form, "meal": self.meal, "items": self.items})

    def post(self, request, meal_id):
        meal_item_form = MealItemForm(request.POST)
        if meal_item_form.is_valid():
            new_meal_item = meal_item_form.save(commit=False)
            new_meal_item.meal = self.meal
            new_meal_item.save()
            return redirect("tracker:add_meal_item", meal_id=self.meal.id)
        else:
            return render(request, "tracker/add_meal_item.html", {"meal_item_form": meal_item_form, "meal": self.meal, "items": self.items})


class AddExerciseView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.today = timezone.now().date()
        self.today_exercises = ExerciseLog.objects.filter(user=request.user, date__date=self.today)

    def get(self, request):
        exercise_log_form = ExerciseLogForm()

        return render(
        request,
        "tracker/add_exercise.html",
        {"exercise_log_form": exercise_log_form, "today_exercises": self.today_exercises}
        )

    def post(self, request):
        exercise_log_form = ExerciseLogForm(request.POST)
        if exercise_log_form.is_valid():
            new_exercise = exercise_log_form.save(commit=False)
            new_exercise.user = request.user
            new_exercise.save()
            return redirect("tracker:add_exercise")
        else:
            return render(
                    request,
                    "tracker/add_exercise.html",
                    {"exercise_log_form": exercise_log_form, "today_exercises": self.today_exercises}
                    )


class ProfileView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if ClientProfile.objects.filter(user=request.user).exists():
            self.profile = ClientProfile.objects.get(user=request.user)
            self.profile_form = ClientProfileForm
            self.profile_template = "tracker/profile_client.html"
        else:
            self.profile = DietitianProfile.objects.get(user=request.user)
            self.profile_form = DietitianProfileForm
            self.profile_template = "tracker/profile_dietitian.html"

    def get(self, request):
        # instance=profile diyerek Django'ya "yeni bir kayıt oluşturma,
        # kullanıcının zaten var olan profilini güncelle" diyoruz.
        # instance= olmasaydı, her kaydette veritabanına ikinci bir
        # ClientProfile/DietitianProfile satırı daha eklenirdi.
        form = self.profile_form(instance=self.profile)
        return render(request, self.profile_template, {"profile_form": form})

    def post(self, request):
        form = self.profile_form(request.POST, instance=self.profile)
        if form.is_valid():
            form.save()
            return redirect("tracker:profile")
        else:
            return render(request, self.profile_template, {"profile_form": form})


class ClientDetailView(LoginRequiredMixin, View):
    def get(self, request, client_id):
        client = get_object_or_404(ClientProfile, pk=client_id)
        try:
            profile = DietitianProfile.objects.get(user=request.user)

        except DietitianProfile.DoesNotExist:
            raise PermissionDenied

        if profile != client.dietitian:
            raise PermissionDenied

        selected_date = get_selected_date(request)
        consumed = calculate_calories_consumed(client.user, selected_date)
        burned = calculate_calories_burned(client.user, selected_date)
        daily_data = get_daily_breakdown(client.user, selected_date)

        return render(
            request,
            "tracker/client_detail.html",
            {"client": client,
            "calories_consumed": consumed,
            "calories_burned": burned,
            "selected_date": selected_date,
            "breakfast": daily_data["breakfast"],
            "lunch": daily_data["lunch"],
            "dinner": daily_data["dinner"],
            "snack": daily_data["snack"],
            "exercises": daily_data["exercises"]}
            )


class MealLogView(LoginRequiredMixin, View):
    def get(self, request):
        selected_date = timezone.now().date()
        daily_data = get_daily_breakdown(request.user, selected_date)
        foods = Food.objects.all()

        return render(
            request,
            "tracker/meal_log.html",
            {"breakfast_items": daily_data["breakfast"],
            "lunch_items": daily_data["lunch"],
            "dinner_items": daily_data["dinner"],
            "snack_items": daily_data["snack"], "foods": foods}
            )


class MealLogAddView(View):
    @method_decorator(login_required)
    def get(self, request, meal_type):
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


class SearchFoodView(LoginRequiredMixin, View):
    def get(self, request):
        # request.GET, URL'in ?query=... kısmındaki veriyi taşır
        # JavaScript tarafında fetch ile bu URL'e istek atarken kullanıcının arama
        # kutusuna yazdığı kelimeyi buradan okuyoruz .get() kullanıyoruz
        # çünkü query hiç gönderilmemişse hata vermek yerine None döner.
        query = request.GET.get("query")
        if not query:
            return JsonResponse({"results": []})
        # icontains: food_name alanında, aranan kelimeyi İÇEREN (tam eşleşme
        # değil) kayıtları, büyük/küçük harf FARKETMEDEN bulur
        # Önce kendi veritabanımızda arıyoruz, USDA API'sine sadece
        # burada hiç sonuç bulunamazsa gideceğiz (aşağıdaki if not food_list)
        results = Food.objects.filter(food_name__icontains=query)
        food_list = []
        for food in results:
            food_list.append({"id": food.id, "name": food.food_name, "calories": food.calorie_per_100g})

        if not food_list:
            response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", params={"query": query, "api_key": settings.USDA_API_KEY}, timeout=5)
            data = response.json()
            results = data.get("foods", [])
            for food in results:
                for nutrient in food["foodNutrients"]:
                    if nutrient["nutrientName"] == "Energy":
                        calories = nutrient["value"]

                food_list.append({"usda_id": food["fdcId"], "name": food["description"], "calories": calories})

        return JsonResponse({"results": food_list})


class CreateFoodFromUSDAView(LoginRequiredMixin, View):
    def post(self, request):
        name = request.POST.get("name")
        calories = request.POST.get("calories")
        new_food = Food.objects.create(food_name=name, calorie_per_100g=calories)

        return JsonResponse({"id": new_food.id})


class SearchExerciseView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get("query")
        if not query:
            return JsonResponse({"results": []})
        results = Exercise.objects.filter(exercise_name__icontains=query)
        exercise_list = []
        for exercise in results:
            exercise_list.append({"id": exercise.id, "name": exercise.exercise_name, "calories": exercise.calories_per_hour})

        return JsonResponse({"results": exercise_list})


class DeleteMealItemView(LoginRequiredMixin, View):
    def post(self, request, meal_item_id):
        deleted_item = get_object_or_404(MealItem, pk=meal_item_id)
        if deleted_item.meal.user != request.user:
            raise PermissionDenied
        deleted_item.delete()

        return redirect("tracker:meal_log")


class DeleteExerciseView(LoginRequiredMixin, View):
    def post(self, request, exercise_id):
        deleted_item = get_object_or_404(ExerciseLog, pk=exercise_id)
        if deleted_item.user != request.user:
            raise PermissionDenied
        deleted_item.delete()

        return redirect("tracker:add_exercise")

