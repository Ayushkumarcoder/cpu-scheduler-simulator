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