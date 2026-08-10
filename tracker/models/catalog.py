from django.db import models


class Food(models.Model):
    food_name = models.CharField(max_length=400)
    calorie_per_100g = models.FloatField()

    def __str__(self):
        return f"{self.food_name} - {self.calorie_per_100g} kcal/100g"


class Exercise(models.Model):
    exercise_name = models.CharField(max_length=400)
    calories_per_hour = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.exercise_name} - {self.calories_per_hour} kcal"
