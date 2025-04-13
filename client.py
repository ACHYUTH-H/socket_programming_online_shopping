import socket
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json

# === Socket Connection ===
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.0.133", 8888))  # Replace with your server IP

# === Styling ===
BG_COLOR = "#ffffff"
CARD_COLOR = "#f8f9fa"
TEXT_COLOR = "#000000"
BUTTON_COLOR = "#000000"
BUTTON_TEXT = "#ffffff"
LOW_STOCK_COLOR = "#e67e22"
OUT_OF_STOCK_COLOR = "#e74c3c"
IN_STOCK_COLOR = "#2ecc71"
FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI", 18, "bold")

card_refs = []

# === Communication ===
def fetch_menu():
    client.send("GET_MENU".encode())
    return json.loads(client.recv(4096).decode())

def place_order(item_id):
    client.send(f"ORDER_ITEM:{item_id}".encode())
    response = client.recv(1024).decode()
    messagebox.showinfo("Order Status", response)
    refresh_menu()

# === Helpers ===
def get_stock_status(stock):
    if stock == 0:
        return "Out of Stock", OUT_OF_STOCK_COLOR
    elif stock <= 2:
        return f"Low Stock ({stock})", LOW_STOCK_COLOR
    else:
        return f"In Stock ({stock})", IN_STOCK_COLOR

def refresh_menu():
    for widget in menu_frame.winfo_children():
        widget.destroy()
    display_menu()

def display_menu():
    global card_refs
    card_refs.clear()
    menu = fetch_menu()
    for index, (key, item) in enumerate(menu.items()):
        frame = tk.Frame(menu_frame, bg=CARD_COLOR, bd=0, highlightbackground="#dddddd", highlightthickness=1)
        card_refs.append((frame, index))

        # Placeholder Image
        placeholder = Image.new("RGB", (100, 80), color="#cccccc")
        img = ImageTk.PhotoImage(placeholder)
        img_label = tk.Label(frame, image=img, bg=CARD_COLOR)
        img_label.image = img
        img_label.pack(pady=(10, 5))

        # Item Name
        title = tk.Label(frame, text=item["name"], font=("Segoe UI", 11, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
        title.pack()

        # Price
        price = tk.Label(frame, text=f"₹{item['price']}", font=FONT, bg=CARD_COLOR, fg="#666666")
        price.pack()

        # Stock
        status_text, status_color = get_stock_status(item["stock"])
        stock_label = tk.Label(frame, text=status_text, font=("Segoe UI", 9, "italic"), fg=status_color, bg=CARD_COLOR)
        stock_label.pack(pady=(0, 5))

        # Order Button
        btn_state = tk.NORMAL if item["stock"] > 0 else tk.DISABLED
        order_btn = tk.Button(
            frame,
            text="Order Now",
            font=("Segoe UI", 9, "bold"),
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT,
            activebackground="#222222",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=lambda k=key: place_order(k),
            state=btn_state
        )
        order_btn.pack(pady=(0, 10))

    arrange_cards()

def arrange_cards():
    for widget in menu_frame.winfo_children():
        widget.grid_forget()

    width = menu_frame.winfo_width()
    card_width = 220
    columns = max(width // card_width, 1)

    for idx, (frame, index) in enumerate(card_refs):
        row = index // columns
        col = index % columns
        frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

    for i in range(columns):
        menu_frame.grid_columnconfigure(i, weight=1)

# === GUI Setup ===
def create_gui():
    global menu_frame

    window = tk.Tk()
    window.title("🍽️ Modern Restaurant")
    window.geometry("720x620")
    window.configure(bg=BG_COLOR)

    title = tk.Label(window, text="Today's Specials", font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    title.pack(pady=15)

    # Scrollable Container Setup
    container = tk.Frame(window, bg=BG_COLOR)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)
    scrollable_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Update scroll region when content changes
    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", update_scroll_region)

    # Handle resizing
    def resize_canvas(event):
        canvas.itemconfig(scrollable_window, width=event.width)
        arrange_cards()

    canvas.bind("<Configure>", resize_canvas)

    # Enable mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    menu_frame = scrollable_frame
    display_menu()

    window.mainloop()

if __name__ == "__main__":
    create_gui()
