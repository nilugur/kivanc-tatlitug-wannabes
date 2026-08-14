from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import random
from ...models.profiles import ClientProfile
from ...models.catalog import Food, Exercise
from ...models.logs import Meal
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Bu komut tekrar tekrar çalıştırılabilir olmalı
        # ama User.username alanı unique olduğu için komut
        # ikinci kez çalıştırıldığında "dummy_user_0" gibi isimler zaten var
        # olacağından User.objects.create_user(...) hata verirdi bu yüzden
        # her çalıştırmada önce eski dummy kullanıcıları (ve CASCADE sayesinde
        # onlara bağlı ClientProfile/Meal/MealItem/ExerciseLog kayıtlarını)
        # silip sıfırdan üretiyoruz
        User.objects.filter(username__startswith="dummy_user_").delete()
        low_calorie_foods = Food.objects.filter(calorie_per_100g__lte=100)
        medium_calorie_foods = Food.objects.filter(calorie_per_100g__gt=100, calorie_per_100g__lte=400)
        high_calorie_foods = Food.objects.filter(calorie_per_100g__gt=400)
        exercise_pool = Exercise.objects.all()
        for i in range(60):
            username = f"dummy_user_{i}"
            new_user = User.objects.create_user(username=username, password="dummy_password")
            new_client_profile = ClientProfile(user=new_user)
            new_client_profile.gender = random.choice(["M", "F"])
            new_client_profile.goal = random.choice(["L", "G", "MT"])
            new_client_profile.age = random.randint(18, 65)
            new_client_profile.height_cm = random.uniform(140, 200)
            new_client_profile.weight_kg = random.uniform(40, 150)
            new_client_profile.activity_level = random.choice(
                                                [("Sedentary"),
                                                ("Lightly"),
                                                ("Moderately"),
                                                ("High"),
                                                ("Extra")]
                                                )
            if new_client_profile.goal == "L":
                food_pool = low_calorie_foods
            elif new_client_profile.goal == "G":
                food_pool = high_calorie_foods
            else:
                food_pool = medium_calorie_foods

            new_client_profile.save()

            for day_offset in range(7):
                meal_date = timezone.now() - timedelta(days=day_offset)
                meal_types_today = random.sample(["B", "L", "D", "S"], random.randint(1, 4))
                for meal_type in meal_types_today:
                    new_meal = Meal(user=new_user, meal_type=meal_type, date=meal_date)
                    new_meal.save()
                    num_items = random.randint(1, 3)
                    for _ in range(num_items):
                        food_item = random.choice(food_pool)
                        quantity_g = random.randint(10, 300)
                        new_meal.mealitem_set.create(food=food_item, quantity_g=quantity_g)

            if new_client_profile.activity_level == "Sedentary":
                min_duration = 10
                max_duration = 20
                num_exercise_days = random.randint(0, 1)
            elif new_client_profile.activity_level == "Lightly":
                min_duration = 15
                max_duration = 30
                num_exercise_days = random.randint(1, 3)
            elif new_client_profile.activity_level == "Moderately":
                min_duration = 30
                max_duration = 45
                num_exercise_days = random.randint(3, 5)
            elif new_client_profile.activity_level == "High":
                min_duration = 45
                max_duration = 75
                num_exercise_days = random.randint(6, 7)
            else:  # Extra active
                min_duration = 75
                max_duration = 120
                num_exercise_days = random.randint(6, 7)

            exercise_days = random.sample(range(7), num_exercise_days)

            for day_offset in exercise_days:
                exercise_date = timezone.now() - timedelta(days=day_offset)
                exercise_duration = random.randint(min_duration, max_duration)
                new_user.exerciselog_set.create(duration_minutes=exercise_duration, date=exercise_date, exercise=random.choice(exercise_pool))

    


