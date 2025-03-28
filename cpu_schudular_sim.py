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