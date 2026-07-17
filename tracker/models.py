from django.db import models
from django.conf import settings
from django.utils import timezone


class DietitianProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user.username} - {self.specialty}"


class ClientProfile(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ]
    GOAL_CHOICES = [
        ("L", "Lose Weight"),
        ("G", "Gain Weight"),
        ("MT", "Maintain Weight"),
        ]
    ACTIVITY_CHOICES = [
        ("Sedentary", "Sedentary (little or no exercise)"),
        ("Lightly", "Lightly active (light exercise/sports 1-3 days/week)"),
        ("Moderately", "Moderately active (moderate exercise/sports 3-5 days/week)"),
        ("High", "Very active (hard exercise/sports 6-7 days a week)"),
        ("Extra", "Extra active (very hard exercise/sports)"),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    goal = models.CharField(max_length=2, choices=GOAL_CHOICES)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    height_cm = models.FloatField()
    weight_kg = models.FloatField()
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    # diyetisyen silinirse sadece bağlantı kopsun,
    # danışan verisi kalsın diye CASCADE yerine SET_NULL
    dietitian = models.ForeignKey(
        DietitianProfile, on_delete=models.SET_NULL, null=True, blank=True
        )

    def __str__(self):
        # get_gender_display() kullanıyoruz çünkü self.gender ham kodu ("M")
        # döndürür, get_gender_display() ise GENDER_CHOICES'daki okunabilir
        # karşılığını ("Male") verir.
        return f"{self.user.username} - {self.get_gender_display()}"


class Food(models.Model):
    food_name = models.CharField(max_length=400)
    calorie_per_100g = models.FloatField()

    def __str__(self):
        return f"{self.food_name} - {self.calorie_per_100g} kcal/100g"


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
        return f"{self.user.username} - {self.get_meal_type_display()} - {local_date}"


class Exercise(models.Model):
    exercise_name = models.CharField(max_length=400)
    calories_per_hour = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.exercise_name} - {self.calories_per_hour} kcal"


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
