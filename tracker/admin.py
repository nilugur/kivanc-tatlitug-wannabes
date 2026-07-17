from django.contrib import admin
from .models import ClientProfile, DietitianProfile
from .models import Food, Meal, Exercise, ExerciseLog, MealItem

admin.site.register(ClientProfile)
admin.site.register(DietitianProfile)
admin.site.register(Food)
admin.site.register(Meal)
admin.site.register(Exercise)
admin.site.register(ExerciseLog)
admin.site.register(MealItem)
