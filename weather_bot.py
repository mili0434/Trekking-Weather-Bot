import tkinter as tk
from tkinter import ttk, messagebox
import requests
import sqlite3
from datetime import datetime

# Bright & Beautiful Indigo / Blue Theme (Strictly NO BLACK)
BG_COLOR = "#1e1b4b"        # Rich Indigo background
FG_COLOR = "#ffffff"        # Clean White text
BUTTON_BG = "#7c3aed"       # Vibrant Purple buttons
BUTTON_FG = "#ffffff"       # White text on buttons
ENTRY_BG = "#312e81"        # Lighter indigo for input boxes
FRAME_BG = "#1e1b4b"        # Matching frame background

INDIAN_DESTINATIONS = [
    "Manali",
    "Kedarnath",
    "Leh Ladakh",
    "Gulmarg",
    "Darjeeling",
    "Ooty",
    "Rishikesh",
    "Roorkee",
    "Shimla",
    "Mussoorie"
]

DESTINATION_COORDS = {
    "Manali": (32.2432, 77.1892),
    "Kedarnath": (30.7346, 79.0669),
    "Leh Ladakh": (34.1526, 77.5771),
    "Gulmarg": (34.0495, 74.3820),
    "Darjeeling": (27.0410, 88.2663),
    "Ooty": (11.4102, 76.6950),
    "Rishikesh": (30.0869, 78.2676),
    "Roorkee": (29.8543, 77.8880),
    "Shimla": (31.1048, 77.1734),
    "Mussoorie": (30.4598, 78.0644)
}

