#!/usr/bin/env python3

import json
import requests
from datetime import datetime

# Конфигурация
latitude = 47.2364 # координаты
longitude = 39.7139 
appid = "you_key"
units = "metric"
lang = "ru"
url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={appid}&units={units}&lang={lang}"

# Локализация
localization = {
    "ru": {
        "feels_like": "Ощущается",
        "wind": "Ветер",
        "humidity": "Влажность",
        "pressure": "Давление",
        "today": "Сегодня",
        "tomorrow": "Завтра",
        "clouds": "Облачность",
        "m_s": "м/с",
        "hpa": "гПа",
        "percent": "%",
        "temp_now": "Сейчас",
        "temp_min": "Мин",
        "temp_max": "Макс",
        "sunrise": "Восход",
        "sunset": "Закат"
    }
}

# Иконки погоды  Nerd Fonts - Noto Sans
WEATHER_ICONS = {
    '01d': '󰖙',  # Ясно (день)
    '01n': '󰖔',  # Ясно (ночь)
    '02d': '󰖕',  # Малооблачно (день)
    '02n': '󰼱',  # Малооблачно (ночь)
    '03d': '󰖐',  # Облачно
    '03n': '󰖐',
    '04d': '󰖑',  # Пасмурно
    '04n': '󰖑',
    '09d': '󰼳',  # Ливень
    '09n': '󰼳',
    '10d': '󰖗',  # Дождь (день)
    '10n': '󰖗',  # Дождь (ночь)
    '11d': '󰖓',  # Гроза
    '11n': '󰖓',
    '13d': '󰖘',  # Снег
    '13n': '󰖘',
    '50d': '󰖑',  # Туман
    '50n': '󰖑'
}

def get_weather_data():
    """Получение данных о погоде"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(json.dumps({
            "text": "󰤮",
            "tooltip": f"Ошибка получения данных: {e}",
            "class": "error"
        }))
        exit(1)

def format_time(timestamp):
    """Форматирование времени"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%H:%M")

def format_date(dt_txt):
    """Форматирование даты"""
    dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
    
    # Определяем день
    today = datetime.now().date()
    target_date = dt.date()
    
    if target_date == today:
        return "Сегодня"
    elif target_date == today.replace(day=today.day + 1):
        return "Завтра"
    else:
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        return f"{dt.day:02d}.{dt.month:02d} {days[dt.weekday()]}"

def format_temp(temp):
    """Форматирование температуры"""
    return f"{round(temp):+}°C"

def create_tooltip(weather_data, loc):
    """Создание всплывающей подсказки"""
    city = weather_data['city']['name']
    current = weather_data['list'][0]
    city_info = weather_data['city']
    
    # Текущая погода
    current_temp = round(current['main']['temp'])
    feels_like = round(current['main']['feels_like'])
    description = current['weather'][0]['description'].capitalize()
    icon = current['weather'][0]['icon']
    wind_speed = round(current['wind']['speed'], 1)
    humidity = current['main']['humidity']
    pressure = current['main']['pressure']
    clouds = current['clouds']['all']
    
    tooltip = f"""
<span size="x-large" weight="bold">{city}</span>
<span size="large">{description} {WEATHER_ICONS.get(icon, '?')}</span>

<span weight="bold">Сейчас:</span>
  • {loc['temp_now']}: <span weight="bold">{format_temp(current_temp)}</span>
  • {loc['feels_like']}: {format_temp(feels_like)}
  • {loc['wind']}: {wind_speed} {loc['m_s']}
  • {loc['humidity']}: {humidity}{loc['percent']}
  • {loc['pressure']}: {pressure} {loc['hpa']}
  • {loc['clouds']}: {clouds}{loc['percent']}

<span weight="bold">Солнце:</span>
  • {loc['sunrise']}: {format_time(city_info['sunrise'])}
  • {loc['sunset']}: {format_time(city_info['sunset'])}

<span weight="bold">Прогноз на 24 часа:</span>
"""
    
    # Прогноз на ближайшие 24 часа (8 периодов по 3 часа)
    for i, forecast in enumerate(weather_data['list'][:8]):
        dt = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
        time_str = dt.strftime("%H:%M")
        temp = round(forecast['main']['temp'])
        forecast_icon = forecast['weather'][0]['icon']
        pop = forecast.get('pop', 0) * 100  # Вероятность осадков
        
        # Добавляем индикатор осадков если есть вероятность
        precip_text = f" ☔{pop:.0f}%" if pop > 20 else ""
        
        tooltip += f"  • {time_str}: {format_temp(temp)} {WEATHER_ICONS.get(forecast_icon, '?')}{precip_text}\n"
    
    # Прогноз по дням
    tooltip += f"\n<span weight='bold'>По дням:</span>\n"
    
    # Группируем по дням
    daily_forecasts = {}
    for forecast in weather_data['list']:
        dt = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
        day = dt.strftime("%Y-%m-%d")
        
        if day not in daily_forecasts:
            daily_forecasts[day] = []
        daily_forecasts[day].append(forecast)
    
    # Берем первые 5 дней
    for day_index, (day, forecasts) in enumerate(list(daily_forecasts.items())[:5]):
        temps = [f['main']['temp'] for f in forecasts]
        min_temp = min(temps)
        max_temp = max(temps)
        
        # Наиболее частая иконка за день
        icons = [f['weather'][0]['icon'] for f in forecasts]
        day_icon = max(set(icons), key=icons.count)
        
        # Описание погоды
        descriptions = [f['weather'][0]['description'] for f in forecasts]
        day_desc = max(set(descriptions), key=descriptions.count)
        
        dt = datetime.strptime(day, "%Y-%m-%d")
        day_name = format_date(forecasts[0]['dt_txt'])
        
        tooltip += f"  • {day_name}: {format_temp(min_temp)}/{format_temp(max_temp)} {WEATHER_ICONS.get(day_icon, '?')} {day_desc}\n"
    
    return tooltip.strip()

def main():
    loc = localization[lang]
    weather = get_weather_data()
    
    if not weather:
        return
    
    current = weather['list'][0]
    current_temp = round(current['main']['temp'])
    icon = current['weather'][0]['icon']
    
    # Определяем CSS класс для стилизации в зависимости от температуры
    temp_class = "normal"
    if current_temp > 30:
        temp_class = "hot"
    elif current_temp > 20:
        temp_class = "warm"
    elif current_temp < 0:
        temp_class = "cold"
    elif current_temp < 10:
        temp_class = "cool"
    
    # Формируем вывод для waybar
    data = {
        "text": f"{WEATHER_ICONS.get(icon, '?')} {format_temp(current_temp)}",
        "tooltip": create_tooltip(weather, loc),
        "class": temp_class,
        "percentage": min(100, max(0, current_temp + 30))  # Для прогресс-бара если нужно
    }
    
    print(json.dumps(data))

if __name__ == "__main__":
    main()