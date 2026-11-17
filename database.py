import psycopg2
from config import db_config
from psycopg2 import extras


class DBManager:
    """Класс для подключения к базе данных PostgreSQL"""
    def __init__(self):
        self.config = db_config
        self.conn = None

    def connect(self):
        """Установка соединения с базой данных"""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(**self.config)

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def create_tables(self):
        """Метод создает таблицу стран и таблицу самолетов в воздушных пространствах стран"""
        queries = [
             """
             CREATE TABLE IF NOT EXISTS countries (
             id SERIAL PRIMARY KEY,
             name VARCHAR(100) UNIQUE NOT NULL,
             lamin NUMERIC NOT NULL,
             lomin NUMERIC NOT NULL,
             lamax NUMERIC NOT NULL,
             lomax NUMERIC NOT NULL);
             """,
             """
             CREATE TABLE IF NOT EXISTS flights (
             id SERIAL PRIMARY KEY,
             country_id INT REFERENCES countries(id),
             icao24 VARCHAR(10) NOT NULL,
             callsign VARCHAR(20),
             longitude NUMERIC,
             latitude NUMERIC,
             velocity NUMERIC,
             on_ground BOOLEAN,
             last_contact INT,
             captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
             """
             ]
        self.connect()
        with self.conn.cursor() as cursor:
            for query in queries:
                cursor.execute(query)
            self.conn.commit()

    def insert_country(self, name, bbox):
        """Вставка новой страны или обновление координат существующей.
        Возвращает id страны в базе данных"""
        query = """
            INSERT INTO countries (name, lamin, lomin, lamax, lomax)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET lamin = EXCLUDED.lamin, lomin = EXCLUDED.lomin,
                lamax = EXCLUDED.lamax, lomax = EXCLUDED.lomax
            RETURNING id;
            """
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query, (name, bbox[0], bbox[1], bbox[2], bbox[3]))
            country_id = cursor.fetchone()[0]
            self.conn.commit()
            return country_id

    def get_all_countries(self):
        """Метод получает список всех стран, зарегистрированных в базе данных,
        для последующего сбора данных"""
        query = """SELECT id, name, lamin, lomin, lamax, lomax FROM countries"""
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def insert_flights(self, country_id, flights_data):
        """Метод получает информацию о самолетах и добавляет ее в базу данных"""
        if not flights_data:
            return
        query = """
            INSERT INTO flights (country_id, icao24, callsign, longitude, latitude, velocity, on_ground, last_contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
        data_to_insert = [
            (
                country_id, f[0], f[1].strip() if f[1] else None, f[5], f[6], f[9], f[8], f[4]
            )
            for f in flights_data
        ]
        self.connect()
        with self.conn.cursor() as cursor:
            extras.execute_batch(cursor, query, data_to_insert)
            self.conn.commit()

    def get_countries_and_aeroplanes_count(self):
        """Метод получает список всех стран и количество самолетов в их воздушных пространствах"""
        query = """
            SELECT c.name, COUNT(f.id) as aeroplane_count
            FROM countries c
            LEFT JOIN flights f ON c.id = f.country_id
            GROUP BY c.id, c.name
            ORDER BY aeroplane_count DESC;
            """
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def get_all_aeroplanes(self):
        """Метод получает список всех воздушных судов"""
        query = """
            SELECT DISTINCT ON (icao24) icao24, callsign, longitude, latitude, velocity, captured_at
            FROM flights
            ORDER BY icao24, captured_at DESC;
            """
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def get_avg_speed(self):
        """Метод получает среднюю скорость по самолетам"""
        query = """
            SELECT AVG(velocity) FROM flights WHERE velocity IS NOT NULL;"""
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            result =  cursor.fetchone()
            return float(result[0]) if result[0] is not None else 0.0

    def get_aeroplanes_with_higher_speed(self):
        """Метод получает список всех самолетов со скоростью выше средней"""
        query = """
            SELECT icao24, callsign, velocity
            FROM flights
            WHERE velocity > (SELECT AVG(velocity) FROM flights WHERE velocity IS NOT NULL)
            ORDER BY velocity DESC
            """
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def get_aeroplanes_with_keyword(self, keyword):
        """Метод получает список всех самолетов,
        в позывном которых есть переданные в метод символы"""
        query = """
            SELECT icao24, callsign, longitude, latitude
            FROM flights
            WHERE callsign LIKE %s
            ORDER BY captured_at DESC;
            """
        search_pattern = f"%{keyword}%"
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query, (search_pattern, ))
            return cursor.fetchall()
