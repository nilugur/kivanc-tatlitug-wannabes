from django.db import models
from django.conf import settings


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
