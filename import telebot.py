import telebot
import psycopg2
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = '7819265666:AAGONawI3yvy8PGsFXxH0bG04AHzOcHt4Gs'
ADMIN_ID = 1594554887 
bot = telebot.TeleBot(BOT_TOKEN)

DB_CONFIG = {
    'dbname': 'nexttrip001',
    'user': 'postgres',
    'password': 'aiymzhan',
    'host': 'localhost',
    'port': '5432'
}

def db_connect():
    return psycopg2.connect(**DB_CONFIG)

@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🌍 Просмотреть города", callback_data="view_cities"),
        InlineKeyboardButton("🛫 Найти рейсы", callback_data="find_flights"),
        InlineKeyboardButton("🏨 Отели", callback_data="hotels"),
        InlineKeyboardButton("📍 Список гидов", callback_data="attractions"),
        InlineKeyboardButton("📋 Мои маршруты", callback_data="my_routes"),
        InlineKeyboardButton("✅ Завершить", callback_data="finish_trip")
    )
    if message.from_user.id == ADMIN_ID:
        keyboard.add(InlineKeyboardButton("🔑 Панель администратора", callback_data="admin_panel"))
    
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в бота для планирования путешествий! Выберите действие:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "view_cities")
def view_cities(call):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT city_name, country FROM cities")
    cities = cursor.fetchall()
    cursor.close()
    conn.close()

    cities_text = "\n".join([f"🌆 {city} ({country})" for city, country in cities])
    bot.send_message(call.message.chat.id, f"Доступные города:\n\n{cities_text}")

@bot.callback_query_handler(func=lambda call: call.data == "hotels")
def view_hotels(call):
    msg = bot.send_message(call.message.chat.id, "Введите название города для поиска отелей.")
    bot.register_next_step_handler(msg, show_hotels)

def show_hotels(message):
    city_name = message.text
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.name, h.stars, h.address
        FROM hotels h
        JOIN cities c ON h.city_id = c.city_id
        WHERE c.city_name = %s
    """, (city_name,))
    hotels = cursor.fetchall()
    cursor.close()
    conn.close()

    if hotels:
        hotels_text = "\n".join([f"{hotel[0]} ({hotel[1]} звезд) - {hotel[2]}" for hotel in hotels])
        bot.send_message(message.chat.id, f"Отели в {city_name}:\n\n{hotels_text}")
    else:
        bot.send_message(message.chat.id, f"Отели в городе {city_name} не найдены.")

@bot.callback_query_handler(func=lambda call: call.data == "my_routes")
def view_routes(call):
    user_id = call.from_user.id  
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.route_name, r.description, c.city_name
        FROM routes r
        JOIN cities c ON r.departure_city_id = c.city_id
        JOIN bookings b ON r.route_id = b.route_id
        JOIN users u ON b.user_id = u.user_id
        WHERE u.user_id = %s
    """, (user_id,))
    routes = cursor.fetchall()
    cursor.close()
    conn.close()

    if routes:
        routes_text = "\n".join([f"{route[0]}: {route[1]} (Город: {route[2]})" for route in routes])
        bot.send_message(call.message.chat.id, f"Ваши маршруты:\n\n{routes_text}")
    else:
        bot.send_message(call.message.chat.id, "У вас нет сохраненных маршрутов.")

@bot.callback_query_handler(func=lambda call: call.data == "find_flights")
def find_flights(call):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("По городам", callback_data="flights_by_cities"),
        InlineKeyboardButton("По дате", callback_data="flights_by_date"),
    )
    bot.send_message(
        call.message.chat.id,
        "Как вы хотите искать рейсы?",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "flights_by_cities")
def flights_by_cities(call):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.flight_number, c1.city_name, c2.city_name, f.departure_time, f.arrival_time, f.airline
        FROM flights f
        JOIN cities c1 ON f.departure_city_id = c1.city_id
        JOIN cities c2 ON f.arrival_city_id = c2.city_id
    """)
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    flights_text = "\n\n".join([f"✈️ {flight[0]}: {flight[1]} → {flight[2]}\n"
                               f"🕒 Вылет: {flight[3]}\n🕒 Прилет: {flight[4]}\n🛩 Авиакомпания: {flight[5]}"
                               for flight in flights])
    bot.send_message(call.message.chat.id, f"Доступные рейсы:\n\n{flights_text}")

@bot.callback_query_handler(func=lambda call: call.data == "flights_by_date")
def flights_by_date(call):
    msg = bot.send_message(call.message.chat.id, "Введите дату в формате ГГГГ-ММ-ДД для поиска рейсов.")
    bot.register_next_step_handler(msg, show_flights_by_date)

def show_flights_by_date(message):
    flight_date = message.text
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.flight_number, c1.city_name, c2.city_name, f.departure_time, f.arrival_time, f.airline
        FROM flights f
        JOIN cities c1 ON f.departure_city_id = c1.city_id
        JOIN cities c2 ON f.arrival_city_id = c2.city_id
        WHERE DATE(f.departure_time) = %s
    """, (flight_date,))
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    if flights:
        flights_text = "\n\n".join([f"✈️ {flight[0]}: {flight[1]} → {flight[2]}\n"
                                   f"🕒 Вылет: {flight[3]}\n🕒 Прилет: {flight[4]}\n🛩 Авиакомпания: {flight[5]}"
                                   for flight in flights])
        bot.send_message(message.chat.id, f"Рейсы на {flight_date}:\n\n{flights_text}")
    else:
        bot.send_message(message.chat.id, f"Рейсы на {flight_date} не найдены.")

