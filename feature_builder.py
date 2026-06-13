# Импорт библиотек
import pandas as pd

# Функция для предобработки данных (для внедрения)
def preprocess_data(users_df, visits_df, ads_df, surf_df, device_df, cloud_df):
    # Копируем, чтобы не изменять исходные данные
    users = users_df.copy()
    visits = visits_df.copy()
    ads = ads_df.copy()
    surf = surf_df.copy()
    device = device_df.copy()
    cloud = cloud_df.copy()

    # Удаляем дубликаты по user_id (оставляем первое вхождение)
    users = users.drop_duplicates(subset='user_id', keep='first')
    ads = ads.drop_duplicates(subset='user_id', keep='first')
    surf = surf.drop_duplicates(subset='user_id', keep='first')
    device = device.drop_duplicates(subset='user_id', keep='first')
    cloud = cloud.drop_duplicates(subset='user_id', keep='first')

    # Преобразуем дату в datetime
    visits['date'] = pd.to_datetime(visits['date'])
    # Добавляем день недели (0=понедельник, 6=воскресенье)
    visits['weekday'] = visits['date'].dt.dayofweek

    # Агрегация базовых счетчиков
    visits_agg = visits.groupby('user_id').agg(
        total_visits=('session_id', 'count'),
        active_days=('date', 'nunique')
    ).reset_index()   

    # Доли по времени суток
    daytime_dummies = pd.get_dummies(visits['daytime'], prefix='daytime')
    visits_daytime = pd.concat([visits['user_id'], daytime_dummies], axis=1)
    visits_daytime_agg = visits_daytime.groupby('user_id').mean().add_prefix('prop_')

     # Доли по дням недели 
    weekday_dummies = pd.get_dummies(visits['weekday'], prefix='weekday')
    visits_weekday = pd.concat([visits['user_id'], weekday_dummies], axis=1)
    visits_weekday_agg = visits_weekday.groupby('user_id').mean().add_prefix('prop_')

    # Доли по категориям сайтов
    cat_dummies = pd.get_dummies(visits['website_category'], prefix='cat')
    visits_cat = pd.concat([visits['user_id'], cat_dummies], axis=1)
    visits_cat_agg = visits_cat.groupby('user_id').mean().add_prefix('prop_')

    # Объединение всех таблиц 
    merged = users
    for df in [ads, surf, device, cloud, visits_agg, visits_daytime_agg, visits_weekday_agg, visits_cat_agg]:
        merged = merged.merge(df, on='user_id', how='left')
    
    # Заполняем NaN нулями (предполагаем, что отсутствие данных означает отсутствие использования)
    merged['cloud_usage'] = merged['cloud_usage'].fillna(0).astype(int)
    
    return merged