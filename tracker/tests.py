from django.test import TestCase
from django.contrib.auth.models import User
from .models.profiles import ClientProfile, DietitianProfile
from .models.catalog import Food, Exercise
from .models.logs import Meal, MealItem, ExerciseLog
from .utils import (
    calculate_calories_consumed,
    calculate_calories_burned,
    calculate_weekly_calories_consumed,
    calculate_weekly_calories_burned,
    get_daily_breakdown,
    get_selected_date,
    )
from datetime import date
from django.utils import timezone
from datetime import timedelta
from django.test import RequestFactory

# ________________________
# YETKİLENDİRME TESTLERİ
# _________________________

class ClientDetailViewTests(TestCase):
    def setUp(self):
        # Test veritabanına 2 dietitian ve 1 client ekliyoruz

        # 1. dietitian ve onun kullanıcı hesabı
        # Eğer self.dietitian_user yerine sadece dietitian_user yazsaydık
        # bu dietitian_user değişkeni sadece setUp() metodu çalışırken var olurdu
        # setUp() bitip est_dietitian_can_view_own_client metoduna geçildiğinde
        # o dietitian_user değişkeni tamamen kaybolmuş olurdu
        self.dietitian1_user = User.objects.create_user(
            username="dietitian1", password="testpass123"
        )
        self.dietitian1 = DietitianProfile.objects.create(
            user=self.dietitian1_user, specialty="Sports Nutrition"
        )

        # 2. dietitian ve onun kullanıcı hesabı
        self.dietitian2_user = User.objects.create_user(
            username="dietitian2", password="testpass123"
        )
        self.dietitian2 = DietitianProfile.objects.create(
            user=self.dietitian2_user, specialty="Weight Management"
        )

        # 1. dietitian'a bağlı bir client
        self.client1_user = User.objects.create_user(
            username="client1", password="testpass123"
        )
        self.client1 = ClientProfile.objects.create(
            user=self.client1_user,
            gender="F",
            goal="L",
            age=25,
            height_cm=165,
            weight_kg=60,
            activity_level="Moderately",
            dietitian=self.dietitian1,
        )

    def test_dietitian_can_view_own_client(self):
        # Senaryo 1: dietitian1, kendi danışanı client1'in detayına bakabilmeli

        # Django'nun test aracıyla, dietitian1 olarak giriş yapıyoruz
        self.client.login(username="dietitian1", password="testpass123")

        # dietitian1, client1'in detay sayfasını istiyor
        response = self.client.get(f"/tracker/client/{self.client1.id}/")

        # assertEqual(a, b) a ile b'nin birbirine eşit olup olmadığını
        # kontrol eder eşit değilse test BAŞARISIZ olur ve bize haber verir
        # burada gerçekte dönen kod ile beklediğimiz kod (200)
        # karşılaştırılıyor 200 = OK yani istek başarıyla işlendi demek
        # Beklentimiz sayfa başarıyla açılsın
        self.assertEqual(response.status_code, 200)

    def test_dietitian_cannot_view_other_dietitians_client(self):
        # Senaryo 2: dietitian2, client1'in detayına bakmaya çalışıyor
        # ama client1, dietitian1'e bağlı (dietitian2'ye değil) 
        # bu yüzden erişim REDDEDİLMELİ (403 Forbidden)

        self.client.login(username="dietitian2", password="testpass123")

        response = self.client.get(f"/tracker/client/{self.client1.id}/")

        # Beklentimiz: 403 (Forbidden) dönsün, çünkü dietitian2'nin
        # bu client'a bakma yetkisi yok
        self.assertEqual(response.status_code, 403)

    def test_client_cannot_view_client_detail_page(self):
        # Senaryo 3: client1_user, dietitian DEĞİL (bir ClientProfile'ı
        # var ama DietitianProfile'ı yok) Bu sayfa sadece dietitian'lar
        # için bu yüzden erişim REDDEDİLMELİ (403 Forbidden)

        self.client.login(username="client1", password="testpass123")

        response = self.client.get(f"/tracker/client/{self.client1.id}/")

        # Beklentimiz: 403 (Forbidden) dönsün, çünkü client1_user'ın
        # hiç DietitianProfile'ı yok
        self.assertEqual(response.status_code, 403)


