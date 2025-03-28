
# CPU Scheduler Simulator

## Overview
The CPU Scheduler Simulator is a Python-based simulation tool designed to implement and analyze various CPU scheduling algorithms. It allows users to add processes, configure scheduling policies, and visualize execution metrics through a structured scheduling engine.

## Features
- Supports multiple scheduling algorithms:
  - First-Come, First-Served (FCFS)**
  - Shortest Job First (SJF)**
  - Round Robin (RR)**
  - Priority Scheduling**
- Allows users to add processes dynamically with:
  - Process ID (PID)
  - Arrival Time
  - Burst Time
  - Priority (for priority scheduling)
- Configurable options:
  - Preemption** (for SJF & Priority Scheduling)
  - Quantum Time** (for Round Robin)
- Generates execution history including:
  - Schedule Timeline
  - Turnaround Time
  - Waiting Time
  - Response Time
- Provides a Gantt Chart and Metrics Table for process execution details.

## Installation
### Prerequisites
- Python 3.8 or later
- Required Python libraries:
  ```bash
  pip install matplotlib numpy
  ```

### Clone the Repository
```bash
git clone https://github.com/yourusername/cpu-scheduler-simulator.git
cd cpu-scheduler-simulator
```

## Usage
### Running the Simulator
```bash
python cpu-scheduler-simulator.py
```

### Example: Adding Processes and Running FCFS
```python
from scheduler_engine import SchedulerEngine

scheduler = SchedulerEngine()
scheduler.add_process(1, arrival_time=0, burst_time=5)
scheduler.add_process(2, arrival_time=2, burst_time=3)
scheduler.add_process(3, arrival_time=4, burst_time=2)

results = scheduler.fcfs()
print(results)
```

### Flowchart of Execution
```mermaid
graph TD;
    Start -->|User Input| Add_Process;
    Add_Process -->|Add Process (PID, Arrival, Burst, Priority)| Algorithm_Selection;
    Algorithm_Selection -->|Choose Algorithm (FCFS, SJF, RR, Priority)| Configuration;
    Configuration -->|Set Preemption (SJF/Priority) or Quantum (RR)| Run_Simulation;
    Run_Simulation -->|Scheduler Engine Executes Algorithm| Results_Generated;
    Results_Generated -->|Generate Schedule, Metrics, Process Details| Visualization;
    Visualization -->|Update Gantt Chart, Metrics, Process Table| End;
```

## Code Structure
```
📂 cpu-scheduler-simulator/
├── scheduler_engine.py  # Core scheduler logic
├── cpu-scheduler-simulator.py  # Main script
├── process.py  # Process class definition
├── requirements.txt  # Dependencies
└── README.md  # Project Documentation
```

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author
Developed by Ayush Kumar

