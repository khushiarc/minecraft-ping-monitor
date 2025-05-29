import tkinter as tk
from ping3 import ping
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import socket

packet_count = 0
timeout_count = 0

# Minecraft server list
minecraft_servers = {
    "Hypixel": "play.hypixel.net",
    "CubeCraft": "play.cubecraft.net",
    "Mineplex": "us.mineplex.com",
    "Purple Prison": "purpleprison.net",
    "Herobrine": "herobrine.org"
}

ping_times = []
TARGET_IP = "209.222.115.21"

# GUI setup
root = tk.Tk()
root.title("Minecraft Ping Monitor")
root.geometry("750x520")

selected_server = tk.StringVar(root)
selected_server.set("Hypixel")

dropdown = tk.OptionMenu(root, selected_server, *minecraft_servers.keys())
dropdown.pack(pady=10)

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# After canvas packing
stats_label = tk.Label(root, text="Average Ping: N/A ms | Packet Loss: N/A%", font=("Arial", 12))
stats_label.pack(pady=5)

legend_frame = tk.Frame(root)
legend_frame.pack(pady=5)

# Color boxes for legend
def create_legend_box(color, text):
    frame = tk.Frame(legend_frame)
    box = tk.Canvas(frame, width=20, height=20)
    box.create_rectangle(0, 0, 20, 20, fill=color)
    box.pack(side=tk.LEFT)
    label = tk.Label(frame, text=text)
    label.pack(side=tk.LEFT, padx=5)
    frame.pack(side=tk.LEFT, padx=10)

create_legend_box("green", "Good (< 100 ms)")
create_legend_box("orange", "Playable (100-250 ms)")
create_legend_box("red", "High Latency (> 250 ms)")
create_legend_box("gray", "Timeout / Packet Loss")

# Graph update
def update_plot():
    ax.clear()
    ax.set_title(f"Pings to {selected_server.get()} ({TARGET_IP})")
    ax.set_ylabel("Latency (ms)")
    ax.set_xlabel("Ping Count")

    display_pings = []
    colors = []

    # Filter out None values for average calculation
    valid_pings = [p for p in ping_times if p is not None]

    for ping_val in ping_times:
        if ping_val is None:
            display_pings.append(0)
            colors.append('gray')
        elif ping_val <= 100:
            display_pings.append(ping_val)
            colors.append('green')
        elif ping_val <= 250:
            display_pings.append(ping_val)
            colors.append('orange')
        else:
            display_pings.append(ping_val)
            colors.append('red')

    ax.bar(range(len(display_pings)), display_pings, color=colors)
    ax.set_ylim(0, max(display_pings + [300]))  # adjust Y scale
    ax.grid(True)
    canvas.draw()

    # Calculate average ping and packet loss
    avg_ping = round(sum(valid_pings) / len(valid_pings), 2) if valid_pings else 0
    packet_loss = round((ping_times.count(None) / len(ping_times)) * 100, 2) if ping_times else 0

    stats_label.config(text=f"Average Ping: {avg_ping} ms | Packet Loss: {packet_loss}%")

def ping_loop():
    global ping_times, packet_count, timeout_count
    while True:
        if TARGET_IP:
            latency = ping(TARGET_IP, timeout=1)
            packet_count += 1
            if latency is not None:
                ms = round(latency * 1000, 2)
                ping_times.append(ms)
            else:
                timeout_count += 1
                ping_times.append(None)  # timeout

            if len(ping_times) > 50:
                ping_times.pop(0)

            update_plot()
        time.sleep(1)

def resolve_and_start():
    global TARGET_IP
    domain = minecraft_servers[selected_server.get()]
    try:
        TARGET_IP = socket.gethostbyname(domain)
        ping_times.clear()
    except Exception as e:
        print(f"Failed to resolve {domain}: {e}")

start_button = tk.Button(root, text="Start Monitoring", command=resolve_and_start)
start_button.pack(pady=5)

# Start ping thread
thread = threading.Thread(target=ping_loop, daemon=True)
thread.start()

root.mainloop()
