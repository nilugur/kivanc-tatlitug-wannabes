from django import forms
from .models.profiles import ClientProfile, DietitianProfile
from .models.logs import MealItem, ExerciseLog


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            "age", "gender", "weight_kg", "height_cm",
            "goal", "activity_level", "dietitian"
            ]


class DietitianProfileForm(forms.ModelForm):
    class Meta:
        model = DietitianProfile
        fields = ["specialty"]


class MealItemForm(forms.ModelForm):
    class Meta:
        model = MealItem
        fields = ["food", "quantity_g"]


class ExerciseLogForm(forms.ModelForm):
    class Meta:
        model = ExerciseLog
        fields = ["exercise", "duration_minutes"]
        