@bot.callback_query_handler(func=lambda call: call.data == "attractions")
def view_guides(call):
    msg = bot.send_message(call.message.chat.id, "Введите название города для поиска гидов.")
    bot.register_next_step_handler(msg, show_guides)

def show_guides(message):
    city_name = message.text
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(""" 
        SELECT g.name, g.experience_years, g.phone_number, g.email
        FROM guides g
        JOIN cities c ON g.city_id = c.city_id
        WHERE c.city_name = %s
    """, (city_name,))
    guides = cursor.fetchall()
    cursor.close()
    conn.close()

    if guides:
        guides_text = "\n".join([f"👨‍💼 {guide[0]} - {guide[1]} лет опыта\n📞 Телефон: {guide[2]}\n📧 Email: {guide[3]}"
                                 for guide in guides])
        bot.send_message(message.chat.id, f"Гиды в {city_name}:\n\n{guides_text}")
    else:
        bot.send_message(message.chat.id, f"Гиды в городе {city_name} не найдены.")

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel" and call.from_user.id == ADMIN_ID)
def admin_panel(call):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Добавить город", callback_data="add_city"),
        InlineKeyboardButton("Добавить рейс", callback_data="add_flight"),
    )
    bot.send_message(call.message.chat.id, "🔑 Панель администратора:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "add_city" and call.from_user.id == ADMIN_ID)
def add_city(call):
    msg = bot.send_message(call.message.chat.id, "Введите название нового города:")
    bot.register_next_step_handler(msg, process_city_name)

def process_city_name(message):
    city_name = message.text
    msg = bot.send_message(message.chat.id, "Введите страну этого города:")
    bot.register_next_step_handler(msg, process_country_name, city_name)

def process_country_name(message, city_name):
    country_name = message.text
    conn = db_connect()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT city_id FROM cities WHERE city_name = %s AND country = %s", (city_name, country_name))
        existing_city = cursor.fetchone()

        if existing_city:
            bot.send_message(message.chat.id, f"Город {city_name}, {country_name} уже существует.")
        else:
            cursor.execute("INSERT INTO cities (city_name, country) VALUES (%s, %s)", (city_name, country_name))
            conn.commit()
            bot.send_message(message.chat.id, f"Город {city_name}, {country_name} успешно добавлен.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

@bot.callback_query_handler(func=lambda call: call.data == "add_flight" and call.from_user.id == ADMIN_ID)
def add_flight(call):
    msg = bot.send_message(call.message.chat.id, "Введите номер рейса:")
    bot.register_next_step_handler(msg, process_flight_number)

def process_flight_number(message):
    flight_number = message.text
    msg = bot.send_message(message.chat.id, "Введите город отправления:")
    bot.register_next_step_handler(msg, process_departure_city, flight_number)

def process_departure_city(message, flight_number):
    departure_city = message.text
    msg = bot.send_message(message.chat.id, "Введите город назначения:")
    bot.register_next_step_handler(msg, process_arrival_city, flight_number, departure_city)

def process_arrival_city(message, flight_number, departure_city):
    arrival_city = message.text
    msg = bot.send_message(message.chat.id, "Введите дату и время вылета (ГГГГ-ММ-ДД ЧЧ:ММ):")
    bot.register_next_step_handler(msg, process_departure_time, flight_number, departure_city, arrival_city)

def process_departure_time(message, flight_number, departure_city, arrival_city):
    departure_time = message.text
    msg = bot.send_message(message.chat.id, "Введите дату и время прилета (ГГГГ-ММ-ДД ЧЧ:ММ):")
    bot.register_next_step_handler(msg, process_arrival_time, flight_number, departure_city, arrival_city, departure_time)

def process_arrival_time(message, flight_number, departure_city, arrival_city, departure_time):
    arrival_time = message.text
    msg = bot.send_message(message.chat.id, "Введите название авиакомпании:")
    bot.register_next_step_handler(msg, process_airline, flight_number, departure_city, arrival_city, departure_time, arrival_time)

def process_airline(message, flight_number, departure_city, arrival_city, departure_time, arrival_time):
    airline = message.text
    conn = db_connect()
    cursor = conn.cursor()

    try:
        print(f"Departure city: {departure_city}, Arrival city: {arrival_city}")
        
        cursor.execute("SELECT city_id FROM cities WHERE city_name ILIKE %s", (departure_city,))
        departure_city_id = cursor.fetchone()
        cursor.execute("SELECT city_id FROM cities WHERE city_name ILIKE %s", (arrival_city,))
        arrival_city_id = cursor.fetchone()

        if departure_city_id and arrival_city_id:
            cursor.execute(""" 
                INSERT INTO flights (flight_number, departure_city_id, arrival_city_id, departure_time, arrival_time, airline)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (flight_number, departure_city_id[0], arrival_city_id[0], departure_time, arrival_time, airline))
            conn.commit()
            bot.send_message(message.chat.id, f"Рейс {flight_number} успешно добавлен.")
        else:
            bot.send_message(message.chat.id, "Ошибка: один из городов не найден в базе данных.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()


@bot.callback_query_handler(func=lambda call: call.data == "finish_trip")
def finish_trip(call):
    bot.send_message(
        call.message.chat.id,
        "Ваша поездка спланирована. Спасибо за использование нашего сервиса! Удачного путешествия!"
    )

bot.polling(none_stop=True)
