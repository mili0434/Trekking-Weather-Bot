
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import sqlite3
from datetime import datetime

# Colorful Theme Color Constants
GRADIENT_START = "#8b5cf6"  # Purple
GRADIENT_MID = "#3b82f6"    # Blue
GRADIENT_END = "#ec4899"    # Pink
FG_COLOR = "#ffffff"
CARD_BG = "#1e1b4b"
BUTTON_BG = "#8b5cf6"
BUTTON_FG = "#ffffff"
ENTRY_BG = "#312e81"
TEXT_BG = "#312e81"


def create_gradient(canvas, width, height, color1, color2, color3):
    """Create a vertical gradient on a Tkinter Canvas with three colors"""
    # Divide the canvas into segments
    for i in range(height):
        # Calculate interpolation for color1 -> color2 for first half, color2 -> color3 for second half
        ratio = i / height
        if i < height // 2:
            r = int(color1[0] + (color2[0] - color1[0]) * (i / (height // 2)))
            g = int(color1[1] + (color2[1] - color1[1]) * (i / (height // 2)))
            b = int(color1[2] + (color2[2] - color1[2]) * (i / (height // 2)))
        else:
            ratio2 = (i - height // 2) / (height // 2)
            r = int(color2[0] + (color3[0] - color2[0]) * ratio2)
            g = int(color2[1] + (color3[1] - color2[1]) * ratio2)
            b = int(color2[2] + (color3[2] - color2[2]) * ratio2)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=color, width=1)


# Convert hex colors to RGB tuples
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# Popular Indian trekking destinations
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
    "Mussoorie",
    "Nainital",
    "Munnar",
    "Coorg",
    "Srinagar",
    "Amritsar",
    "Varanasi",
    "Goa",
    "Mumbai",
    "Delhi",
    "Bangalore"
]

# Database configuration
DATABASE_NAME = "weather_history.db"


def init_database():
    """Initialize SQLite database and create weather_history table if it doesn't exist"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT NOT NULL,
            temperature REAL NOT NULL,
            weather_condition TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_weather_record(location, temperature, weather_condition):
    """Save a weather record to the SQLite database"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weather_history (timestamp, location, temperature, weather_condition)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, location, temperature, weather_condition))
    conn.commit()
    conn.close()


def get_all_weather_records():
    """Retrieve all weather records from the database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, location, temperature, weather_condition
        FROM weather_history
        ORDER BY timestamp DESC
    ''')
    records = cursor.fetchall()
    conn.close()
    return records


def get_coordinates(location):
    """Get latitude and longitude for a location using Open-Meteo's geocoding API"""
    base_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "name": result["name"],
                "country": result.get("country", "")
            }
        else:
            return None
    except Exception as e:
        return None


def get_weather(lat, lon):
    """Get current weather and 3-day forecast using Open-Meteo API"""
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "weather_code", "wind_speed_10m"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "forecast_days": 4,
        "timezone": "auto"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        return None


def interpret_weather_code(code):
    """Interpret WMO weather code into human-readable description"""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown weather condition")


def get_weather_emoji(code):
    """Get appropriate emoji for weather condition"""
    if code == 0 or code == 1:
        return "☀️"
    elif code == 2 or code == 3:
        return "⛅"
    elif code == 45 or code == 48:
        return "🌫️"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "🌧️"
    elif code in [71, 73, 75, 77, 85, 86]:
        return "❄️"
    elif code in [95, 96, 99]:
        return "⚡"
    else:
        return "🌤️"


def is_bad_weather(weather_code, wind_speed):
    """Check if weather conditions are bad for trekking"""
    bad_weather_codes = [51, 53, 55, 61, 63, 65, 71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99]
    high_wind_threshold = 30  # km/h
    
    if weather_code in bad_weather_codes or wind_speed >= high_wind_threshold:
        return True
    return False


def get_packing_guide(temperature, weather_code):
    """Generate a smart packing guide based on weather conditions"""
    items = []
    
    # Temperature-based recommendations
    if temperature < 0:
        items.append("🧥 Heavy winter jacket")
        items.append("🧦 Thermal underwear")
        items.append("🧤 Warm gloves and hat")
        items.append("🥾 Insulated boots")
    elif temperature < 10:
        items.append("🧥 Heavy jacket or fleece")
        items.append("👖 Long pants")
        items.append("🧦 Warm socks")
    elif temperature < 20:
        items.append("🧥 Light jacket or sweater")
        items.append("👖 Long pants or jeans")
    else:
        items.append("👕 Light clothing (t-shirt, shorts)")
        items.append("🧴 Sunscreen and hat")
    
    # Weather condition-based recommendations
    rain_codes = [51, 53, 55, 61, 63, 65, 80, 81, 82]
    snow_codes = [71, 73, 75, 77, 85, 86]
    thunderstorm_codes = [95, 96, 99]
    
    if weather_code in rain_codes:
        items.append("🧥 Raincoat or waterproof jacket")
        items.append("👖 Waterproof pants")
        items.append("🥾 Waterproof shoes/boots")
    if weather_code in snow_codes:
        items.append("🥾 Snow boots")
        items.append("👖 Snow pants")
        items.append("🕶️ Goggles or sunglasses")
    if weather_code in thunderstorm_codes:
        items.append("⚠️ Avoid trekking during thunderstorms!")
    
    # Always recommended
    items.append("💧 Plenty of water")
    items.append("🍎 Snacks")
    items.append("🩹 First-aid kit")
    
    return items


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌄 Trekking Weather Bot")
        self.root.geometry("600x950")
        self.root.resizable(False, False)
        
        # Initialize database
        init_database()
        
        # Create gradient background canvas
        self.canvas = tk.Canvas(self.root, width=600, height=950, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw gradient
        self.draw_gradient()
        
        # Configure ttk styles for colorful theme
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Frame style
        self.style.configure("TFrame", background=CARD_BG)
        
        # Label styles
        self.style.configure("Title.TLabel", font=("Arial", 20, "bold"), foreground=FG_COLOR, background=CARD_BG)
        self.style.configure("Section.TLabel", font=("Arial", 12, "bold"), foreground=FG_COLOR, background=CARD_BG)
        self.style.configure("WeatherEmoji.TLabel", font=("Arial", 80), foreground=FG_COLOR, background=CARD_BG)
        self.style.configure("Data.TLabel", font=("Arial", 12), foreground=FG_COLOR, background=CARD_BG)
        self.style.configure("TLabel", foreground=FG_COLOR, background=CARD_BG)
        
        # Combobox style
        self.style.configure("TCombobox", font=("Arial", 12), foreground=FG_COLOR, background=ENTRY_BG, fieldbackground=ENTRY_BG, borderwidth=0)
        self.style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)], background=[("readonly", ENTRY_BG)], foreground=[("readonly", FG_COLOR)])
        
        # Button style
        self.style.configure("TButton", font=("Arial", 11, "bold"), foreground=BUTTON_FG, background=BUTTON_BG, borderwidth=0, focuscolor="none")
        self.style.map("TButton", background=[("active", "#7c3aed"), ("pressed", "#6d28d9")], foreground=[("active", BUTTON_FG)])
        
        # LabelFrame style
        self.style.configure("TLabelframe", background=CARD_BG, borderwidth=2, relief="groove")
        self.style.configure("TLabelframe.Label", font=("Arial", 11, "bold"), foreground=FG_COLOR, background=CARD_BG)
        
        # Create main frame on canvas
        self.main_frame = ttk.Frame(self.canvas, padding="20")
        self.canvas.create_window(300, 475, window=self.main_frame, anchor="center")
        
        # Title
        self.title_label = ttk.Label(self.main_frame, text="🌄 Trekking Weather Bot", style="Title.TLabel")
        self.title_label.pack(pady=(0, 18))
        
        # Input section
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 18))
        
        # Dropdown label
        self.dropdown_label = ttk.Label(self.input_frame, text="Select a Popular Destination:", style="Section.TLabel")
        self.dropdown_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Dropdown menu
        self.destination_var = tk.StringVar()
        self.destination_dropdown = ttk.Combobox(
            self.input_frame, 
            textvariable=self.destination_var,
            values=INDIAN_DESTINATIONS,
            state="readonly",
            style="TCombobox"
        )
        self.destination_dropdown.pack(fill=tk.X, pady=(0, 8))
        self.destination_dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)
        
        # Custom entry label
        self.custom_label = ttk.Label(self.input_frame, text="Or Enter Custom Destination:", style="Section.TLabel")
        self.custom_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Custom entry box (tk widget, not ttk)
        self.location_entry = tk.Entry(self.input_frame, font=("Arial", 12), bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat")
        self.location_entry.pack(fill=tk.X, pady=(0, 8))
        self.location_entry.bind("<Return>", lambda e: self.check_weather())
        
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.input_frame)
        self.buttons_frame.pack(fill=tk.X)
        
        # Check weather button
        self.check_button = ttk.Button(self.buttons_frame, text="Check Weather", command=self.check_weather, style="TButton")
        self.check_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # View history button
        self.history_button = ttk.Button(self.buttons_frame, text="View History", command=self.view_history, style="TButton")
        self.history_button.pack(side=tk.LEFT)
        
        # Current weather section
        self.current_frame = ttk.LabelFrame(self.main_frame, text="Current Weather", padding="15")
        self.current_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.weather_emoji_label = ttk.Label(self.current_frame, text="🌤️", style="WeatherEmoji.TLabel")
        self.weather_emoji_label.pack(pady=(10, 5))
        
        self.location_display_label = ttk.Label(self.current_frame, text="Select a destination to check weather", style="Section.TLabel")
        self.location_display_label.pack()
        
        self.temp_label = ttk.Label(self.current_frame, text="", style="Data.TLabel")
        self.temp_label.pack()
        
        self.condition_label = ttk.Label(self.current_frame, text="", style="Data.TLabel")
        self.condition_label.pack()
        
        self.wind_label = ttk.Label(self.current_frame, text="", style="Data.TLabel")
        self.wind_label.pack()
        
        self.recommendation_label = ttk.Label(self.current_frame, text="", style="Section.TLabel")
        self.recommendation_label.pack(pady=(10, 0))
        
        # Forecast section
        self.forecast_frame = ttk.LabelFrame(self.main_frame, text="Next 3 Days Forecast", padding="15")
        self.forecast_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.forecast_labels = []
        for i in range(3):
            lbl = ttk.Label(self.forecast_frame, text="", style="Data.TLabel")
            lbl.pack(anchor=tk.W)
            self.forecast_labels.append(lbl)
        
        # Packing guide section
        self.packing_frame = ttk.LabelFrame(self.main_frame, text="Smart Packing Guide", padding="15")
        self.packing_frame.pack(fill=tk.BOTH, expand=True)
        
        self.packing_text = tk.Text(
            self.packing_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            height=10,
            state=tk.DISABLED,
            bg=TEXT_BG,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            relief="flat"
        )
        self.packing_text.pack(fill=tk.BOTH, expand=True)
        
    def draw_gradient(self):
        """Draw the colorful gradient on the canvas"""
        rgb_start = hex_to_rgb(GRADIENT_START)
        rgb_mid = hex_to_rgb(GRADIENT_MID)
        rgb_end = hex_to_rgb(GRADIENT_END)
        create_gradient(self.canvas, 600, 950, rgb_start, rgb_mid, rgb_end)
        
    def on_dropdown_select(self, event):
        """Handle dropdown selection and update entry box"""
        selected = self.destination_var.get()
        if selected:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, selected)
        
    def check_weather(self):
        # Get location from entry box (priority)
        location = self.location_entry.get().strip()
        
        # If entry is empty, check dropdown
        if not location:
            location = self.destination_var.get().strip()
        
        if not location:
            messagebox.showwarning("Warning", "Please select a destination or enter a custom location!")
            return
        
        # Get coordinates
        coords = get_coordinates(location)
        if not coords:
            messagebox.showerror("Error", f"Could not find location: {location}")
            return
        
        # Get weather data
        weather_data = get_weather(coords["latitude"], coords["longitude"])
        if not weather_data:
            messagebox.showerror("Error", "Could not fetch weather data!")
            return
        
        # Update GUI
        self.update_gui(coords, weather_data)
        
    def update_gui(self, coords, weather_data):
        # Extract current weather
        current = weather_data["current"]
        temperature = current["temperature_2m"]
        weather_code = current["weather_code"]
        wind_speed = current["wind_speed_10m"]
        weather_condition = interpret_weather_code(weather_code)
        weather_emoji = get_weather_emoji(weather_code)
        location_name = f"{coords['name']}, {coords['country']}"
        
        # Update current weather section
        self.weather_emoji_label.config(text=weather_emoji)
        self.location_display_label.config(text=location_name)
        self.temp_label.config(text=f"🌡️  Temperature: {temperature}°C")
        self.condition_label.config(text=f"☁️  Condition: {weather_condition}")
        self.wind_label.config(text=f"💨 Wind Speed: {wind_speed} km/h")
        
        # Update recommendation
        if is_bad_weather(weather_code, wind_speed):
            self.recommendation_label.config(text="⚠️  Bad weather: Not recommended for trekking today!", foreground="#ef4444")
        else:
            self.recommendation_label.config(text="✅  Great weather for an adventure!", foreground="#22c55e")
        
        # Extract and update forecast
        daily = weather_data["daily"]
        forecast_dates = daily["time"][1:4]
        forecast_weather_codes = daily["weather_code"][1:4]
        forecast_max_temps = daily["temperature_2m_max"][1:4]
        forecast_min_temps = daily["temperature_2m_min"][1:4]
        
        for i in range(3):
            date = forecast_dates[i]
            cond = interpret_weather_code(forecast_weather_codes[i])
            emoji = get_weather_emoji(forecast_weather_codes[i])
            max_t = forecast_max_temps[i]
            min_t = forecast_min_temps[i]
            self.forecast_labels[i].config(text=f"{emoji} {date}: {cond} | Max: {max_t}°C | Min: {min_t}°C")
        
        # Update packing guide
        packing_items = get_packing_guide(temperature, weather_code)
        self.packing_text.config(state=tk.NORMAL)
        self.packing_text.delete(1.0, tk.END)
        for item in packing_items:
            self.packing_text.insert(tk.END, f"• {item}\n")
        self.packing_text.config(state=tk.DISABLED)
        
        # Save to history
        save_weather_record(location_name, temperature, weather_condition)
        
    def view_history(self):
        """Open a pop-up window to view weather search history with colorful theme"""
        history_window = tk.Toplevel(self.root)
        history_window.title("📜 Weather Search History")
        history_window.geometry("700x500")
        history_window.resizable(True, True)
        
        # Create history canvas for gradient
        history_canvas = tk.Canvas(history_window, width=700, height=500, highlightthickness=0)
        history_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw gradient on history window
        h_rgb_start = hex_to_rgb(GRADIENT_START)
        h_rgb_mid = hex_to_rgb(GRADIENT_MID)
        h_rgb_end = hex_to_rgb(GRADIENT_END)
        create_gradient(history_canvas, 700, 500, h_rgb_start, h_rgb_mid, h_rgb_end)
        
        # Create history frame
        history_frame = ttk.Frame(history_canvas, padding="20")
        history_canvas.create_window(350, 250, window=history_frame, anchor="center")
        
        # History title
        history_title = ttk.Label(history_frame, text="Weather Search History", style="Title.TLabel")
        history_title.pack(pady=(0, 15))
        
        # Create Treeview for displaying records with colorful theme
        columns = ("timestamp", "location", "temperature", "condition")
        tree = ttk.Treeview(history_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        # Configure Treeview style for colorful theme
        self.style.configure("Custom.Treeview", background=TEXT_BG, foreground=FG_COLOR, fieldbackground=TEXT_BG, borderwidth=0)
        self.style.configure("Custom.Treeview.Heading", background=BUTTON_BG, foreground=FG_COLOR, font=("Arial", 10, "bold"), relief="flat")
        self.style.map("Custom.Treeview.Heading", background=[("active", "#7c3aed")])
        
        # Define column headings
        tree.heading("timestamp", text="Date & Time")
        tree.heading("location", text="Location")
        tree.heading("temperature", text="Temperature (°C)")
        tree.heading("condition", text="Weather Condition")
        
        # Define column widths
        tree.column("timestamp", width=150)
        tree.column("location", width=200)
        tree.column("temperature", width=120)
        tree.column("condition", width=200)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Retrieve and insert records
        records = get_all_weather_records()
        if not records:
            tree.insert("", tk.END, values=("No records found", "", "", ""))
        else:
            for record in records:
                tree.insert("", tk.END, values=record)


def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