class DeleteMealItemViewTests(TestCase):
    def setUp(self):
        # İki farklı kullanıcı oluşturuyoruz biri MealItem'ın
        # gerçek sahibi diğeri başkasının verisine erişmeye
        # çalışan kişiyi temsil edecek

        self.owner_user = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123"
        )

        # düzenlenecek bir MealItem oluşturmak için önce
        # bir Food, sonra bir Meal, en son da o Meal'a bağlı MealItem
        # lazım (MealItem, hem Food'a hem Meal'a ForeignKey ile bağlı)
        self.food = Food.objects.create(
            food_name="Test Food", calorie_per_100g=100
        )
        self.meal = Meal.objects.create(
            user=self.owner_user, meal_type="B"
        )
        self.meal_item = MealItem.objects.create(
            meal=self.meal, food=self.food, quantity_g=150
        )

    def test_owner_can_delete_own_meal_item(self):
        # Senaryo 1: owner_user, kendi MealItem'ını siliyor - başarılı olmalı

        self.client.login(username="owner", password="testpass123")

        response = self.client.post(
            f"/tracker/delete-meal_item/{self.meal_item.id}/"
        )

        # DeleteMealItemView işlem başarılı olunca meal_log sayfasına yönlendiriliyor
        # Yönlendirme isteklerinin durum kodu 302'ymiş (200 değil)
        self.assertEqual(response.status_code, 302)

        # MealItem'ın gerçekten silindiğini de kontrol edelim
        # MealItem.objects.filter(...).exists() bu id'ye sahip bir
        # kayıt var mı diye sorar — silindiyse False dönmeli
        self.assertFalse(MealItem.objects.filter(id=self.meal_item.id).exists())

    def test_other_user_cannot_delete_someone_elses_meal_item(self):
        # Senaryo 2: other_user, owner_user'a ait MealItem'ı silmeye
        # çalışıyor — bu REDDEDİLMELİ (403 Forbidden)

        self.client.login(username="other", password="testpass123")

        response = self.client.post(
            f"/tracker/delete-meal_item/{self.meal_item.id}/"
        )

        self.assertEqual(response.status_code, 403)

        # Ve MealItem'ın hala var olduğunu (silinmediğini) kontrol
        # edelim çünkü yetkisiz bir silme işlemi engellenmiş olmalı
        self.assertTrue(MealItem.objects.filter(id=self.meal_item.id).exists())


