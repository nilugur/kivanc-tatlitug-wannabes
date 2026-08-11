from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import requests
from django.conf import settings
from django.core.paginator import Paginator

from ..models.catalog import Food, Exercise


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

        response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", params={"query": query, "api_key": settings.USDA_API_KEY}, timeout=5)
        data = response.json()
        results = data.get("foods", [])
        for food in results:
            for nutrient in food["foodNutrients"]:
                if nutrient["nutrientName"] == "Energy":
                    calories = nutrient["value"]

            food_list.append({"usda_id": food["fdcId"], "name": food["description"], "calories": calories})

        page = int(request.GET.get("page", 1))
        paginator = Paginator(food_list, 10)
        page_obj = paginator.page(page)

        return JsonResponse({"results": list(page_obj), "total_pages": paginator.num_pages})


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
