from django.db import models
from django.conf import settings
from django.utils import timezone

from .catalog import Food, Exercise


class Meal(models.Model):
    MEAL_TYPE_CHOICES = [
        ("B", "Breakfast"),
        ("L", "Lunch"),
        ("D", "Dinner"),
        ("S", "Snack"),
    ]
    meal_type = models.CharField(max_length=1, choices=MEAL_TYPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Eskiden auto_now_add=True kullanıyorduk (kayıt oluşturulduğu anki
    # tarih/saat otomatik yazılsın, kullanıcı elle giremesin diye).
    # Ama ML için ürettiğimiz dummy verilerde (generate_dummy_data
    # komutunda), geçmiş günlere ait sahte Meal/ExerciseLog kayıtları
    # oluşturmamız gerekiyor — auto_now_add=True bu durumda elle
    # verilen tarihi YOK SAYIP her zaman "şu an"ı yazardı. Bu yüzden
    # default=timezone.now'a geçtik: elle tarih verilirse onu kullanır,
    # verilmezse (normal kullanıcı akışında olduğu gibi) yine "şu an"ı
    # otomatik atar.
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        local_date = timezone.localtime(self.date)
        return f"{self.user.username} - {self.get_meal_type_display()} - {local_date.strftime('%d %b %H:%M')}"


class ExerciseLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.ForeignKey(
        Exercise, on_delete=models.SET_NULL, null=True, blank=True
        )
    duration_minutes = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        local_date = timezone.localtime(self.date)
        return f"{self.user.username} - {self.exercise.exercise_name if self.exercise else 'Deleted Exercise'} - {self.duration_minutes} - {local_date}"


class MealItem(models.Model):
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True, blank=True)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity_g = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.meal} - {self.food.food_name if self.food else 'Deleted Food'} - {self.quantity_g}"