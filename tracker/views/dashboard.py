from django.views import View
from django.shortcuts import render
from ..models.profiles import ClientProfile, DietitianProfile
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


from ..utils import (
    calculate_calories_consumed,
    calculate_calories_burned,
    calculate_weekly_calories_consumed,
    calculate_weekly_calories_burned,
    get_selected_date,
    get_daily_breakdown,
)


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if ClientProfile.objects.filter(user=request.user).exists():
                profile = ClientProfile.objects.get(user=request.user)
                index_template = "tracker/client_index.html"
                selected_date = get_selected_date(request)
                consumed = calculate_calories_consumed(request.user, selected_date)
                burned = calculate_calories_burned(request.user, selected_date)
                daily_data = get_daily_breakdown(request.user, selected_date)
                weekly_consumed = calculate_weekly_calories_consumed(request.user, selected_date)
                weekly_burned = calculate_weekly_calories_burned(request.user, selected_date)

                context = {"calories_consumed": consumed,
                           "calories_burned": burned,
                           "selected_date": selected_date,
                           "breakfast": daily_data["breakfast"],
                           "lunch": daily_data["lunch"],
                           "dinner": daily_data["dinner"],
                           "snack": daily_data["snack"],
                           "exercises": daily_data["exercises"],
                           "weekly_consumed": weekly_consumed,
                           "weekly_burned": weekly_burned
                           }
            else:
                profile = DietitianProfile.objects.get(user=request.user)
                clients = ClientProfile.objects.filter(dietitian=profile)
                index_template = "tracker/dietitian_index.html"
                context = {"clients": clients}

            return render(request, index_template, context)
        else:
            return render(request, "tracker/index.html", {})


class ClientDetailView(LoginRequiredMixin, View):
    def get(self, request, client_id):
        client = get_object_or_404(ClientProfile, pk=client_id)
        try:
            profile = DietitianProfile.objects.get(user=request.user)

        except DietitianProfile.DoesNotExist:
            raise PermissionDenied

        if profile != client.dietitian:
            raise PermissionDenied

        selected_date = get_selected_date(request)
        consumed = calculate_calories_consumed(client.user, selected_date)
        burned = calculate_calories_burned(client.user, selected_date)
        daily_data = get_daily_breakdown(client.user, selected_date)

        return render(
            request,
            "tracker/client_detail.html",
            {"client": client,
            "calories_consumed": consumed,
            "calories_burned": burned,
            "selected_date": selected_date,
            "breakfast": daily_data["breakfast"],
            "lunch": daily_data["lunch"],
            "dinner": daily_data["dinner"],
            "snack": daily_data["snack"],
            "exercises": daily_data["exercises"]}
            )
