import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import psutil  # pip install psutil if needed
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys, os

class ThreadMonitor(threading.Thread):
    """
    This thread periodically gathers system-wide thread information using psutil.
    It updates a log text widget and a callback for graph updates.
    """
    def __init__(self, log_widget, update_graph_callback, refresh_interval=5):
        super().__init__()
        self.log_widget = log_widget
        self.update_graph_callback = update_graph_callback
        self.refresh_interval = refresh_interval
        self.running = True
        self.daemon = True  # Ensures thread exits with main process

    def run(self):
        print("ThreadMonitor started.")
        while self.running:
            process_info = []  # list of tuples: (process_name, thread_count)
            log_lines = []
            # Limit to top 50 processes to reduce CPU load
            processes = list(psutil.process_iter(['pid', 'name']))[:50]
            for proc in processes:
                try:
                    name = proc.info['name'] or "Unknown"
                    pid = proc.info['pid']
                    threads = proc.threads()  # list of thread info objects
                    thread_count = len(threads)
                    process_info.append((f"{name} (PID: {pid})", thread_count))
                    log_lines.append(f"{time.strftime('%H:%M:%S')} - {name} (PID: {pid}) has {thread_count} thread(s).")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Update the log widget with the current snapshot
            self.log_widget.delete('1.0', tk.END)
            for line in log_lines:
                self.log_widget.insert(tk.END, line + "\n")
            self.log_widget.see(tk.END)

            # Update the graph using the callback
            self.update_graph_callback(process_info)

            time.sleep(self.refresh_interval)
        print("ThreadMonitor stopped.")

    def stop(self):
        self.running = False

class ThreadMonitorApp:
    def __init__(self, root):
        print("Starting ThreadMonitorApp...")
        self.root = root
        self.root.title("Live System Thread Monitor")
        self.create_widgets()
        self.thread_monitor = ThreadMonitor(self.log_text, self.update_graph, refresh_interval=5)
        self.thread_monitor.start()

    def create_widgets(self):
        # Main frames for layout
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Left frame: Log messages
        self.log_frame = tk.LabelFrame(self.top_frame, text="Live Thread Log", padx=5, pady=5)
        self.log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=50, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Right frame: Graph
        self.graph_frame = tk.LabelFrame(self.top_frame, text="Top Processes by Thread Count", padx=5, pady=5)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Controls frame: Buttons
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.refresh_button = tk.Button(self.controls_frame, text="Refresh Now", command=self.manual_refresh)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        self.exit_button = tk.Button(self.controls_frame, text="Exit", command=self.on_close)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.bottom_frame, textvariable=self.status_var, anchor="w")
        self.status_bar.pack(fill=tk.X)

    def update_graph(self, process_info):
        # Sort processes by thread count descending and select top 5
        sorted_info = sorted(process_info, key=lambda x: x[1], reverse=True)[:5]
        names = [info[0] for info in sorted_info]
        counts = [info[1] for info in sorted_info]

        self.ax.clear()
        self.ax.barh(names, counts, color='skyblue')
        self.ax.set_xlabel("Thread Count")
        self.ax.set_title("Top 5 Processes by Thread Count")
        self.ax.invert_yaxis()  # Highest count at top
        self.canvas.draw()

        total_processes = len(process_info)
        self.status_var.set(f"Total Processes Monitored: {total_processes}")

    def manual_refresh(self):
        try:
            process_info = []
            processes = list(psutil.process_iter(['pid', 'name']))[:50]
            for proc in processes:
                try:
                    name = proc.info['name'] or "Unknown"
                    pid = proc.info['pid']
                    thread_count = len(proc.threads())
                    process_info.append((f"{name} (PID: {pid})", thread_count))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            self.update_graph(process_info)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_close(self):
        print("Closing application...")
        self.thread_monitor.stop()
        self.thread_monitor.join(timeout=2)
        self.root.destroy()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == "__main__":
    print("Starting application...")
    root = tk.Tk()
    app = ThreadMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
    print("Application ended.")
