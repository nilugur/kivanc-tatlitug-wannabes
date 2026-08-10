from django.contrib import admin
from .models.profiles import ClientProfile, DietitianProfile
from .models.catalog import Food, Exercise
from .models.logs import Meal, MealItem, ExerciseLog

admin.site.register(ClientProfile)
admin.site.register(DietitianProfile)
admin.site.register(Food)
admin.site.register(Meal)
admin.site.register(Exercise)
admin.site.register(ExerciseLog)
admin.site.register(MealItem)
