import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from .models.profiles import ClientProfile
from .models.logs import MealItem
from collections import Counter

from django.utils import timezone
from datetime import timedelta


def build_user_dataframe():
    # Tüm kullanıcı profillerini al
    profiles = ClientProfile.objects.all()

    # Kullanıcı profillerini bir listeye dönüştür
    data = []
    for profile in profiles:
        data.append({
            'user_id': profile.user.id,
            'age': profile.age,
            'gender': profile.gender,
            'goal': profile.goal,
        })

    # Kullanıcı verilerini (user_id, age, gender, goal) bir pandas
    # DataFrame'e (tablo yapısına) dönüştürüyoruz bu noktada
    # gender/goal sütunları hâlâ metin ("M", "L")
    df = pd.DataFrame(data)
    # One-hot encoding: gender ve goal sütunları kategorik
    # olduğu için, benzerlik hesaplamasında yanlış sıralama/büyüklük
    # ilişkisi çıkmasın diye her kategoriyi ayrı bir 0-1 sütununa
    # bölüyoruz  (gender_M, gender_F, goal_L, goal_MT, goal_G)
    df = pd.get_dummies(df, columns=['gender', 'goal'])

    # MinMaxScaler ile age'i de 0-1 aralığına
    # sıkıştırıyoruz böylece tüm sütunlar eşit ağırlıkta karşılaştırılır
    scaler = MinMaxScaler()
    df['age'] = scaler.fit_transform(df[['age']])

    return df


def compute_similarity_matrix():

    # Tüm kullanıcıların age/gender/goal bilgisini içeren
    # one-hot encoded ve scale edilmiş tabloyu al
    df = build_user_dataframe()
    # hangi satır hangi kullanıcıya ait
    # bilgisini kaybetmemek için önce yedekliyoruz
    user_ids = df['user_id']
    # user_id sadece bir kimlik numarası benzerlik hesabına
    # katılması anlamsızı olur (ID ler birbirine yakın
    # diye kullanıcılar benzer sayılmamalı) bu yüzden çıkarıyoruz
    df = df.drop(columns=['user_id'])
    # Her kullanıcıyı bir profil vektörü gibi düşünüp
    # her kullanıcı çiftinin birbirine ne kadar benzediğini hesaplar
    # sonuç NxN boyutunda bir matris - N kullanıcı sayııs 
    similarity_matrix = cosine_similarity(df)
    return similarity_matrix, user_ids


def find_similar_users(user_id, top_n=5):
    similarity_matrix, user_ids = compute_similarity_matrix()
    # matrisin satır/sütun numaraları 0,1,2... şeklinde, gerçek
    # user_id'lerle aynı değil bu yüzden user_ids listesinden
    # userın kaçıncı sırada olduğunu buluyoruz
    user_index = user_ids.tolist().index(user_id)
    # Matrisin o satırını çekiyoruz  bu bizim kullanıcımızın
    # diğer tüm kullanıcılarla (kendisi dahil) olan benzerlik
    # skorlarını içeren tek boyutlu bir liste
    similarities = similarity_matrix[user_index]
    # argsort() değerleri küçükten büyüğe sıralasak hangi indexler
    # hangi sırada olurdu onu döndürür (değerlerin kendisini değil index'lerini)!
    # [::-1] ile tersine çeviriyoruz çünkü biz
    # büyükten küçüğe (en benzerden en az benzere) istiyoruz
    sorted_indices = similarities.argsort()[::-1]  # Benzerlikleri büyükten küçüğe sıralıyoruz
    # sorted_indices'in ilk elemanı her zaman kullanıcının KENDİSİ
    # (skor 1) bunu atlayıp sonraki top_n taneyi alıyoruz
    # bunlar en benzer top_n kişinin matris index'leri
    top_indices = sorted_indices[1:top_n+1]
    # Bulduğumuz index'leri gerçek user_idlere çeviriyoruz
    similar_users = user_ids.iloc[top_indices]

    return similar_users


def recommended_foods(user_id, top_n_users=5, top_n_foods=5):
    similar_users = find_similar_users(user_id, top_n_users)
    week_ago = timezone.now().date() - timedelta(days=7)

    similar_meal_items = MealItem.objects.filter(meal__user__id__in=similar_users, meal__date__date__gte=week_ago)
    foods = []
    for items in similar_meal_items:
        if items.food:
            foods.append(items.food)
    frequency = Counter(foods)
    most_common_foods = frequency.most_common(top_n_foods)

    return most_common_foods





