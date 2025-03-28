import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
from collections import deque
import random
import copy

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None
        self.execution_history = []

    def reset(self):
        self.remaining_time = self.burst_time
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None
        self.execution_history = []

    def __str__(self):
        return f"P{self.pid}"

class SchedulerEngine:
    def __init__(self):
        self.processes = []
        self.current_time = 0
        self.schedule = []
        self.completed_processes = []
        self.quantum = 2  # Default quantum for Round Robin

    def add_process(self, pid, arrival_time, burst_time, priority=0):
        self.processes.append(Process(pid, arrival_time, burst_time, priority))

    def reset(self):
        self.current_time = 0
        self.schedule = []
        self.completed_processes = []
        for process in self.processes:
            process.reset()

    def clear_all_processes(self):
        self.processes = []
        self.reset()

    def fcfs(self):
        self.reset()
        remaining_processes = sorted(copy.deepcopy(self.processes), key=lambda p: (p.arrival_time, p.pid))

        while remaining_processes:
            # Find the process that has arrived
            available_process = None
            for process in remaining_processes:
                if process.arrival_time <= self.current_time:
                    available_process = process
                    break

            if available_process:
                # If process is starting for the first time
                if available_process.start_time is None:
                    available_process.start_time = self.current_time
                    available_process.response_time = self.current_time - available_process.arrival_time

                # Execute the process
                time_slice = available_process.remaining_time
                available_process.execution_history.append((self.current_time, self.current_time + time_slice))
                self.schedule.append((str(available_process), self.current_time, self.current_time + time_slice))

                # Update times
                self.current_time += time_slice
                available_process.remaining_time = 0
                available_process.finish_time = self.current_time
                available_process.turnaround_time = available_process.finish_time - available_process.arrival_time
                available_process.waiting_time = available_process.turnaround_time - available_process.burst_time

                # Add to completed and remove from remaining
                self.completed_processes.append(available_process)
                remaining_processes.remove(available_process)
            else:
                # No process available, advance time to next arrival
                self.current_time = min(p.arrival_time for p in remaining_processes)

        return self.get_results()

    def sjf(self, preemptive=False):
        self.reset()
        remaining_processes = copy.deepcopy(self.processes)

        while remaining_processes:
            # Find processes that have arrived
            available_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]

            if available_processes:
                # Sort by remaining time
                available_processes.sort(key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
                current_process = available_processes[0]

                # If process is starting for the first time
                if current_process.start_time is None:
                    current_process.start_time = self.current_time
                    current_process.response_time = self.current_time - current_process.arrival_time

                # Determine how long to run
                if preemptive:
                    # Find next arrival time or completion time
                    next_event_time = float('inf')
                    for p in remaining_processes:
                        if p.arrival_time > self.current_time and p.arrival_time < next_event_time:
                            next_event_time = p.arrival_time

                    run_time = min(current_process.remaining_time, next_event_time - self.current_time)
                    if run_time == float('inf'):  # No future arrivals
                        run_time = current_process.remaining_time
                else:
                    run_time = current_process.remaining_time

                # Execute the process
                current_process.execution_history.append((self.current_time, self.current_time + run_time))
                self.schedule.append((str(current_process), self.current_time, self.current_time + run_time))
                self.current_time += run_time
                current_process.remaining_time -= run_time

                # Check if process is complete
                if current_process.remaining_time == 0:
                    current_process.finish_time = self.current_time
                    current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
                    current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                    self.completed_processes.append(current_process)

                    # Find corresponding process in remaining_processes
                    for i, p in enumerate(remaining_processes):
                        if p.pid == current_process.pid:
                            remaining_processes.pop(i)
                            break
            else:
                # No process available, advance time to next arrival
                self.current_time = min(p.arrival_time for p in remaining_processes)

        return self.get_results()

    def round_robin(self):
        self.reset()
        remaining_processes = copy.deepcopy(self.processes)
        ready_queue = deque()

        # Initial queue setup
        current_process = None

        while remaining_processes or ready_queue or current_process:
            # Check for new arrivals
            new_arrivals = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            for process in new_arrivals:
                ready_queue.append(process)
                remaining_processes.remove(process)

            # If no process is running, get one from the queue
            if current_process is None:
                if ready_queue:
                    current_process = ready_queue.popleft()
                    # If process is starting for the first time
                    if current_process.start_time is None:
                        current_process.start_time = self.current_time
                        current_process.response_time = self.current_time - current_process.arrival_time
                else:
                    # No process available, advance time to next arrival
                    if remaining_processes:
                        self.current_time = min(p.arrival_time for p in remaining_processes)
                        continue
                    else:
                        break  # No more processes to execute

            # Execute for quantum or remaining time
            run_time = min(self.quantum, current_process.remaining_time)
            current_process.execution_history.append((self.current_time, self.current_time + run_time))
            self.schedule.append((str(current_process), self.current_time, self.current_time + run_time))
            self.current_time += run_time
            current_process.remaining_time -= run_time

            # Check for new arrivals again after execution
            new_arrivals = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            for process in new_arrivals:
                ready_queue.append(process)
                remaining_processes.remove(process)

            # Process the current process
            if current_process.remaining_time == 0:
                # Process completed
                current_process.finish_time = self.current_time
                current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                self.completed_processes.append(current_process)
                current_process = None
            else:
                # Process needs more time, back to ready queue
                ready_queue.append(current_process)
                current_process = None

        return self.get_results()

    def priority_scheduling(self, preemptive=True):
        self.reset()
        remaining_processes = copy.deepcopy(self.processes)

        while remaining_processes:
            # Find processes that have arrived
            available_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]

            if available_processes:
                # Sort by priority (lower value = higher priority)
                available_processes.sort(key=lambda p: (p.priority, p.arrival_time, p.pid))
                current_process = available_processes[0]

                # If process is starting for the first time
                if current_process.start_time is None:
                    current_process.start_time = self.current_time
                    current_process.response_time = self.current_time - current_process.arrival_time

                # Determine how long to run
                if preemptive:
                    # Find next arrival time
                    next_event_time = float('inf')
                    for p in remaining_processes:
                        if p.arrival_time > self.current_time and p.arrival_time < next_event_time:
                            next_event_time = p.arrival_time

                    run_time = min(current_process.remaining_time, next_event_time - self.current_time)
                    if run_time == float('inf'):  # No future arrivals
                        run_time = current_process.remaining_time
                else:
                    run_time = current_process.remaining_time

                # Execute the process
                current_process.execution_history.append((self.current_time, self.current_time + run_time))
                self.schedule.append((str(current_process), self.current_time, self.current_time + run_time))
                self.current_time += run_time
                current_process.remaining_time -= run_time

                # Check if process is complete
                if current_process.remaining_time == 0:
                    current_process.finish_time = self.current_time
                    current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
                    current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                    self.completed_processes.append(current_process)

                    # Find corresponding process in remaining_processes
                    for i, p in enumerate(remaining_processes):
                        if p.pid == current_process.pid:
                            remaining_processes.pop(i)
                            break
            else:
                # No process available, advance time to next arrival
                self.current_time = min(p.arrival_time for p in remaining_processes)

        return self.get_results()

    def get_results(self):
        # Sort by PID for consistent display
        self.completed_processes.sort(key=lambda p: p.pid)

        avg_waiting_time = np.mean([p.waiting_time for p in self.completed_processes]) if self.completed_processes else 0
        avg_turnaround_time = np.mean([p.turnaround_time for p in self.completed_processes]) if self.completed_processes else 0
        avg_response_time = np.mean([p.response_time for p in self.completed_processes]) if self.completed_processes else 0

        return {
            'schedule': self.schedule,
            'processes': self.completed_processes,
            'avg_waiting_time': avg_waiting_time,
            'avg_turnaround_time': avg_turnaround_time,
            'avg_response_time': avg_response_time
        }

class CPUSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        self.root.geometry("1200x800")
        self.root.config(bg="#f5f5f5")

        self.scheduler = SchedulerEngine()
        self.results = {}
        self.algorithm_var = tk.StringVar(value="FCFS")
        self.preemptive_var = tk.BooleanVar(value=False)
        self.quantum_var = tk.IntVar(value=2)

        self.create_widgets()
        self.setup_demo_processes()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel (inputs)
        left_frame = ttk.LabelFrame(main_frame, text="Process Management", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        # Process inputs
        process_frame = ttk.Frame(left_frame)
        process_frame.pack(fill=tk.X, pady=5)

        ttk.Label(process_frame, text="Process ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.pid_var = tk.StringVar()
        ttk.Entry(process_frame, textvariable=self.pid_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(process_frame, text="Arrival Time:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.arrival_var = tk.IntVar()
        ttk.Entry(process_frame, textvariable=self.arrival_var, width=10).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(process_frame, text="Burst Time:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.burst_var = tk.IntVar()
        ttk.Entry(process_frame, textvariable=self.burst_var, width=10).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(process_frame, text="Priority:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.priority_var = tk.IntVar()
        ttk.Entry(process_frame, textvariable=self.priority_var, width=10).grid(row=3, column=1, padx=5, pady=2)

        # Buttons for process management
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Add Process", command=self.add_process).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_processes).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="Load Demo", command=self.setup_demo_processes).grid(row=0, column=2, padx=5, pady=5)

        # Process table
        self.process_tree = ttk.Treeview(left_frame, columns=("PID", "Arrival", "Burst", "Priority"), show="headings", height=10)
        self.process_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Arrival", text="Arrival Time")
        self.process_tree.heading("Burst", text="Burst Time")
        self.process_tree.heading("Priority", text="Priority")

        self.process_tree.column("PID", width=50)
        self.process_tree.column("Arrival", width=80)
        self.process_tree.column("Burst", width=80)
        self.process_tree.column("Priority", width=80)

        # Algorithm selection
        algo_frame = ttk.LabelFrame(left_frame, text="Algorithm Selection", padding=10)
        algo_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(algo_frame, text="First-Come, First-Served (FCFS)", variable=self.algorithm_var, value="FCFS").pack(anchor=tk.W)
        ttk.Radiobutton(algo_frame, text="Shortest Job First (SJF)", variable=self.algorithm_var, value="SJF").pack(anchor=tk.W)

        sjf_preemp_frame = ttk.Frame(algo_frame)
        sjf_preemp_frame.pack(fill=tk.X, pady=2)
        self.sjf_preemptive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(sjf_preemp_frame, text="Preemptive (SRTF)", variable=self.sjf_preemptive_var).pack(side=tk.LEFT, padx=20)

        ttk.Radiobutton(algo_frame, text="Round Robin (RR)", variable=self.algorithm_var, value="RR").pack(anchor=tk.W)

        rr_frame = ttk.Frame(algo_frame)
        rr_frame.pack(fill=tk.X, pady=2)
        ttk.Label(rr_frame, text="Time Quantum:").pack(side=tk.LEFT, padx=20)
        ttk.Spinbox(rr_frame, from_=1, to=10, textvariable=self.quantum_var, width=5).pack(side=tk.LEFT)

        ttk.Radiobutton(algo_frame, text="Priority Scheduling", variable=self.algorithm_var, value="Priority").pack(anchor=tk.W)

        prio_preemp_frame = ttk.Frame(algo_frame)
        prio_preemp_frame.pack(fill=tk.X, pady=2)
        self.priority_preemptive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(prio_preemp_frame, text="Preemptive", variable=self.priority_preemptive_var).pack(side=tk.LEFT, padx=20)

        # Run simulation button
        ttk.Button(left_frame, text="Run Simulation", command=self.run_simulation, style="Accent.TButton").pack(fill=tk.X, pady=10)

        # Right panel (results)
        right_frame = ttk.LabelFrame(main_frame, text="Simulation Results", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Gantt chart
        gantt_frame = ttk.LabelFrame(right_frame, text="Gantt Chart", padding=10)
        gantt_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=gantt_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Metrics
        metrics_frame = ttk.LabelFrame(right_frame, text="Performance Metrics", padding=10)
        metrics_frame.pack(fill=tk.X, pady=5)

        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, wrap=tk.WORD, height=8)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)

        # Process details
        details_frame = ttk.LabelFrame(right_frame, text="Process Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.details_tree = ttk.Treeview(details_frame,
                                         columns=("PID", "Start", "Finish", "Turnaround", "Waiting", "Response"),
                                         show="headings", height=6)
        self.details_tree.pack(fill=tk.BOTH, expand=True)

        self.details_tree.heading("PID", text="PID")
        self.details_tree.heading("Start", text="Start Time")
        self.details_tree.heading("Finish", text="Finish Time")
        self.details_tree.heading("Turnaround", text="Turnaround")
        self.details_tree.heading("Waiting", text="Waiting")
        self.details_tree.heading("Response", text="Response")

        self.details_tree.column("PID", width=50)
        self.details_tree.column("Start", width=70)
        self.details_tree.column("Finish", width=70)
        self.details_tree.column("Turnaround", width=70)
        self.details_tree.column("Waiting", width=70)
        self.details_tree.column("Response", width=70)

        # Apply styles
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Helvetica", 10, "bold"))

    def add_process(self):
        try:
            pid = self.pid_var.get()
            arrival = self.arrival_var.get()
            burst = self.burst_var.get()
            priority = self.priority_var.get()

            if not pid or burst <= 0:
                messagebox.showerror("Error", "Process ID must not be empty and Burst Time must be positive")
                return

            self.scheduler.add_process(pid, arrival, burst, priority)

            # Add to treeview
            self.process_tree.insert("", "end", values=(pid, arrival, burst, priority))

            # Clear inputs
            self.pid_var.set("")
            self.arrival_var.set(0)
            self.burst_var.set(0)
            self.priority_var.set(0)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add process: {str(e)}")

    def clear_processes(self):
        self.scheduler.clear_all_processes()

        # Clear treeviews
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        for item in self.details_tree.get_children():
            self.details_tree.delete(item)

        # Clear Gantt chart
        self.ax.clear()
        self.canvas.draw()

        # Clear metrics
        self.metrics_text.delete(1.0, tk.END)

    def setup_demo_processes(self):
        self.clear_processes()

        # Demo processes
        demo_processes = [
            ("P1", 0, 8, 3),
            ("P2", 1, 4, 1),
            ("P3", 2, 9, 4),
            ("P4", 3, 5, 2)
        ]

        for pid, arrival, burst, priority in demo_processes:
            self.scheduler.add_process(pid, arrival, burst, priority)
            self.process_tree.insert("", "end", values=(pid, arrival, burst, priority))

    def run_simulation(self):
        # Clear previous results
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)

        # Get selected algorithm
        algorithm = self.algorithm_var.get()
        self.scheduler.quantum = self.quantum_var.get()

        # Run simulation
        if algorithm == "FCFS":
            self.results = self.scheduler.fcfs()
        elif algorithm == "SJF":
            self.results = self.scheduler.sjf(preemptive=self.sjf_preemptive_var.get())
        elif algorithm == "RR":
            self.results = self.scheduler.round_robin()
        elif algorithm == "Priority":
            self.results = self.scheduler.priority_scheduling(preemptive=self.priority_preemptive_var.get())

        # Update Gantt chart
        self.update_gantt_chart()

        # Update metrics
        self.update_metrics()

        # Update process details
        self.update_process_details()

    def update_gantt_chart(self):
        self.ax.clear()

        schedule = self.results['schedule']
        if not schedule:
            return

        # Colors for processes
        colors = plt.cm.tab10.colors
        pid_colors = {}

        # Assign colors to unique PIDs
        unique_pids = set(pid for pid, _, _ in schedule)
        for i, pid in enumerate(unique_pids):
            pid_colors[pid] = colors[i % len(colors)]

        # Plot Gantt chart
        y_pos = 0
        for pid, start, end in schedule:
            self.ax.broken_barh([(start, end - start)], (y_pos, 0.8),
                                facecolors=pid_colors[pid], edgecolor='black', alpha=0.7)

            # Add process label
            self.ax.text(start + (end - start) / 2, y_pos + 0.4, pid,
                         ha='center', va='center', color='black', fontweight='bold')

        # Set labels and grid
        self.ax.set_yticks([])
        self.ax.set_xlabel('Time', fontsize=10)

        # Set x-axis limits
        max_time = max(end for _, _, end in schedule)
        self.ax.set_xlim(0, max_time)

        # Add grid
        self.ax.grid(True, axis='x', linestyle='--', alpha=0.7)

        # Add time markers with improved spacing and smaller font
        x_ticks = list(range(0, int(max_time) + 1))
        self.ax.set_xticks(x_ticks)

        # Set smaller font size for x-axis tick labels and increase spacing
        self.ax.tick_params(axis='x', labelsize=8, pad=2)

        # Improve spacing between tick labels by rotating them slightly if needed
        if max_time > 15:  # If we have many time units, rotate labels for better spacing
            plt.setp(self.ax.get_xticklabels(), rotation=30, ha='right')

        # Adjust bottom margin to ensure labels are visible
        self.fig.subplots_adjust(bottom=0.2)

        self.canvas.draw()

    def update_metrics(self):
        avg_waiting = self.results.get('avg_waiting_time', 0)
        avg_turnaround = self.results.get('avg_turnaround_time', 0)
        avg_response = self.results.get('avg_response_time', 0)

        algorithm = self.algorithm_var.get()
        algo_details = algorithm

        if algorithm == "SJF" and self.sjf_preemptive_var.get():
            algo_details += " (Preemptive/SRTF)"
        elif algorithm == "SJF":
            algo_details += " (Non-preemptive)"
        elif algorithm == "RR":
            algo_details += f" (Quantum={self.quantum_var.get()})"
        elif algorithm == "Priority" and self.priority_preemptive_var.get():
            algo_details += " (Preemptive)"
        elif algorithm == "Priority":
            algo_details += " (Non-preemptive)"

        metrics_text = (
            f"Algorithm: {algo_details}\n\n"
            f"Average Waiting Time: {avg_waiting:.2f} time units\n"
            f"Average Turnaround Time: {avg_turnaround:.2f} time units\n"
            f"Average Response Time: {avg_response:.2f} time units\n"
            f"Total Execution Time: {self.scheduler.current_time} time units\n"
        )

        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, metrics_text)

    def update_process_details(self):
        processes = self.results.get('processes', [])

        for p in processes:
            self.details_tree.insert("", "end", values=(
                p.pid,
                p.start_time,
                p.finish_time,
                p.turnaround_time,
                p.waiting_time,
                p.response_time
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerApp(root)
    root.mainloop()
