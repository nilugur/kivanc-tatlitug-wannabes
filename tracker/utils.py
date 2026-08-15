from django.utils import timezone
from datetime import datetime, timedelta
from .models.logs import Meal, ExerciseLog, MealItem


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


def get_selected_date(request):
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

    return selected_date


def get_daily_breakdown(user, date):
    all_items = MealItem.objects.filter(meal__user=user, meal__date__date=date)
    breakfast = []
    lunch = []
    dinner = []
    snack = []
    for item in all_items:
        if item.meal.meal_type == "B":
            breakfast.append(item)
        elif item.meal.meal_type == "L":
            lunch.append(item)
        elif item.meal.meal_type == "D":
            dinner.append(item)
        elif item.meal.meal_type == "S":
            snack.append(item)

    exercises = ExerciseLog.objects.filter(user=user, date__date=date)

    return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner, "snack": snack, "exercises": exercises}