def init_database():
    conn = sqlite3.connect("weather_history.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            location TEXT,
            temperature REAL,
            condition TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_search(location, temp, condition):
    conn = sqlite3.connect("weather_history.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO searches (timestamp, location, temperature, condition) VALUES (?, ?, ?, ?)",
                   (timestamp, location, temp, condition))
    conn.commit()
    conn.close()

def get_weather_graphic_and_desc(code):
    if code == 0:
        return "☀️", "Clear & Sunny", "#facc15"
    elif code in [1, 2]:
        return "🌤️", "Partly Cloudy", "#fde68a"
    elif code == 3:
        return "☁️", "Overcast Clouds", "#e5e7eb"
    elif code in [45, 48]:
        return "🌫️", "Foggy", "#d1d5db"
    elif code in [51, 53, 55, 56, 57]:
        
        return "🌦️", "Light Drizzle", "#93c5fd"
    elif code in [61, 63, 65, 66, 67]:
        return "🌧️", "Rainy", "#60a5fa"
    elif code in [71, 73, 75, 77]:
        return "❄️", "Snow Fall", "#bfdbfe"
    elif code in [80, 81, 82]:
        return "🌧️", "Rain Showers", "#2563eb"
    elif code in [85, 86]:
        return "❄️", "Snow Showers", "#93c5fd"
    elif code in [95, 96, 99]:
        return "⛈️", "Thunderstorm", "#93c5fd"
    else:
        return "☁️", "Cloudy", "#e5e7eb"

def get_packing_guide(temperature, weather_code):
    items = []
    if temperature < 0:
        items.append(("🧥", "Heavy winter jacket"))
        items.append(("🧣", "Thermal underwear"))
        items.append(("🧤", "Warm gloves and hat"))
        items.append(("🥾", "Insulated boots"))
    elif temperature < 10:
        items.append(("🧥", "Heavy jacket or fleece"))
        items.append(("👖", "Long pants"))
        items.append(("🧦", "Warm socks"))
    elif temperature < 20:
        items.append(("👕", "Light jacket or sweater"))
        items.append(("👖", "Long pants or jeans"))
    else:
        items.append(("👕", "Light clothing (t-shirt)"))
        items.append(("🧢", "Sunscreen and hat"))
        
    rainy_codes = [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99]
    snow_codes = [71, 73, 75, 77, 85, 86]
    
    if weather_code in rainy_codes:
        items.append(("🌧️", "Raincoat or waterproof jacket"))
        items.append(("🎒", "Waterproof backpack cover"))
    elif weather_code in snow_codes:
        items.append(("❄️", "Snow boots and gaiters"))
        items.append(("🕶️", "UV-protection sunglasses"))
        
    items.append(("💧", "Water bottle (at least 2L)"))
    items.append(("🍫", "High-energy snacks"))
    items.append(("🩹", "First-aid kit"))
    return items

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏔️ Trekking Weather Bot")
        self.root.geometry("600x1020")
        self.root.resizable(False, False)
        
        init_database()
        self.create_ui()

    def create_ui(self):
        self.root.configure(bg=BG_COLOR)
        
        # Title Label
        title_frame = tk.Frame(self.root, bg=BUTTON_BG, pady=10)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="🏔️ Trekking Weather Bot", font=("Helvetica Neue", 16, "bold"), bg=BUTTON_BG, fg=FG_COLOR)
        title_label.pack()

        # Input Section Frame
        self.input_section = tk.LabelFrame(self.root, text="Select a Popular Destination:", font=("Helvetica Neue", 11, "bold"), bg=FRAME_BG, fg=FG_COLOR, padx=15, pady=10)
        self.input_section.pack(fill=tk.X, padx=15, pady=10)

        # Dropdown for Popular Destinations
        self.dest_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self.input_section, textvariable=self.dest_var, values=INDIAN_DESTINATIONS, state="readonly", font=("Helvetica Neue", 11))
        self.dropdown.pack(fill=tk.X, pady=5)
        self.dropdown.set("Select a destination...")

        # Custom Destination Entry
        tk.Label(self.input_section, text="Or Enter Custom Destination:", font=("Helvetica Neue", 10), bg=FRAME_BG, fg=FG_COLOR).pack(anchor="w", pady=(5,0))
        
        self.location_entry = tk.Entry(self.input_section, font=("Helvetica Neue", 11), bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR)
        self.location_entry.pack(fill=tk.X, pady=5)

        # Buttons Frame
        btn_frame = tk.Frame(self.input_section, bg=FRAME_BG)
        btn_frame.pack(fill=tk.X, pady=5)

        self.check_btn = tk.Button(btn_frame, text="Check Weather", command=self.fetch_weather, font=("Helvetica Neue", 10, "bold"), bg=BUTTON_BG, fg=BUTTON_FG, relief=tk.FLAT, padx=10, pady=5)
        self.check_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.history_btn = tk.Button(btn_frame, text="View History", command=self.show_history, font=("Helvetica Neue", 10, "bold"), bg=BUTTON_BG, fg=BUTTON_FG, relief=tk.FLAT, padx=10, pady=5)
        self.history_btn.pack(side=tk.LEFT)

        # Current Weather Frame
        self.current_frame = tk.LabelFrame(self.root, text="Current Weather", font=("Helvetica Neue", 11, "bold"), bg=FRAME_BG, fg=FG_COLOR, padx=15, pady=10)
        self.current_frame.pack(fill=tk.X, padx=15, pady=5)

        # Graphical Weather Icon
        self.weather_icon_label = tk.Label(self.current_frame, text="☀️", font=("Helvetica Neue", 60), bg=FRAME_BG, fg="#facc15")
        self.weather_icon_label.pack(pady=(2, 0))

        self.weather_label = tk.Label(self.current_frame, text="Select a destination to check weather", font=("Helvetica Neue", 10), bg=FRAME_BG, fg=FG_COLOR, justify=tk.CENTER)
        self.weather_label.pack(fill=tk.X, pady=5)

        # Trekking Status Label (Safe/Unsafe)
        self.status_label = tk.Label(self.current_frame, text="", font=("Helvetica Neue", 11, "bold"), bg=FRAME_BG, fg="#22c55e", justify=tk.CENTER)
        self.status_label.pack(fill=tk.X, pady=(2, 5))

        # Forecast Frame
        self.forecast_frame = tk.LabelFrame(self.root, text="Next 3 Days Forecast", font=("Helvetica Neue", 11, "bold"), bg=FRAME_BG, fg=FG_COLOR, padx=15, pady=10)
        self.forecast_frame.pack(fill=tk.X, padx=15, pady=5)

        self.forecast_label = tk.Label(self.forecast_frame, text="No forecast available yet.", font=("Helvetica Neue", 10), bg=FRAME_BG, fg=FG_COLOR, justify=tk.LEFT)
        self.forecast_label.pack(fill=tk.X, pady=5)

        # Packing Guide Frame
        self.packing_frame = tk.LabelFrame(self.root, text="Smart Packing Guide", font=("Helvetica Neue", 11, "bold"), bg=FRAME_BG, fg=FG_COLOR, padx=15, pady=10)
        self.packing_frame.pack(fill=tk.X, padx=15, pady=5)

        self.packing_label = tk.Label(self.packing_frame, text="Packing recommendations will appear here.", font=("Helvetica Neue", 10), bg=FRAME_BG, fg=FG_COLOR, justify=tk.LEFT)
        self.packing_label.pack(fill=tk.X, pady=5)

    def fetch_weather(self):
        location = self.dest_var.get()
        custom_loc = self.location_entry.get().strip()

        lat, lon = None, None
        location_name = ""

        if custom_loc:
            location_name = custom_loc.capitalize()
            lat, lon = self.get_coordinates(location_name)
        elif location and location != "Select a destination...":
            location_name = location
            lat, lon = DESTINATION_COORDS.get(location, (None, None))
            if lat is None or lon is None:
                lat, lon = self.get_coordinates(location_name)
        else:
            messagebox.showerror("Error", "Please select or enter a valid location!")
            return

        if lat is None or lon is None:
            messagebox.showerror("Error", f"Could not find coordinates for '{location_name}'. Try typing it in custom destination.")
            return

        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
            response = requests.get(url)
            data = response.json()

            current = data["current"]
            temp = current["temperature_2m"]
            code = current["weather_code"]
            wind = current["wind_speed_10m"]
            
            graphic_icon, condition_desc, icon_color = get_weather_graphic_and_desc(code)
            self.weather_icon_label.config(text=graphic_icon, fg=icon_color)

            rainy_codes = [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99]
            if code in rainy_codes or wind > 30 or temp < -5:
                status_text = "⚠️ Bad weather: Not recommended today!"
                status_color = "#ef4444"
            else:
                status_text = "✅ Great weather for an adventure!"
                status_color = "#22c55e"

            weather_text = f"📍 {location_name}, India   |   🌡️ Temp: {temp}°C\n🌥️ Condition: {condition_desc}   |   💨 Wind: {wind} km/h"
            self.weather_label.config(text=weather_text)
            self.status_label.config(text=status_text, fg=status_color)
            
            daily = data["daily"]
            forecast_text = ""
            for i in range(1, 4):
                date = daily["time"][i]
                max_t = daily["temperature_2m_max"][i]
                min_t = daily["temperature_2m_min"][i]
                f_code = daily["weather_code"][i]
                f_icon, f_cond, _ = get_weather_graphic_and_desc(f_code)
                forecast_text += f"{f_icon} {date}: {f_cond} | Max: {max_t}°C | Min: {min_t}°C\n"
            
            self.forecast_label.config(text=forecast_text.strip())

            packing_items = get_packing_guide(temp, code)
            packing_text = "\n".join([f"• {icon} {item}" for icon, item in packing_items])
            self.packing_label.config(text=packing_text)

            log_search(location_name, temp, condition_desc)

        except Exception as e:
            messagebox.showerror("API Error", f"Failed to fetch weather data: {str(e)}")

    def get_coordinates(self, place_name):
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={place_name}&count=1"
            res = requests.get(geo_url).json()
            if "results" in res and len(res["results"]) > 0:
                lat = res["results"][0]["latitude"]
                lon = res["results"][0]["longitude"]
                return lat, lon
        except:
            pass
        return None, None

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Weather Search History")
        history_window.geometry("700x400")
        history_window.configure(bg=BG_COLOR)

        tk.Label(history_window, text="Weather Search History", font=("Helvetica Neue", 14, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)

        columns = ("ID", "Date & Time", "Location", "Temperature (°C)", "Weather Condition")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        conn = sqlite3.connect("weather_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM searches ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()