import socket
import threading
import json

MENU = {
    "1": {"name": "Paneer Butter Masala", "price": 220, "stock": 10},
    "2": {"name": "Veg Biryani", "price": 180, "stock": 10},
    "3": {"name": "Masala Dosa", "price": 90, "stock": 10},
    "4": {"name": "Lassi", "price": 50, "stock": 10},
    "5": {"name": "Chole Bhature", "price": 130, "stock": 10},
    "6": {"name": "Butter Naan", "price": 30, "stock": 10},
    "7": {"name": "Chicken Curry", "price": 260, "stock": 10},
    "8": {"name": "Fish Fry", "price": 280, "stock": 10},
    "9": {"name": "Pav Bhaji", "price": 100, "stock": 10},
    "10": {"name": "Samosa", "price": 25, "stock": 10},
    "11": {"name": "Cold Coffee", "price": 90, "stock": 10},
    "12": {"name": "French Fries", "price": 80, "stock": 10},
    "13": {"name": "Tandoori Roti", "price": 20, "stock": 10},
    "14": {"name": "Manchurian", "price": 150, "stock": 10},
    "15": {"name": "Momos", "price": 70, "stock": 10},
    "16": {"name": "Veg Pizza", "price": 250, "stock": 10},
    "17": {"name": "Chocolate Shake", "price": 110, "stock": 10},
    "18": {"name": "Ice Cream Sundae", "price": 120, "stock": 10},
    "19": {"name": "Caesar Salad", "price": 170, "stock": 10},
    "20": {"name": "Tomato Soup", "price": 60, "stock": 10}
}

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        try:
            data = conn.recv(1024).decode()
            if data == "GET_MENU":
                conn.send(json.dumps(MENU).encode())
            elif data.startswith("ORDER_ITEM:"):
                item_id = data.split(":")[1]
                if item_id in MENU:
                    if MENU[item_id]["stock"] > 0:
                        MENU[item_id]["stock"] -= 1
                        response = f"Order placed for '{MENU[item_id]['name']}'"
                    else:
                        response = "Sorry, this item is out of stock."
                else:
                    response = "Invalid item selected."
                conn.send(response.encode())
            else:
                conn.send("Invalid command".encode())
        except:
            break
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(5)
    print("[SERVER STARTED ON PORT 8888] Waiting for connections...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
