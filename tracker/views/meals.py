from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from ..models.logs import Meal, MealItem
from ..models.catalog import Food
from ..forms import MealItemForm
from ..utils import get_daily_breakdown


class AddMealItemView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        # setup, Django'nun her istekten önce (get/post çağrılmadan önce)
        # otomatik çalıştırdığı özel bir metod. Hem get hem post metodunun
        # ihtiyaç duyduğu ortak hazırlığı burada bir kere yapıyoruz, tekrar
        # tekrar yazmamak için.

        # View'ın kendi orijinal setup mantığını (örn. self.request atamasını)
        # önce çalıştırıyoruz, sonra kendi ek satırlarımızı ekliyoruz.
        super().setup(request, *args, **kwargs)
        # kwargs, URL'den gelen parametreleri (meal_id gibi) sözlük olarak
        # taşıyor. self.meal'e atıyoruz (sade "meal" değil) çünkü bu bilgiye
        # get ve post metodlarından da erişmemiz gerekiyor — setup bittiğinde
        # yerel bir değişken (meal) silinirdi, ama self'e bağlanan bir değer,
        # aynı örneğin (instance) tüm metodlarında kalıcı olarak erişilebilir.

        # setup metodunda, URL'den gelen parametreler (meal_id gibi)
        # doğrudan meal_id diye bir parametre olarak değil
        # kwargs (keyword arguments) adlı bir sözlüğün içinde geliyor.
        # Bu setup'ın genel amaçlı bir metod olması yüzünden
        self.meal = get_object_or_404(Meal, pk=kwargs["meal_id"])
        self.items = self.meal.mealitem_set.all()

    def get(self, request, meal_id):
        meal_item_form = MealItemForm()
        return render(request, "tracker/add_meal_item.html", {"meal_item_form": meal_item_form, "meal": self.meal, "items": self.items})

    def post(self, request, meal_id):
        meal_item_form = MealItemForm(request.POST)
        if meal_item_form.is_valid():
            new_meal_item = meal_item_form.save(commit=False)
            new_meal_item.meal = self.meal
            new_meal_item.save()
            return redirect("tracker:add_meal_item", meal_id=self.meal.id)
        else:
            return render(request, "tracker/add_meal_item.html", {"meal_item_form": meal_item_form, "meal": self.meal, "items": self.items})


class MealLogView(LoginRequiredMixin, View):
    def get(self, request):
        selected_date = timezone.now().date()
        daily_data = get_daily_breakdown(request.user, selected_date)
        foods = Food.objects.all()

        return render(
            request,
            "tracker/meal_log.html",
            {"breakfast_items": daily_data["breakfast"],
            "lunch_items": daily_data["lunch"],
            "dinner_items": daily_data["dinner"],
            "snack_items": daily_data["snack"], "foods": foods}
            )


class MealLogAddView(View):
    @method_decorator(login_required)
    def get(self, request, meal_type):
        selected_date = timezone.now().date()
        # get_or_create: bugün, bu kullanıcı için, bu meal_type'ta zaten bir
        # Meal var mı diye bakar. Varsa onu getirir yoksa yeni bir tane
        # oluşturur. Bunu kullanmasaydık kullanıcı aynı öğüne (örn. Lunch)
        # birden fazla kez "+ Add" dediğinde her seferinde yeni, tekrarlayan
        # bir Meal kaydı oluşurdu.
        # İki değişkene atama yapıyoruz çünkü get_or_create her zaman iki
        # değer döndürür: bulunan/oluşturulan nesnenin kendisi (meal) ve
        # bu nesnenin yeni mi oluşturulduğunu yoksa zaten var mı olduğunu
        # söyleyen bir True/False değeri (created). Biz created'i şu an
        # kullanmıyoruz ama Python'a iki değişkenle karşılamamız gerekiyor.
        meal, created = Meal.objects.get_or_create(user=request.user, meal_type=meal_type, date=selected_date)
        return redirect("tracker:add_meal_item", meal_id=meal.id)


class DeleteMealItemView(LoginRequiredMixin, View):
    def post(self, request, meal_item_id):
        deleted_item = get_object_or_404(MealItem, pk=meal_item_id)
        if deleted_item.meal.user != request.user:
            raise PermissionDenied
        deleted_item.delete()

        return redirect("tracker:meal_log")


class EditMealItemView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.edited_item = get_object_or_404(MealItem, pk=kwargs["meal_item_id"])
        if self.edited_item.meal.user != request.user:
            raise PermissionDenied

    def get(self, request, meal_item_id):
        meal_item_form = MealItemForm(instance=self.edited_item)
        return render(request, "tracker/edit_meal_item.html", {"meal_item_form": meal_item_form, "meal_item": self.edited_item})

    def post(self, request, meal_item_id):
        meal_item_form = MealItemForm(request.POST, instance=self.edited_item)
        if meal_item_form.is_valid():
            meal_item_form.save()
            return redirect("tracker:meal_log")
        else:
            return render(request, "tracker/edit_meal_item.html", {"meal_item_form": meal_item_form, "meal_item": self.edited_item})