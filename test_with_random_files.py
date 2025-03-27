import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
import time
import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os

# --- Log Simulator Class ---
class LogSimulator(threading.Thread):
    """
    This thread simulates log generation.
    In a real application, you'd replace this with a function reading from a log file or endpoint.
    """
    def __init__(self, text_widget, status_callback):
        super().__init__()
        self.text_widget = text_widget
        self.running = True
        self.paused = False
        self.log_count = 0
        self.status_callback = status_callback
        self.daemon = True  # Ensure the thread exits when the main program exits

    def run(self):
        while self.running:
            if not self.paused:
                log_entry = f"{time.strftime('%H:%M:%S')} - Thread {random.randint(1,5)} acquired lock on MutexA\n"
                self.text_widget.insert(tk.END, log_entry)
                self.text_widget.see(tk.END)
                self.log_count += 1
                self.status_callback(self.log_count)
            time.sleep(random.uniform(0.5, 1.5))

    def stop(self):
        self.running = False

    def toggle_pause(self):
        self.paused = not self.paused

# --- Graph Updater Class ---
class GraphUpdater:
    """
    This class manages a simulated wait-for graph.
    For demonstration, it randomly generates a directed graph.
    """
    def __init__(self, canvas_frame):
        self.canvas_frame = canvas_frame
        self.figure, self.ax = plt.subplots(figsize=(4, 3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.graph = nx.DiGraph()
        self.generate_random_graph()

    def generate_random_graph(self):
        # Create a random directed graph with 5 nodes and some edges
        self.graph.clear()
        nodes = [f"T{i}" for i in range(1, 6)]
        self.graph.add_nodes_from(nodes)
        for _ in range(random.randint(3, 7)):
            src = random.choice(nodes)
            dst = random.choice(nodes)
            if src != dst:
                self.graph.add_edge(src, dst)
        print("New graph edges:", list(self.graph.edges()))  # Debug print
        self.draw_graph()

    def draw_graph(self):
        self.ax.clear()
        pos = nx.spring_layout(self.graph)
        nx.draw_networkx(self.graph, pos, ax=self.ax, node_color='lightblue', 
                         arrows=True, with_labels=True, arrowstyle='->', arrowsize=10)
        self.ax.set_title("Simulated Wait-For Graph")
        self.canvas.draw()

    def refresh(self):
        self.generate_random_graph()

    def save_snapshot(self):
        # Ask for a file location and save the current figure as an image
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if file_path:
            self.figure.savefig(file_path)
            messagebox.showinfo("Snapshot Saved", f"Graph snapshot saved as {file_path}")

# --- Main Application ---
class SynchronizationAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Process Synchronization Analyzer")
        self.create_widgets()
        self.log_simulator = LogSimulator(self.log_text, self.update_status)
        self.log_simulator.start()

        # Set up graph updater in its own frame
        self.graph_updater = GraphUpdater(self.graph_frame)
        self.update_status(0)

    def create_widgets(self):
        # Create main frames for layout
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Left frame for logs
        self.log_frame = tk.LabelFrame(self.top_frame, text="Log Messages", padx=5, pady=5)
        self.log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right frame for graph
        self.graph_frame = tk.LabelFrame(self.top_frame, text="Wait-For Graph", padx=5, pady=5)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrolled text widget for logs
        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=50, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Controls frame with buttons
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.pause_button = tk.Button(self.controls_frame, text="Pause/Resume Logs", command=self.toggle_logs)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.restart_button = tk.Button(self.controls_frame, text="Restart Logs", command=self.restart_logs)
        self.restart_button.pack(side=tk.LEFT, padx=5)

        self.refresh_graph_button = tk.Button(self.controls_frame, text="Refresh Graph", command=self.refresh_graph)
        self.refresh_graph_button.pack(side=tk.LEFT, padx=5)

        self.save_snapshot_button = tk.Button(self.controls_frame, text="Save Graph Snapshot", command=self.save_snapshot)
        self.save_snapshot_button.pack(side=tk.LEFT, padx=5)

        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.bottom_frame, textvariable=self.status_var, anchor="w")
        self.status_bar.pack(fill=tk.X)

    def toggle_logs(self):
        self.log_simulator.toggle_pause()

    def restart_logs(self):
        # Stop and join the current log simulator thread with a timeout
        self.log_simulator.stop()
        self.log_simulator.join(timeout=2)
        # Clear the log area if needed
        self.log_text.delete('1.0', tk.END)
        # Start a new log simulator thread
        self.log_simulator = LogSimulator(self.log_text, self.update_status)
        self.log_simulator.start()

    def refresh_graph(self):
        self.graph_updater.refresh()

    def save_snapshot(self):
        self.graph_updater.save_snapshot()

    def update_status(self, log_count):
        # Update status bar with number of logs processed
        status_text = f"Total Log Messages: {log_count}"
        self.status_var.set(status_text)

    def on_close(self):
        # Called when the window's close button is pressed.
        print("Closing application...")
        self.log_simulator.stop()         # Signal thread to stop
        self.log_simulator.join(timeout=2)  # Wait for thread to finish
        self.root.destroy()               # Destroy the main window
        
        # Force exit if necessary. Use os._exit(0) if sys.exit(0) doesn't work.
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SynchronizationAnalyzerApp(root)
    # Bind the on_close() function to the window's close event
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
