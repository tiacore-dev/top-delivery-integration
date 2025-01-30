from datetime import datetime, date, time

# Преобразуем объект времени в строку


def time_to_string(time_obj):
    return time_obj.strftime('%H:%M:%S') if time_obj else None

# Преобразуем объект даты в строку


def date_to_string(date_obj):
    return date_obj.strftime('%Y-%m-%d') if date_obj else None

# Рекурсивная функция для преобразования всех datetime объектов


def serialize_dates(obj):
    if isinstance(obj, dict):
        return {key: serialize_dates(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_dates(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()  # или используйте date_to_string
    elif isinstance(obj, date):  # Здесь используем date
        return date_to_string(obj)
    elif isinstance(obj, time):  # Здесь используем time
        return time_to_string(obj)
    return obj  # Возвращаем объект, если он не требует преобразования
