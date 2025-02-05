import customtkinter as ctk
import psycopg2
from tkinter import messagebox
import bcrypt
import re
import webbrowser
from PIL import Image, ImageTk

try:
    conn = psycopg2.connect(
        host="localhost",
        database="project15",
        user="postgres",
        password="1234567890"
    )
    cursor = conn.cursor()
except Exception as e:
    print("Ошибка подключения к базе данных:", e)
    exit()

PRIMARY_COLOR = "#4B9CD3"
SECONDARY_COLOR = "#F5F5F5"
BUTTON_COLOR = "#1F7A8C"
BUTTON_HOVER_COLOR = "#145374"
TEXT_COLOR = "#333333"
FONT = ("Roboto", 14)
TITLE_FONT = ("Roboto", 20, "bold")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class RegisterWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Регистрация")
        self.geometry("900x600")
        self.resizable(False, False)

        form_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=SECONDARY_COLOR)
        form_frame.pack(pady=50, padx=50, fill="both", expand=True)


        ctk.CTkLabel(form_frame, text="Регистрация", font=TITLE_FONT, text_color=PRIMARY_COLOR).pack(pady=20)

        self.entry_username = ctk.CTkEntry(form_frame, placeholder_text="Имя пользователя")
        self.entry_username.pack(pady=10)

        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="Электронная почта")
        self.entry_email.pack(pady=10)

        self.entry_password = ctk.CTkEntry(form_frame, placeholder_text="Пароль", show="*")
        self.entry_password.pack(pady=10)

        ctk.CTkLabel(form_frame, text="Пароль должен содержать не менее 8 символов.", font=("Roboto", 10), text_color=PRIMARY_COLOR).pack(pady=5)

        self.btn_register = ctk.CTkButton(
            form_frame,
            text="Зарегистрироваться",
            command=self.register_user,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        self.btn_register.pack(pady=20)
    def register_user(self):
        username = self.entry_username.get()
        email = self.entry_email.get()
        password = self.entry_password.get()

        if not username or not email or not password:
           messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
           return

        if len(password) < 8:
           messagebox.showerror("Ошибка", "Пароль должен содержать не менее 8 символов!")
           return

        if not re.search(r"\d", password):
           messagebox.showerror("Ошибка", "Пароль должен содержать хотя бы одну цифру!")
           return
        if not re.search(r"[A-Z]", password):
           messagebox.showerror("Ошибка", "Пароль должен содержать хотя бы одну заглавную букву!")
           return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
           messagebox.showerror("Ошибка", "Пароль должен содержать хотя бы один специальный символ!")
           return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hashed_password.decode('utf-8'))
        )
            conn.commit()
            messagebox.showinfo("Успех", "Вы успешно зарегистрировались!")
            self.destroy()
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при регистрации: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при регистрации: {e}")
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Вход")
        self.geometry("900x600")
        self.resizable(False, False)

        self.configure(fg_color=SECONDARY_COLOR)
        form_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=SECONDARY_COLOR)
        form_frame.pack(pady=50, padx=50, fill="both", expand=True)

        ctk.CTkLabel(form_frame, text="Вход", font=TITLE_FONT, text_color=PRIMARY_COLOR).pack(pady=20)

        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="Электронная почта")
        self.entry_email.pack(pady=10)

        self.entry_password = ctk.CTkEntry(form_frame, placeholder_text="Пароль", show="*")
        self.entry_password.pack(pady=10)

        self.btn_login = ctk.CTkButton(
            form_frame,
            text="Войти",
            command=self.login_user,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        self.btn_login.pack(pady=20)

        self.btn_register = ctk.CTkButton(
            form_frame,
            text="Регистрация",
            command=self.open_register_window,
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        self.btn_register.pack(pady=10)
    def login_user(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        if not email or not password:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            cursor.execute(
                "SELECT email, password_hash FROM users WHERE email = %s",
                (email,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                messagebox.showinfo("Успех", "Добро пожаловать!")
                self.open_main_window()
            else:
                messagebox.showerror("Ошибка", "Неверная почта или пароль.")
        except Exception as e:
            print(f"Ошибка при входе: {e}")
            conn.rollback()
            messagebox.showerror("Ошибка", f"Ошибка при входе: {e}")
    def open_register_window(self):
        RegisterWindow(self)
    def open_main_window(self):
        self.destroy()
        app = TravelApp()
        app.mainloop()
class TravelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Планировщик путешествий")
        self.geometry("900x600")
        self.resizable(False, False)

        self.configure_grid()
        self.create_navigation()
        self.create_main_frame()
    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    def create_navigation(self):
        self.nav_frame = ctk.CTkFrame(self, width=250, corner_radius=15, fg_color=PRIMARY_COLOR)
        self.nav_frame.grid(row=0, column=0, sticky="nsw")

        ctk.CTkLabel(self.nav_frame, text="Навигация", font=TITLE_FONT, text_color="white").pack(pady=10)
        self.create_nav_buttons()
    def create_nav_buttons(self):
        buttons = [
            ("Маршруты", self.show_routes),
            ("Города", self.show_cities),
            ("Отели", self.show_hotels),
            ("Культура", self.show_attractions),
            ("Гиды", self.show_guides),
            ("Отзывы", self.show_reviews),
            ("Бронирования", self.show_bookings),
            ("Добавить маршрут", self.add_route_window),
            ("Перейти в Telegram-бот", self.open_telegram_bot),
        ]

        for text, command in buttons:
            ctk.CTkButton(
                self.nav_frame,
                text=text,
                command=command,
                fg_color=BUTTON_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color="white"
            ).pack(fill="x", padx=10, pady=5)
    def create_main_frame(self):
   
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=SECONDARY_COLOR)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=10)

        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=700, height=400)
        scrollable_frame.pack(pady=5, padx=5, fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="Добро пожаловать в Планировщик Путешествий!", font=TITLE_FONT, text_color=PRIMARY_COLOR).pack(pady=10)

        map_image = Image.open("img/titulka.jpg")  
        map_image = map_image.resize((900, 600)) 
        map_image_tk = ImageTk.PhotoImage(map_image)  

        canvas = ctk.CTkCanvas(scrollable_frame, width=900, height=640)
        canvas.pack(pady=10)

        canvas.create_image(0, 0, anchor="nw", image=map_image_tk)  
        canvas.image = map_image_tk 
    def open_telegram_bot(self):
        webbrowser.open("https://t.me/nexttrip06_bot")
    def show_routes(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Ваши маршруты", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=10)

        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=700, height=500)
        scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)

        try:
            cursor.execute("SELECT route_name FROM routes")
            routes = cursor.fetchall()
            for route in routes:
                ctk.CTkLabel(scrollable_frame, text=route[0], text_color="white").pack(pady=2, anchor="w")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {e}")
    def show_cities(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Список городов", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=10)

        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=700, height=500)
        scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)

        cities = [
            ('Астана', 'Казахстан', 'img/астана.jpg'),
            ('Алматы', 'Казахстан', 'img/алматы.jpg'),
            ('Майами', 'США', 'img/майами.jpg'),
            ('Нью-Йорк', 'США', 'img/ньюйорк.jpg'),
            ('Лондон', 'Великобритания', 'img/лондон.jpg'),
            ('Париж', 'Франция', 'img/париж.jpg'),
            ('Токио', 'Япония', 'img/токио.jpeg'),
            ('Берлин', 'Германия', 'img/берлин.jpg'),
            ('Сидней', 'Австралия', 'img/сидней.jpg'),
            ('Сан-Франциско', 'США', 'img/санфранциско.jpg'),
            ('Рио-де-Жанейро', 'Бразилия', 'img/рио.jpg'),
            ('Барселона', 'Испания', 'img/Барселона.jpg')
    ]

        for city, country, img_path in cities:

            city_image = Image.open(img_path)
            city_image = city_image.resize((100, 100)) 
            city_image_ctk = ImageTk.PhotoImage(city_image)

            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(pady=5, anchor="w", fill="x")

            text_label = ctk.CTkLabel(frame, text=f"{city}, {country}", text_color="white")
            text_label.pack(side="left", anchor="w")

            canvas = ctk.CTkCanvas(frame, width=100, height=100)
            canvas.pack(side="right", padx=10)

            canvas.create_image(0, 0, anchor="nw", image=city_image_ctk)
            canvas.image = city_image_ctk 
    def show_hotels(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Список отелей", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=10)

        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=700, height=500)
        scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)

        hotels = [
           ('The Ritz-Carlton', 1, 5, 'Улица Кабанбай Батыр, 1', 'img/отельастана.jpg'),
           ('Hilton Astana', 3, 5, 'Проспект Кабанбай Батыр, 60', 'img/HiltonAstana.jpg'),
           ('The Savoy', 4, 5, 'Strand', 'img/TheSavoy.jpg'),
           ('Hotel de Crillon', 5, 5, '10 Place de la Concorde', 'img/HoteldeCrillon.jpg'),
           ('Park Hyatt Tokyo', 6, 5, '3-7-1-2 Nishi Shinjuku', 'img/ParkHyattTokyo.jpg'),
           ('Hotel Adlon Kempinski', 7, 5, 'Unter den Linden 77', 'img/adlon1.jpg'),
           ('Shangri-La Sydney', 8, 5, '176 Cumberland Street', 'img/ShangriLaSydney.jpg'),
           ('The Westin St. Francis', 9, 5, '335 Powell Street', 'img/TheWestinSt.Francis.jpg'),
           ('Four Seasons Hotel New York', 10, 5, '57 E 57th St', 'img/FourSeasons1.jpg')
    ]

        for hotel, _, _, address, img_path in hotels:

            hotel_image = Image.open(img_path)
            hotel_image = hotel_image.resize((100, 100))  
            hotel_image_ctk = ImageTk.PhotoImage(hotel_image)

            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(pady=5, anchor="w", fill="x")

            text_label = ctk.CTkLabel(frame, text=f"{hotel}: {address}", text_color="white")
            text_label.pack(side="left", anchor="w")

            canvas = ctk.CTkCanvas(frame, width=100, height=100)
            canvas.pack(side="right", padx=10)

            canvas.create_image(0, 0, anchor="nw", image=hotel_image_ctk)
            canvas.image = hotel_image_ctk  
    def show_attractions(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Культура", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=10)

        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=700, height=500)
        scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)

        attractions = [
            ('Байтерек', 1, 'Башня Байтерек - символ Астаны и Казахстана.', 'img/bait.jpg'),
            ('Медеу', 2, 'Высокогорный каток Медеу в Алматы.', 'img/medeu.jpg'),
            ('Астана Опера', 3, 'Оперы и балеты в Астане.', 'img/astanaopera.jpg'),
            ('Биг-Бен', 4, 'Знаменитая часовая башня Биг-Бен в Лондоне.', 'img/bigben.jpg'),
            ('Эйфелева башня', 5, 'Эйфелева башня в Париже, символ Франции.', 'img/eiffel.jpg'),
            ('Храм Сэнсодзи', 6, 'Древний буддийский храм в Токио.', 'img/sensoji.jpg'),
            ('Бранденбургские ворота', 7, 'Знаменитые ворота в Берлине.', 'img/brandenburg_gate.jpg'),
            ('Сиднейский оперный театр', 8, 'Знаменитый оперный театр в Сиднее.', 'img/sydneyopera.jpg'),
            ('Золотые Ворота', 9, 'Исторический висячий мост в Сан-Франциско.', 'img/golden_gate.jpg'),
            ('Центральный парк', 10, 'Огромный городской парк в Нью-Йорке.', 'img/central1.jpg')
    ]

        for attraction, _, description, img_path in attractions:

            attraction_image = Image.open(img_path)
            attraction_image = attraction_image.resize((100, 100))  
            attraction_image_ctk = ImageTk.PhotoImage(attraction_image)

            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(pady=5, anchor="w", fill="x")

            text_label = ctk.CTkLabel(frame, text=f"{attraction}: {description}", text_color="white")
            text_label.pack(side="left", anchor="w")

            canvas = ctk.CTkCanvas(frame, width=100, height=100)
            canvas.pack(side="right", padx=10)

            canvas.create_image(0, 0, anchor="nw", image=attraction_image_ctk)
            canvas.image = attraction_image_ctk 
    def show_guides(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Список гидов", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=10)

        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=700, height=500)
        scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)

        try:
            cursor.execute("SELECT name, experience_years FROM guides")
            guides = cursor.fetchall()
            for guide in guides:
                ctk.CTkLabel(scrollable_frame, text=f"{guide[0]} ({guide[1]} лет опыта)", text_color="white").pack(pady=2, anchor="w")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {e}")
    def show_reviews(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Отзывы", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=10)

        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=700, height=500)
        scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)

        try:
            cursor.execute("SELECT comment, rating FROM reviews")
            reviews = cursor.fetchall()
            for review in reviews:
                ctk.CTkLabel(scrollable_frame, text=f"Отзыв: {review[0]} | Оценка: {review[1]}", text_color="white").pack(pady=2, anchor="w")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {e}")
    def show_bookings(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Бронирования", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=10)

        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=700, height=500)
        scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)

        try:
            query = """
            SELECT users.username, routes.route_name 
            FROM bookings 
            JOIN users ON bookings.user_id = users.user_id 
            JOIN routes ON bookings.route_id = routes.route_id 
            """ 
            cursor.execute(query)
            bookings = cursor.fetchall()
            for booking in bookings:
                ctk.CTkLabel(scrollable_frame, text=f"Пользователь {booking[0]} забронировал маршрут {booking[1]}", text_color="white").pack(pady=2, anchor="w")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {e}")
    def add_route_window(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Добавить маршрут", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=10)

        self.entry_route_name = ctk.CTkEntry(self.main_frame, placeholder_text="Название маршрута")
        self.entry_route_name.pack(pady=5)

        self.entry_route_id = ctk.CTkEntry(self.main_frame, placeholder_text="ID маршрута")
        self.entry_route_id.pack(pady=5)

        self.entry_duration_days = ctk.CTkEntry(self.main_frame, placeholder_text="Длительность маршрута (в днях)")
        self.entry_duration_days.pack(pady=5)

        self.entry_departure_city_id = ctk.CTkEntry(self.main_frame, placeholder_text="ID города отправления") 
        self.entry_departure_city_id.pack(pady=5) 
        
        self.entry_arrival_city_id = ctk.CTkEntry(self.main_frame, placeholder_text="ID города прибытия") 
        self.entry_arrival_city_id.pack(pady=5) 
        
        self.entry_description = ctk.CTkEntry(self.main_frame, placeholder_text="Описание маршрута") 
        self.entry_description.pack(pady=5)

        self.btn_add_route = ctk.CTkButton(self.main_frame, text="Добавить", command=self.add_route)
        self.btn_add_route.pack(pady=5)
    def add_route(self):
        route_name = self.entry_route_name.get()
        route_id = self.entry_route_id.get()
        duration_days = self.entry_duration_days.get()
        departure_city_id = self.entry_departure_city_id.get() 
        arrival_city_id = self.entry_arrival_city_id.get() 
        description = self.entry_description.get()

        if not route_name or not route_id or not duration_days or not departure_city_id or not arrival_city_id or not description:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            cursor.execute(
                "INSERT INTO routes (route_id, route_name, duration_days, departure_city_id,  arrival_city_id, description) VALUES (%s, %s, %s, %s, %s, %s)",
                (route_id, route_name, duration_days, departure_city_id,  arrival_city_id, description)
        )
            conn.commit()
            messagebox.showinfo("Успех", "Маршрут успешно добавлен!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Ошибка при добавлении маршрута: {e}")
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