class EditMealItemViewTests(TestCase):
    def setUp(self):

        self.owner_user = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123"
        )

        self.food = Food.objects.create(
            food_name="Test Food", calorie_per_100g=100
        )
        self.meal = Meal.objects.create(
            user=self.owner_user, meal_type="B"
        )
        self.meal_item = MealItem.objects.create(
            meal=self.meal, food=self.food, quantity_g=150
        )

    def test_owner_can_view_edit_page(self):
        # Senaryo 1: owner_user, kendi MealItem'ının edit sayfasını
        # açabilmeli (GET isteği, 200 dönmeli)

        self.client.login(username="owner", password="testpass123")

        response = self.client.get(
            f"/tracker/edit-meal_item/{self.meal_item.id}/"
        )

        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_view_edit_page(self):
        # Senaryo 2: other_user, owner_user'a ait MealItem'ın edit
        # sayfasını açmaya çalışıyor REDDEDİLMELİ (403)

        self.client.login(username="other", password="testpass123")

        response = self.client.get(
            f"/tracker/edit-meal_item/{self.meal_item.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_owner_can_edit_own_meal_item(self):
        # Senaryo 3: owner_user kendi MealItem'ının miktarını
        # değiştiriyor başarılı olmalı

        self.client.login(username="owner", password="testpass123")

        response = self.client.post(
            f"/tracker/edit-meal_item/{self.meal_item.id}/",
            {"food": self.food.id, "quantity_g": 250},
        )

        # Başarılı kayıt sonrası meal_log'a yönlendirme (302) bekleriz
        self.assertEqual(response.status_code, 302)

        # Veritabanındaki gerçek değerin değiştiğini doğrulayalım
        # refresh_from_db(), bizim elimizdeki self.meal_item nesnesini
        # veritabanındaki GÜNCEL haliyle tazeler —çünkü self.meal_item,
        # hala setUp()'ta oluşturduğumuz ESKİ haliyle (150 gram) hafızada
        # duruyor veritabanı değişse bile bu Python nesnesi otomatik
        # güncellenmez
        self.meal_item.refresh_from_db()
        self.assertEqual(self.meal_item.quantity_g, 250)

    def test_other_user_cannot_edit_someone_elses_meal_item(self):
        # Senaryo 4: other_user, owner_user'a ait MealItem'ı
        # değiştirmeye çalışıyor — REDDEDİLMELİ (403) ve değer DEĞİŞMEMELİ

        self.client.login(username="other", password="testpass123")

        response = self.client.post(
            f"/tracker/edit-meal_item/{self.meal_item.id}/",
            {"food": self.food.id, "quantity_g": 999},
        )

        self.assertEqual(response.status_code, 403)

        # Değerin hala eski (150) olduğunu doğrulayalım yani
        # yetkisiz değişiklik denemesi hiçbir etki yapmamış olmalı
        self.meal_item.refresh_from_db()
        self.assertEqual(self.meal_item.quantity_g, 150)


class DeleteExerciseViewTests(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123"
        )

        self.exercise = Exercise.objects.create(
            exercise_name="Running", calories_per_hour=500
        )
        self.exercise_log = ExerciseLog.objects.create(
            user=self.owner_user, exercise=self.exercise, duration_minutes=30
        )

    def test_owner_can_delete_own_exercise_log(self):
        self.client.login(username="owner", password="testpass123")

        response = self.client.post(
            f"/tracker/delete-exercise/{self.exercise_log.id}/"
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            ExerciseLog.objects.filter(id=self.exercise_log.id).exists()
        )

    def test_other_user_cannot_delete_someone_elses_exercise_log(self):
        self.client.login(username="other", password="testpass123")

        response = self.client.post(
            f"/tracker/delete-exercise/{self.exercise_log.id}/"
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            ExerciseLog.objects.filter(id=self.exercise_log.id).exists()
        )


class EditExerciseViewTests(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123"
        )

        self.exercise = Exercise.objects.create(
            exercise_name="Running", calories_per_hour=500
        )
        self.exercise_log = ExerciseLog.objects.create(
            user=self.owner_user, exercise=self.exercise, duration_minutes=30
        )

    def test_owner_can_view_edit_page(self):
        self.client.login(username="owner", password="testpass123")

        response = self.client.get(
            f"/tracker/edit-exercise/{self.exercise_log.id}/"
        )

        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_view_edit_page(self):
        self.client.login(username="other", password="testpass123")

        response = self.client.get(
            f"/tracker/edit-exercise/{self.exercise_log.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_owner_can_edit_own_exercise_log(self):
        self.client.login(username="owner", password="testpass123")

        response = self.client.post(
            f"/tracker/edit-exercise/{self.exercise_log.id}/",
            {"exercise": self.exercise.id, "duration_minutes": 60},
        )

        self.assertEqual(response.status_code, 302)

        self.exercise_log.refresh_from_db()
        self.assertEqual(self.exercise_log.duration_minutes, 60)

    def test_other_user_cannot_edit_someone_elses_exercise_log(self):
        self.client.login(username="other", password="testpass123")

        response = self.client.post(
            f"/tracker/edit-exercise/{self.exercise_log.id}/",
            {"exercise": self.exercise.id, "duration_minutes": 999},
        )

        self.assertEqual(response.status_code, 403)

        self.exercise_log.refresh_from_db()
        self.assertEqual(self.exercise_log.duration_minutes, 30)


# ________________________
# HESAPLAMA TESTLERİ
# _______________________

class CalculateCaloriesConsumedTests(TestCase):
    def setUp(self):
        # Testler için bir kullanıcı ve birkaç Food nesnesi hazırlıyoruz
        # Meal/MealItemları her test metodunda ayrı ayrı oluşturacağız
        # çünkü her senaryonun ihtiyacı farklı.

        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        self.food = Food.objects.create(
            food_name="Test Food", calorie_per_100g=100
        )

        self.food2 = Food.objects.create(
            food_name="Test Food 2", calorie_per_100g=50
        )

    def test_single_food_item_calculated_correctly(self):
        # Senaryo 1: 200 gram, 100 kcal/100g'lık bir yiyecek yenirse
        # toplam 200 kcal olmalı

        # Meal.date bir DateTimeField (hem tarih hem saat + saat dilimi
        # bilgisi tutuyor) timezone.now() kullanıyoruz çünkü bu saat
        # dilimi bilgili bir değer veriyor burda date.today() kullandığımızda
        # Django "saat dilimsiz değer" uyarısı verdi
        meal = Meal.objects.create(
            user=self.user, meal_type="B", date=timezone.now()
        )
        MealItem.objects.create(meal=meal, food=self.food, quantity_g=200)

        # calculate_calories_consumed'a verdiğimiz date parametresi ise
        # farklı bir amaç için kullanılıyor fonksiyonun içinde
        # meal__date__date=date şeklinde SADECE tarih kısmıyla (saat
        # olmadan) karşılaştırılıyor bu yüzden burada date.today()
        # (saat dilimsiz bir tarih) kullanmak sorun değil hatta
        # fonksiyonun beklediği şey de zaten bu
        result = calculate_calories_consumed(self.user, date.today())

        self.assertEqual(result, 200)

    def test_multiple_food_items_summed_correctly(self):
        # Senaryo 2: aynı öğünde birden fazla MealItem varsa
        # kalorileri doğru toplanmalı
        # food: 100 kcal/100g, 200g yenirse -> 200 kcal
        # food2: 50 kcal/100g, 100g yenirse -> 50 kcal
        # Toplam 250 kcal

        meal = Meal.objects.create(
            user=self.user, meal_type="B", date=timezone.now()
        )
        MealItem.objects.create(meal=meal, food=self.food, quantity_g=200)
        MealItem.objects.create(meal=meal, food=self.food2, quantity_g=100)

        result = calculate_calories_consumed(self.user, date.today())

        self.assertEqual(result, 250)

    def test_meal_item_with_deleted_food_is_skipped(self):
        # Senaryo 3: Bir MealItem'ın food u silinmişse
        # fonksiyon bunu atlamalı hataya düşmemeli ve o MealItem'ı
        # toplam hesaba katmamalı

        meal = Meal.objects.create(
            user=self.user, meal_type="B", date=timezone.now()
        )
        # Önce normal bir MealItem (food'u dolu)
        MealItem.objects.create(meal=meal, food=self.food, quantity_g=200)

        # Sonra food'u silinmiş bir MealItem oluşturuyoruz
        # Bunun için önce geçici bir Food yaratıp bir MealItem'a bağlıyoruz
        # sonra o Food'u siliyoruz Food silinince on_delete=SET_NULL
        # sayesinde MealItem.food otomatik None oluyor (MealItem'ın
        # kendisi silinmiyor)
        temp_food = Food.objects.create(
            food_name="Temporary Food", calorie_per_100g=300
        )
        deleted_food_item = MealItem.objects.create(
            meal=meal, food=temp_food, quantity_g=100
        )
        temp_food.delete()

        # deleted_food_item'ı veritabanından tazeleyip food'unun
        # gerçekten None olduğunu doğrulayalım
        deleted_food_item.refresh_from_db()
        # gerçekten food'u silinmiş bir MealItem oluşturabildik mi diye kontrol ediyoruz
        self.assertIsNone(deleted_food_item.food)

        # sadece food'u dolu olan MealItem
        # hesaba katılmalı (200 kcal), silinen food'lu olan atlanmalı
        result = calculate_calories_consumed(self.user, date.today())

        self.assertEqual(result, 200)

    def test_meal_from_different_date_not_included(self):
        # Senaryo 4: fonksiyon sadece belirtilentarihe bakmalı
        # dünkü bir Meal'ı oluşturup bugünün kalorisini hesaplarken
        # dünkü verinin hesaba katılmadığını doğruluyoruz

        yesterday = timezone.now() - timedelta(days=1)
        meal_yesterday = Meal.objects.create(
            user=self.user, meal_type="B", date=yesterday
        )
        MealItem.objects.create(
            meal=meal_yesterday, food=self.food, quantity_g=200
        )

        # bugün için hiç Meal oluşturmadık bu yüzden bugünün
        # toplam kalorisi 0 olmalı dünkü 200 kcallik kayıt hesaba katılmamalı
        result = calculate_calories_consumed(self.user, date.today())

        self.assertEqual(result, 0)

    def test_another_users_meal_not_included(self):
        # Senaryo 5: fonksiyon sadece BELİRTİLEN kullanıcının verisine bakmalı
        # başka bir kullanıcının bugünkü Meal'ı bizim
        # kullanıcımızın kalori hesabına karışmamalı

        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        other_meal = Meal.objects.create(
            user=other_user, meal_type="B", date=timezone.now()
        )
        MealItem.objects.create(
            meal=other_meal, food=self.food, quantity_g=200
        )

        # self.user için hiç Meal oluşturmadık bu yüzden self.user'ın
        # bugünkü toplam kalorisi 0 olmalı other_user'ın 200 kcal'lik
        # kaydı hesaba katılmamalı
        result = calculate_calories_consumed(self.user, date.today())

        self.assertEqual(result, 0)


class CalculateCaloriesBurnedTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        self.exercise = Exercise.objects.create(
            exercise_name="Running", calories_per_hour=600
        )
        self.exercise2 = Exercise.objects.create(
            exercise_name="Walking", calories_per_hour=300
        )

    def test_single_exercise_log_calculated_correctly(self):
        # Senaryo 1: 60 dakika, 600 kcal/saatlik bir egzersiz yapılırsa
        # toplam 600 kcal olmalı

        ExerciseLog.objects.create(
            user=self.user,
            exercise=self.exercise,
            duration_minutes=60,
            date=timezone.now(),
        )

        result = calculate_calories_burned(self.user, date.today())

        self.assertEqual(result, 600)

    def test_multiple_exercise_logs_summed_correctly(self):
        # Senaryo 2: Aynı günde birden fazla ExerciseLog varsa
        # kalorileri doğru toplanmalı
        # exercise: 600 kcal/saat 60 dk yapılırsa -> 600 kcal
        # exercise2: 300 kcal/saat 30 dk yapılırsa -> 150 kcal
        # toplam 750 kcal

        ExerciseLog.objects.create(
            user=self.user,
            exercise=self.exercise,
            duration_minutes=60,
            date=timezone.now(),
        )
        ExerciseLog.objects.create(
            user=self.user,
            exercise=self.exercise2,
            duration_minutes=30,
            date=timezone.now(),
        )

        result = calculate_calories_burned(self.user, date.today())

        self.assertEqual(result, 750)

    def test_exercise_log_with_deleted_exercise_is_skipped(self):
        # Senaryo 3: bir ExerciseLog'un exercise'ı silinmişse
        # fonksiyon bunu hesaba katmamalı

        ExerciseLog.objects.create(
            user=self.user,
            exercise=self.exercise,
            duration_minutes=60,
            date=timezone.now(),
        )

        temp_exercise = Exercise.objects.create(
            exercise_name="Temporary Exercise", calories_per_hour=1000
        )
        deleted_exercise_log = ExerciseLog.objects.create(
            user=self.user,
            exercise=temp_exercise,
            duration_minutes=30,
            date=timezone.now(),
        )
        temp_exercise.delete()

        # Ön kontrol exercise gerçekten None oldu mu
        deleted_exercise_log.refresh_from_db()
        self.assertIsNone(deleted_exercise_log.exercise)

        # Asıl test sadece exercise'ı dolu olan log hesaba katılmalı
        # (600 kcal) silinen exerciselı olan atlanmalı
        result = calculate_calories_burned(self.user, date.today())

        self.assertEqual(result, 600)

    def test_exercise_log_from_different_date_not_included(self):
        # Senaryo 4: Fonksiyon sadece BELİRTİLEN tarihe bakmalı

        yesterday = timezone.now() - timedelta(days=1)
        ExerciseLog.objects.create(
            user=self.user,
            exercise=self.exercise,
            duration_minutes=60,
            date=yesterday,
        )

        # Bugün için hiç ExerciseLog oluşturmadık bu yüzden bugünün toplamı 0 olmalı
        result = calculate_calories_burned(self.user, date.today())

        self.assertEqual(result, 0)

    def test_another_users_exercise_log_not_included(self):
        # Senaryo 5: Fonksiyon sadece BELİRTİLEN kullanıcının verisine
        # bakmalı başka kullanıcının verisi karışmamalı

        other_user = User.objects.create_user(
            username="otheruser2", password="testpass123"
        )
        ExerciseLog.objects.create(
            user=other_user,
            exercise=self.exercise,
            duration_minutes=60,
            date=timezone.now(),
        )

        # self.user için hiç ExerciseLog oluşturmadık bu yüzden 0
        # olmalı other_user'ın kaydı karışmamalı
        result = calculate_calories_burned(self.user, date.today())

        self.assertEqual(result, 0)


class CalculateWeeklyCaloriesConsumedTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.food = Food.objects.create(
            food_name="Test Food", calorie_per_100g=100
        )

    def test_meal_within_last_7_days_is_included(self):
        # Senaryo 1: 3 gün önceki bir Meal, haftalık toplama dahil edilmeli
        # 200 kcal

        three_days_ago = timezone.now() - timedelta(days=3)
        meal = Meal.objects.create(
            user=self.user, meal_type="B", date=three_days_ago
        )
        MealItem.objects.create(meal=meal, food=self.food, quantity_g=200)

        result = calculate_weekly_calories_consumed(self.user, date.today())

        self.assertEqual(result, 200)

    def test_meal_older_than_7_days_not_included(self):
        # Senaryo 2: 10 gün önceki bir Meal haftalık toplamın dışında kalmalı

        ten_days_ago = timezone.now() - timedelta(days=10)
        meal = Meal.objects.create(
            user=self.user, meal_type="B", date=ten_days_ago
        )
        MealItem.objects.create(meal=meal, food=self.food, quantity_g=200)

        # 10 gün önceki veri dışarıda kaldığı için toplam 0 olmalı
        result = calculate_weekly_calories_consumed(self.user, date.today())

        self.assertEqual(result, 0)

    def test_meal_exactly_7_days_ago_is_included(self):
        # Senaryo 3 (sınır durumu): fonksiyondaki filtre __gte
        # kullanıyor (week_ago = date - timedelta(days=7)) yani
        # "büyük eşit"o yüzden tam olarak 7 gün önceki veri de dahil edilmeli

        exactly_7_days_ago = timezone.now() - timedelta(days=7)
        meal = Meal.objects.create(
            user=self.user, meal_type="B", date=exactly_7_days_ago
        )
        MealItem.objects.create(meal=meal, food=self.food, quantity_g=200)

        result = calculate_weekly_calories_consumed(self.user, date.today())

        self.assertEqual(result, 200)


class CalculateWeeklyCaloriesBurnedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.exercise = Exercise.objects.create(
            exercise_name="Running", calories_per_hour=600
        )

    def test_exercise_log_within_last_7_days_is_included(self):
        # Senaryo 1: 3 gün önceki bir ExerciseLog haftalık toplama
        # dahil edilmeli (600 kcal)

        three_days_ago = timezone.now() - timedelta(days=3)
        ExerciseLog.objects.create(
            user=self.user,
            exercise=self.exercise,
            duration_minutes=60,
            date=three_days_ago,
        )

        result = calculate_weekly_calories_burned(self.user, date.today())

        self.assertEqual(result, 600)

    def test_exercise_log_older_than_7_days_not_included(self):
        # Senaryo 2: 10 gün önceki bir ExerciseLog haftalık toplamın dışında kalmalı

        ten_days_ago = timezone.now() - timedelta(days=10)
        ExerciseLog.objects.create(
            user=self.user,
            exercise=self.exercise,
            duration_minutes=60,
            date=ten_days_ago,
        )

        result = calculate_weekly_calories_burned(self.user, date.today())

        self.assertEqual(result, 0)

    def test_exercise_log_exactly_7_days_ago_is_included(self):
        # Senaryo 3 (sınır durumu): tam olarak 7 gün önceki veri de
        # dahil edilmeli (filtre __gte kullanıyor, yani büyük eşit)

        exactly_7_days_ago = timezone.now() - timedelta(days=7)
        ExerciseLog.objects.create(
            user=self.user,
            exercise=self.exercise,
            duration_minutes=60,
            date=exactly_7_days_ago,
        )

        result = calculate_weekly_calories_burned(self.user, date.today())

        self.assertEqual(result, 600)


# ________________________
# VERİ GRUPLAMA TESTLERİ
# ________________________


class GetDailyBreakdownTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.food = Food.objects.create(
            food_name="Test Food", calorie_per_100g=100
        )

    def test_meal_items_grouped_by_correct_meal_type(self):
        # Senaryo: bir breakfast ve bir lunch MealItem oluşturuyoruz
        # her birinin doğru gruba (breakfast/lunch) düştüğünü
        # yanlış gruplara karışmadığını doğruluyoruz

        breakfast_meal = Meal.objects.create(
            user=self.user, meal_type="B", date=timezone.now()
        )
        breakfast_item = MealItem.objects.create(
            meal=breakfast_meal, food=self.food, quantity_g=100
        )

        lunch_meal = Meal.objects.create(
            user=self.user, meal_type="L", date=timezone.now()
        )
        lunch_item = MealItem.objects.create(
            meal=lunch_meal, food=self.food, quantity_g=100
        )

        result = get_daily_breakdown(self.user, date.today())

        # breakfast grubunda sadece breakfast_item olmalı
        self.assertIn(breakfast_item, result["breakfast"])
        self.assertNotIn(lunch_item, result["breakfast"])

        # lunch grubunda sadece lunch_item olmalı
        self.assertIn(lunch_item, result["lunch"])
        self.assertNotIn(breakfast_item, result["lunch"])

        # dinner ve snack grupları boş olmalı
        self.assertEqual(len(result["dinner"]), 0)
        self.assertEqual(len(result["snack"]), 0)


class GetSelectedDateTests(TestCase):
    def setUp(self):
        # RequestFactory gerçek bir HTTP isteği atmadan sahte bir
        # request nesnesi oluşturmamızı sağlıyor  get_selected_date
        # fonksiyonu bir request bekliyor biz de ona uygun bir tane üretiyoruz burada
        self.factory = RequestFactory()

    def test_date_param_provided_is_used(self):
        # Senaryo 1: URL'de ?date=2026-08-01 varsa fonksiyon bu tarihi kullanmalı

        request = self.factory.get("/tracker/?date=2026-08-01")

        result = get_selected_date(request)

        self.assertEqual(result, date(2026, 8, 1))

    def test_no_date_param_defaults_to_today(self):
        # Senaryo 2: URL'de hiç date parametresi yoksa
        # fonksiyon bugünün tarihini döndürmeli

        request = self.factory.get("/tracker/")

        result = get_selected_date(request)

        self.assertEqual(result, date.today())
