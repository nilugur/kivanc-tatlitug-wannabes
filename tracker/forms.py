from django import forms
from .models import ClientProfile, DietitianProfile, Meal, MealItem


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


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ["meal_type"]


class MealItemForm(forms.ModelForm):
    class Meta:
        model = MealItem
        fields = ["food", "quantity_g"]
