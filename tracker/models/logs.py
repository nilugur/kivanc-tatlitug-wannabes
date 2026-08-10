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
    # Kullanıcı tarihi elle girmesin; kayıt oluşturulduğu an
    # tarih/saat otomatik olarak buraya yazılsın diye
    # auto_now_add=True parametresi kullandık.
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        local_date = timezone.localtime(self.date)
        return f"{self.user.username} - {self.get_meal_type_display()} - {local_date.strftime('%d %b %H:%M')}"


class ExerciseLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.ForeignKey(
        Exercise, on_delete=models.SET_NULL, null=True, blank=True
        )
    duration_minutes = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        local_date = timezone.localtime(self.date)
        return f"{self.user.username} - {self.exercise.exercise_name if self.exercise else 'Deleted Exercise'} - {self.duration_minutes} - {local_date}"


class MealItem(models.Model):
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True, blank=True)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity_g = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.meal} - {self.food.food_name if self.food else 'Deleted Food'} - {self.quantity_g}"