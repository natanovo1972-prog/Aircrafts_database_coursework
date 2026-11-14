import time
from config import countries_to_track
from database import DBManager
from api_client import DataCollector


def print_header(title):
    """Вспомогательная функция длявывода заголовков отчетов."""
    print("\n" + "=" * 80)
    print(f" {title.upper()} ".center(80, "="))
    print("=" * 80)

def main():
    db = DBManager()
    collector = DataCollector()

    print ("Инициализация базы данных и создание таблиц")
    db.create_tables()

    print("\n[Шаг 1]: Получение географических координат стран")
    for country in countries_to_track:
        try:
            time.sleep(1)
            bbox = collector.get_country_coordinate(country)
            country_id = db.insert_country(country, bbox)
            print(f" Страна {country} успешно сохранена с ID: {country_id}")
        except Exception as e:
            print(f"Ошибка при обработке координат для страны {country}: {e}")

    print("\n[Шаг 2]: Сбор данных о самолетах в воздухе")
    countries_in_db = db.get_all_countries()
    for country_id, name, lamin, lomin, lamax, lomax in countries_in_db:
        bbox = [float(lamin), float(lomin), float(lamax), float(lomax)]
        print(f"Сканирование воздушного пространства страны {name}")
        try:
            time.sleep(5)
            flights = collector.get_aircraft_coordinate(bbox)
            if flights:
                db.insert_flights(country_id, flights)
                print(f"Успешно добавлено {len(flights)} самолетов")
            else:
                print(f"В данной локации самолетов не обнаружено")
        except Exception as e:
            print(f"Ошибка при работе с API OpenSky для страны: {name}: {e}")

    print("\nСбор данных о самолетах и странах завершен. Запуск аналитических мтодов")

    # 1. Список всех стран и количество самолетов
    print("1. Количество самолетов по странам")
    countries_stats = db.get_countries_and_aeroplanes_count()
    print(f"{'Страна':<25} | {'Количество самолетов':<20}")
    print("-" * 50)
    for country_name, count in countries_stats:
        print(f"{country_name:<25} | {count:<20}")

    # 2. Средняя скорость самолетов
    print("2. Средняя скорость самолетов")
    avg_speed = db.get_avg_speed()
    print(f"Средняя скорость всех зафиксированных самолетов: {avg_speed:.2f} м/с")

    # 3. Список всех уникальных воздушных судов
    print("3. Список всех зафиксированных воздушных судов")
    all_planes = db.get_all_aeroplanes()
    print(f"{'ICAO24':<10} | {'Позывной':<10} | {'Широта':<10} | {'Долгота':<10} | {'Скорость (м/с)':<15}")
    print("-" * 65)
    for plane in all_planes[:10]:
        icao, callsign, lat, lon, vel, _ = plane
        callsign_str = callsign if callsign else "N/A"
        vel_str = f"{vel:.1f}" if vel is not None else "N/A"
        print(f"{icao:<10} | {callsign_str:<10} | {float(lat):<10.4f} | {float(lon):<10.4f} | {vel_str:<15}")
    print(f"Всего уникальных бортов в базе: {len(all_planes)}")

    # 4. Список самолетов со скоростью выше средней
    print("4. Самолеты со скоростью выше средней")
    fastest_planes = db.get_aeroplanes_with_higher_speed()
    print(f"{'ICAO24':<10} | {'Позывной':<10} | {'Текущая скорость (м/с)':<25}")
    print("-" * 55)
    for plane in fastest_planes[:10]:
        icao, callsign, vel = plane
        callsign_str = callsign if callsign else "N/A"
        print(f"{icao:<10} | {callsign_str:<10} | {float(vel):<25.2f}")
    print(f"Всего самолетов летящих быстрее среднего: {len(fastest_planes)}")

     # 5. Поиск самолетов по ключевому слову
    keyword = "A"
    print(f"5. Поиск самолетов по ключевому слову {keyword}")
    keyword_planes = db.get_aeroplanes_with_keyword(keyword)
    print(f"{'ICAO24':<10} | {'Позывной':<10} | {'Широта':<10} | {'Долгота':<10}")
    print("-" * 50)
    for plane in keyword_planes[:10]:
        icao, callsign, lat, lon = plane
        print(f"{icao:<10} | {callsign:<10} | {float(lat):<10.4f} | {float(lon):<10.4f}")
    print(f"Всего найдено совпадений: {len(keyword_planes)}")

    db.close()
    print("\n" + "=" * 80)
    print(" Работа программы успешно завершена! ".center(80, "="))
    print("=" * 80)


if __name__ == "__main__":
    main()
