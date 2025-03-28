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
