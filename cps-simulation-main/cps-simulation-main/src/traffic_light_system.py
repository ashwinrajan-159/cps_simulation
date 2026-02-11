"""
Smart Traffic Light System - Core Components
A cyber-physical system simulation for a 4-way traffic intersection.
"""

import random
import time
from enum import Enum
from typing import List, Dict, Tuple
from dataclasses import dataclass


class LightState(Enum):
    """Traffic light states"""
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class Direction(Enum):
    """Traffic directions"""
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"


@dataclass
class SensorReading:
    """Data structure for sensor readings"""
    direction: Direction
    vehicle_count: int
    timestamp: float
    sensor_id: int
    is_compromised: bool = False


class TrafficSensor:
    """Simulates vehicle detection sensors at intersection"""
    
    def __init__(self, direction: Direction, sensor_id: int):
        self.direction = direction
        self.sensor_id = sensor_id
        self.is_compromised = False
        self.false_data_multiplier = 1.0
        
    def detect_vehicles(self, actual_traffic: int) -> SensorReading:
        """
        Detect vehicles in the lane
        
        Args:
            actual_traffic: Actual number of vehicles present
            
        Returns:
            SensorReading object with detection data
        """
        if self.is_compromised:
            # Apply attack - inject false data
            reported_count = int(actual_traffic * self.false_data_multiplier)
        else:
            # Normal operation with minor sensor noise
            reported_count = actual_traffic + random.randint(-1, 1)
            reported_count = max(0, reported_count)  # Cannot be negative
        
        return SensorReading(
            direction=self.direction,
            vehicle_count=reported_count,
            timestamp=time.time(),
            sensor_id=self.sensor_id,
            is_compromised=self.is_compromised
        )
    
    def inject_false_data(self, multiplier: float = 3.0):
        """
        Cyberattack: Inject false sensor data
        
        Args:
            multiplier: Multiplier for vehicle count (e.g., 3.0 = report 3x vehicles)
        """
        self.is_compromised = True
        self.false_data_multiplier = multiplier
    
    def reset(self):
        """Reset sensor to normal operation"""
        self.is_compromised = False
        self.false_data_multiplier = 1.0


class TrafficLight:
    """Represents a traffic light for one direction"""
    
    def __init__(self, direction: Direction):
        self.direction = direction
        self.state = LightState.RED
        self.time_in_state = 0.0
        self.state_history = []
        
    def set_state(self, new_state: LightState, timestamp: float):
        """Change light state"""
        if new_state != self.state:
            self.state_history.append({
                'from': self.state.value,
                'to': new_state.value,
                'timestamp': timestamp,
                'duration': self.time_in_state
            })
            self.state = new_state
            self.time_in_state = 0.0
    
    def update_time(self, delta_time: float):
        """Update time spent in current state"""
        self.time_in_state += delta_time
    
    def get_state(self) -> LightState:
        """Get current state"""
        return self.state


