# Cyber-Physical System Simulation Project

## Project Overview
This project simulates a Cyber-Physical System with cyberattack scenarios and tolerance mechanisms.

## Project Structure
```
cps-simulation/
├── src/                 # Source code for simulation
├── reports/             # Assignment report and documentation
├── outputs/             # Graphs, screenshots, and results
├── data/                # Data files and logs
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## System Options
1. Smart traffic light system
2. Temperature control system
3. Smart water tank system

## Objectives
- Simulate normal operation of the chosen CPS
- Introduce cyberattack scenarios (false sensor data, delays, control signal manipulation)
- Implement tolerance mechanisms (redundancy, threshold validation, fallback logic)
- Compare system performance before and after applying tolerance mechanisms

## Deliverables
- Assignment report (8-10 pages)
- Simulation model files
- Output graphs/screenshots
- Conclusion and future scope

## Getting Started
1. Create virtual environment: `python -m venv venv`
2. Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Run simulation: `python src/main.py`
