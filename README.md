# Real-Time Process Synchronization Analyzer

## Subject: Operating System (CSE316) Project  

### Project Overview
**Real-Time Process Synchronization Analyzer** is a tool designed to analyze and resolve process synchronization issues in multi-threaded applications. It provides a real-time visualization of active threads and their synchronization behavior, helping users identify performance bottlenecks and potential deadlocks.

### Features
- **Live Thread Monitoring**: Captures and displays real-time thread activity from running processes.
- **Graphical Visualization**: Uses Matplotlib to present a bar chart of the top processes by thread count.
- **Thread Log Tracking**: Provides a detailed log of active processes and their threads.
- **Manual and Automatic Refresh**: Allows users to manually refresh data or rely on automatic periodic updates.
- **User-Friendly Interface**: Built with Tkinter for a simple and interactive experience.
- **Efficient Resource Usage**: Designed to monitor system processes with minimal performance impact.

### Technologies Used
- **Python** (Main Programming Language)
- **Tkinter** (GUI Framework)
- **psutil** (Process Management)
- **Matplotlib** (Graphical Representation)

### Installation & Setup
#### Prerequisites
Make sure you have Python installed (>=3.8). Then, install the required dependencies:
```sh
pip install psutil matplotlib
```

#### Running the Application
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/RealTime-Sync-Analyzer.git
   ```
2. Navigate to the project directory:
   ```sh
   cd RealTime-Sync-Analyzer
   ```
3. Run the application:
   ```sh
   python live_thread.py
   ```

### Usage
- The left panel logs the active processes and their thread count in real time.
- The right panel displays a bar chart of the top 5 processes with the most threads.
- Click "Refresh Now" to manually update the data.
- Click "Exit" or close the window to stop monitoring.

### Contribution
Contributions are welcome! Feel free to fork the repository and submit pull requests.

### License
This project is licensed under the MIT License.

### Author
**Sanyam Jain**  
Operating System (CSE316) Project