class TrafficController:
    """
    Main controller that processes sensor data and manages light timing
    """
    
    def __init__(self, use_tolerance: bool = False):
        self.use_tolerance = use_tolerance
        self.communication_delay = 0.0  # Simulated network delay
        self.signal_override = None  # For control signal manipulation attack
        
        # Tolerance mechanism parameters
        self.threshold_max_vehicles = 20  # Physical lane capacity
        self.anomaly_threshold_sigma = 3.0  # Standard deviations for anomaly detection
        self.sensor_history: Dict[Direction, List[int]] = {d: [] for d in Direction}
        
    def process_sensor_data(self, sensor_readings: List[SensorReading]) -> Dict[Direction, int]:
        """
        Process sensor data with optional tolerance mechanisms
        
        Args:
            sensor_readings: List of sensor readings from all sensors
            
        Returns:
            Dict mapping direction to validated vehicle count
        """
        # Group readings by direction
        readings_by_direction: Dict[Direction, List[SensorReading]] = {d: [] for d in Direction}
        for reading in sensor_readings:
            readings_by_direction[reading.direction].append(reading)
        
        validated_data = {}
        
        for direction, readings in readings_by_direction.items():
            if not readings:
                validated_data[direction] = 0
                continue
            
            if self.use_tolerance:
                # Apply tolerance mechanisms
                validated_count = self._apply_tolerance_checks(direction, readings)
            else:
                # No tolerance - just average the readings
                validated_count = int(sum(r.vehicle_count for r in readings) / len(readings))
            
            validated_data[direction] = validated_count
            
            # Update history for anomaly detection
            self.sensor_history[direction].append(validated_count)
            if len(self.sensor_history[direction]) > 100:
                self.sensor_history[direction].pop(0)
        
        return validated_data
    
    def _apply_tolerance_checks(self, direction: Direction, readings: List[SensorReading]) -> int:
        """
        Apply tolerance mechanisms to validate sensor data
        
        Mechanisms:
        1. Threshold validation - reject impossible values
        2. Redundancy with majority voting
        3. Anomaly detection using statistical baseline
        """
        # Filter out readings exceeding physical threshold
        valid_readings = [r for r in readings if r.vehicle_count <= self.threshold_max_vehicles]
        
        if not valid_readings:
            # All readings invalid - use fallback
            return self._get_fallback_value(direction)
        
        # Majority voting with redundant sensors
        if len(valid_readings) >= 3:
            # Use median for robustness
            counts = sorted([r.vehicle_count for r in valid_readings])
            validated_count = counts[len(counts) // 2]
        else:
            # Not enough sensors - take average
            validated_count = int(sum(r.vehicle_count for r in valid_readings) / len(valid_readings))
        
        # Anomaly detection
        if len(self.sensor_history[direction]) >= 10:
            history = self.sensor_history[direction]
            mean = sum(history) / len(history)
            variance = sum((x - mean) ** 2 for x in history) / len(history)
            std_dev = variance ** 0.5
            
            # Check if current reading is anomalous
            if abs(validated_count - mean) > self.anomaly_threshold_sigma * std_dev:
                # Anomaly detected - use historical mean as fallback
                return int(mean)
        
        return validated_count
    
    def _get_fallback_value(self, direction: Direction) -> int:
        """Get fallback value when all sensors fail"""
        if self.sensor_history[direction]:
            # Use historical average
            return int(sum(self.sensor_history[direction]) / len(self.sensor_history[direction]))
        else:
            # Default to moderate traffic
            return 5
    
    def calculate_light_timing(self, traffic_data: Dict[Direction, int]) -> Dict[str, int]:
        """
        Calculate optimal light timing based on traffic
        
        Args:
            traffic_data: Validated vehicle counts per direction
            
        Returns:
            Dict with 'ns_green' and 'ew_green' durations in seconds
        """
        # Check for signal override attack
        if self.signal_override:
            return self.signal_override
        
        # Group by phase
        ns_traffic = traffic_data.get(Direction.NORTH, 0) + traffic_data.get(Direction.SOUTH, 0)
        ew_traffic = traffic_data.get(Direction.EAST, 0) + traffic_data.get(Direction.WEST, 0)
        
        total_traffic = ns_traffic + ew_traffic
        
        if total_traffic == 0:
            # No traffic - use minimum timing
            return {'ns_green': 30, 'ew_green': 30, 'yellow': 5}
        
        # Proportional allocation with min/max bounds
        total_green_time = 90  # Total green time to distribute
        ns_ratio = ns_traffic / total_traffic
        
        ns_green = int(total_green_time * ns_ratio)
        ns_green = max(30, min(60, ns_green))  # Bound between 30-60 seconds
        
        ew_green = total_green_time - ns_green
        ew_green = max(30, min(60, ew_green))
        
        return {'ns_green': ns_green, 'ew_green': ew_green, 'yellow': 5}
    
    def inject_communication_delay(self, delay_seconds: float):
        """Cyberattack: Add communication delay"""
        self.communication_delay = delay_seconds
    
    def inject_signal_override(self, override_timing: Dict[str, int]):
        """Cyberattack: Override control signals"""
        self.signal_override = override_timing
    
    def reset_attacks(self):
        """Reset all attacks"""
        self.communication_delay = 0.0
        self.signal_override = None
    
    def enable_tolerance(self):
        """Enable tolerance mechanisms"""
        self.use_tolerance = True
    
    def disable_tolerance(self):
        """Disable tolerance mechanisms"""
        self.use_tolerance = False


class IntersectionSimulator:
    """
    Orchestrates the entire traffic light system simulation
    """
    
    def __init__(self, use_tolerance: bool = False):
        # Create sensors (3 per direction for redundancy)
        self.sensors: Dict[Direction, List[TrafficSensor]] = {}
        for direction in Direction:
            self.sensors[direction] = [
                TrafficSensor(direction, i) for i in range(3)
            ]
        
        # Create traffic lights
        self.lights: Dict[Direction, TrafficLight] = {
            direction: TrafficLight(direction) for direction in Direction
        }
        
        # Create controller
        self.controller = TrafficController(use_tolerance=use_tolerance)
        
        # Traffic state
        self.actual_traffic: Dict[Direction, int] = {d: 0 for d in Direction}
        self.current_time = 0.0
        self.current_phase = "NS"  # NS or EW
        self.phase_start_time = 0.0
        self.phase_duration = 30
        
        # Performance metrics
        self.metrics = {
            'total_vehicles_processed': 0,
            'total_wait_time': 0,
            'cycle_count': 0,
            'attacks_detected': 0
        }
        
    def generate_traffic(self):
        """Generate random traffic using Poisson distribution"""
        for direction in Direction:
            # Poisson with lambda = 5 (average 5 vehicles per time step)
            arrival_rate = 5
            new_vehicles = random.choices(
                range(0, 15), 
                weights=[((arrival_rate ** k) * (2.71828 ** -arrival_rate) / self._factorial(k)) 
                        for k in range(15)]
            )[0]
            self.actual_traffic[direction] = min(20, self.actual_traffic[direction] + new_vehicles)
    
    def _factorial(self, n: int) -> int:
        """Calculate factorial"""
        if n <= 1:
            return 1
        return n * self._factorial(n - 1)
    
    def collect_sensor_data(self) -> List[SensorReading]:
        """Collect data from all sensors"""
        readings = []
        for direction in Direction:
            for sensor in self.sensors[direction]:
                reading = sensor.detect_vehicles(self.actual_traffic[direction])
                readings.append(reading)
        return readings
    
    def update_lights(self, timing: Dict[str, int]):
        """Update traffic light states based on timing"""
        if self.current_phase == "NS":
            # North-South green, East-West red
            self.lights[Direction.NORTH].set_state(LightState.GREEN, self.current_time)
            self.lights[Direction.SOUTH].set_state(LightState.GREEN, self.current_time)
            self.lights[Direction.EAST].set_state(LightState.RED, self.current_time)
            self.lights[Direction.WEST].set_state(LightState.RED, self.current_time)
        else:
            # East-West green, North-South red
            self.lights[Direction.NORTH].set_state(LightState.RED, self.current_time)
            self.lights[Direction.SOUTH].set_state(LightState.RED, self.current_time)
            self.lights[Direction.EAST].set_state(LightState.GREEN, self.current_time)
            self.lights[Direction.WEST].set_state(LightState.GREEN, self.current_time)
    
    def process_vehicles(self):
        """Process vehicles through intersection"""
        for direction, light in self.lights.items():
            if light.get_state() == LightState.GREEN:
                # Vehicles can pass - process 5 vehicles per second
                vehicles_cleared = min(5, self.actual_traffic[direction])
                self.actual_traffic[direction] -= vehicles_cleared
                self.metrics['total_vehicles_processed'] += vehicles_cleared
            else:
                # Vehicles waiting - accumulate wait time
                self.metrics['total_wait_time'] += self.actual_traffic[direction]
    
    def step(self, delta_time: float = 1.0):
        """
        Execute one simulation step
        
        Args:
            delta_time: Time step in seconds
        """
        self.current_time += delta_time
        
        # Generate new traffic
        self.generate_traffic()
        
        # Collect sensor data
        sensor_readings = self.collect_sensor_data()
        
        # Process data through controller
        validated_data = self.controller.process_sensor_data(sensor_readings)
        
        # Calculate timing
        timing = self.controller.calculate_light_timing(validated_data)
        
        # Check if phase should change
        time_in_phase = self.current_time - self.phase_start_time
        
        if time_in_phase >= self.phase_duration:
            # Switch phase
            self.current_phase = "EW" if self.current_phase == "NS" else "NS"
            self.phase_start_time = self.current_time
            
            # Set new duration
            if self.current_phase == "NS":
                self.phase_duration = timing['ns_green'] + timing['yellow']
            else:
                self.phase_duration = timing['ew_green'] + timing['yellow']
            
            self.metrics['cycle_count'] += 0.5  # Half cycle per phase change
        
        # Update lights
        self.update_lights(timing)
        
        # Process vehicles
        self.process_vehicles()
        
        # Update light timers
        for light in self.lights.values():
            light.update_time(delta_time)
    
    def run_simulation(self, duration: int = 100) -> Dict:
        """
        Run simulation for specified duration
        
        Args:
            duration: Number of time steps to simulate
            
        Returns:
            Performance metrics dictionary
        """
        for _ in range(duration):
            self.step()
        
        # Calculate final metrics
        avg_wait_time = (self.metrics['total_wait_time'] / 
                        max(1, self.metrics['total_vehicles_processed']))
        throughput = self.metrics['total_vehicles_processed'] / (duration / 60)  # vehicles per minute
        
        return {
            'avg_wait_time': avg_wait_time,
            'throughput': throughput,
            'total_vehicles': self.metrics['total_vehicles_processed'],
            'cycle_count': self.metrics['cycle_count']
        }
    
    def launch_attack(self, attack_type: str, **kwargs):
        """
        Launch a cyberattack on the system
        
        Args:
            attack_type: Type of attack ('false_data', 'delay', 'override')
            **kwargs: Attack-specific parameters
        """
        if attack_type == 'false_data':
            multiplier = kwargs.get('multiplier', 3.0)
            target_direction = kwargs.get('direction', Direction.NORTH)
            for sensor in self.sensors[target_direction]:
                sensor.inject_false_data(multiplier)
        
        elif attack_type == 'delay':
            delay = kwargs.get('delay', 10.0)
            self.controller.inject_communication_delay(delay)
        
        elif attack_type == 'override':
            # Override to dangerous state (all green or all red)
            override_type = kwargs.get('override_type', 'all_green')
            if override_type == 'all_green':
                self.controller.inject_signal_override({'ns_green': 1, 'ew_green': 1, 'yellow': 0})
            else:
                self.controller.inject_signal_override({'ns_green': 0, 'ew_green': 0, 'yellow': 0})
