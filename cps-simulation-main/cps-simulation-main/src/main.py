"""
Main execution script for Traffic Light CPS Simulation
Runs all scenarios and generates complete analysis
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from traffic_light_system import IntersectionSimulator, Direction
from visualizer import TrafficVisualizer
import time
import json


def run_normal_operation(duration: int = 100):
    """Run simulation under normal conditions"""
    print("\n" + "="*60)
    print("SCENARIO 1: Normal Operation")
    print("="*60)
    
    sim = IntersectionSimulator(use_tolerance=False)
    results = sim.run_simulation(duration=duration)
    
    print(f"  Average Wait Time: {results['avg_wait_time']:.2f} seconds")
    print(f"  Throughput: {results['throughput']:.2f} vehicles/min")
    print(f"  Total Vehicles Processed: {results['total_vehicles']}")
    
    return results, sim


def run_false_data_attack(duration: int = 100):
    """Run simulation with false sensor data attack"""
    print("\n" + "="*60)
    print("SCENARIO 2: False Sensor Data Attack")
    print("="*60)
    print("  Attack: Injecting 3x phantom vehicles in North direction")
    
    sim = IntersectionSimulator(use_tolerance=False)
    
    # Launch attack on North sensors after 10 steps
    for step in range(duration):
        if step == 10:
            sim.launch_attack('false_data', direction=Direction.NORTH, multiplier=3.0)
            print(f"  [Time {step}] Attack launched!")
        sim.step()
    
    # Calculate metrics
    avg_wait = sim.metrics['total_wait_time'] / max(1, sim.metrics['total_vehicles_processed'])
    throughput = sim.metrics['total_vehicles_processed'] / (duration / 60)
    
    results = {
        'avg_wait_time': avg_wait,
        'throughput': throughput,
        'total_vehicles': sim.metrics['total_vehicles_processed'],
        'cycle_count': sim.metrics['cycle_count']
    }
    
    print(f"  Average Wait Time: {results['avg_wait_time']:.2f} seconds")
    print(f"  Throughput: {results['throughput']:.2f} vehicles/min")
    print(f"  Total Vehicles Processed: {results['total_vehicles']}")
    
    return results, sim


def run_delay_attack(duration: int = 100):
    """Run simulation with communication delay attack"""
    print("\n" + "="*60)
    print("SCENARIO 3: Communication Delay Attack")
    print("="*60)
    print("  Attack: 10-second communication delay")
    
    sim = IntersectionSimulator(use_tolerance=False)
    
    # Launch delay attack
    for step in range(duration):
        if step == 10:
            sim.launch_attack('delay', delay=10.0)
            print(f"  [Time {step}] Delay attack launched!")
        sim.step()
    
    avg_wait = sim.metrics['total_wait_time'] / max(1, sim.metrics['total_vehicles_processed'])
    throughput = sim.metrics['total_vehicles_processed'] / (duration / 60)
    
    results = {
        'avg_wait_time': avg_wait,
        'throughput': throughput,
        'total_vehicles': sim.metrics['total_vehicles_processed'],
        'cycle_count': sim.metrics['cycle_count']
    }
    
    print(f"  Average Wait Time: {results['avg_wait_time']:.2f} seconds")
    print(f"  Throughput: {results['throughput']:.2f} vehicles/min")
    print(f"  Total Vehicles Processed: {results['total_vehicles']}")
    
    return results, sim


def run_with_tolerance(duration: int = 100):
    """Run simulation with tolerance mechanisms enabled under attack"""
    print("\n" + "="*60)
    print("SCENARIO 4: False Data Attack WITH Tolerance Mechanisms")
    print("="*60)
    print("  Tolerance: Redundancy + Threshold Validation + Anomaly Detection")
    
    sim = IntersectionSimulator(use_tolerance=True)
    
    # Launch same attack as scenario 2
    for step in range(duration):
        if step == 10:
            sim.launch_attack('false_data', direction=Direction.NORTH, multiplier=3.0)
            print(f"  [Time {step}] Attack launched (tolerance active)!")
        sim.step()
    
    avg_wait = sim.metrics['total_wait_time'] / max(1, sim.metrics['total_vehicles_processed'])
    throughput = sim.metrics['total_vehicles_processed'] / (duration / 60)
    
    results = {
        'avg_wait_time': avg_wait,
        'throughput': throughput,
        'total_vehicles': sim.metrics['total_vehicles_processed'],
        'cycle_count': sim.metrics['cycle_count']
    }
    
    print(f"  Average Wait Time: {results['avg_wait_time']:.2f} seconds")
    print(f"  Throughput: {results['throughput']:.2f} vehicles/min")
    print(f"  Total Vehicles Processed: {results['total_vehicles']}")
    
    return results, sim


def main():
    """Main execution function"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "TRAFFIC LIGHT CPS SIMULATION" + " "*15 + "║")
    print("║" + " "*10 + "Cyberattack & Tolerance Analysis" + " "*11 + "║")
    print("╚" + "="*58 + "╝")
    
    # Set simulation duration
    DURATION = 100  # 100 time steps (seconds)
    
    # Run all scenarios
    print("\nRunning simulations...")
    
    normal_results, normal_sim = run_normal_operation(DURATION)
    false_data_results, false_data_sim = run_false_data_attack(DURATION)
    delay_results, delay_sim = run_delay_attack(DURATION)
    tolerance_results, tolerance_sim = run_with_tolerance(DURATION)
    
    # Compile all results
    all_results = {
        'Normal Operation': normal_results,
        'False Data Attack': false_data_results,
        'Delay Attack': delay_results,
        'With Tolerance': tolerance_results
    }
    
    # Create visualizations
    print("\n" + "="*60)
    print("Generating Visualizations...")
    print("="*60)
    
    viz = TrafficVisualizer()  # Will use default paths
    
    
    # 1. Performance comparison
    print("\n[1/5] Creating performance comparison chart...")
    viz.plot_performance_comparison(all_results)
    
    # 2. Attack comparison
    print("[2/5] Creating attack impact analysis...")
    attack_results = {
        'Normal': normal_results,
        'False Data': false_data_results,
        'Delay': delay_results,
        'Tolerance Active': tolerance_results
    }
    viz.plot_attack_comparison(attack_results)
    
    # 3. Tolerance effectiveness
    print("[3/5] Creating tolerance effectiveness analysis...")
    viz.plot_tolerance_effectiveness(false_data_results, tolerance_results)
    
    # 4. Traffic light timeline
    print("[4/5] Creating traffic light timeline...")
    light_histories = {
        'NORTH': normal_sim.lights[Direction.NORTH].state_history,
        'SOUTH': normal_sim.lights[Direction.SOUTH].state_history,
        'EAST': normal_sim.lights[Direction.EAST].state_history,
        'WEST': normal_sim.lights[Direction.WEST].state_history
    }
    viz.plot_traffic_light_timeline(light_histories, duration=DURATION)
    
    # 5. Summary data
    print("[5/5] Creating summary data table...")
    summary_df = viz.create_summary_report_data(all_results)
    
    # Save detailed results to JSON
    print("\nSaving detailed results...")
    data_dir = Path(__file__).parent.parent / "data"
    results_path = data_dir / "detailed_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved: {results_path}")
    
    # Print summary table
    print("\n" + "="*60)
    print("SIMULATION SUMMARY")
    print("="*60)
    print(summary_df.to_string(index=False))
    
    # Calculate improvements
    print("\n" + "="*60)
    print("TOLERANCE MECHANISM EFFECTIVENESS")
    print("="*60)
    
    wait_improvement = ((false_data_results['avg_wait_time'] - tolerance_results['avg_wait_time']) / 
                       false_data_results['avg_wait_time'] * 100)
    throughput_improvement = ((tolerance_results['throughput'] - false_data_results['throughput']) / 
                             false_data_results['throughput'] * 100)
    
    print(f"  Wait Time Reduction: {wait_improvement:.1f}%")
    print(f"  Throughput Improvement: {throughput_improvement:.1f}%")
    
    print("\n" + "="*60)
    print("All simulations complete!")
    outputs_path = Path(__file__).parent.parent / "outputs"
    data_path = Path(__file__).parent.parent / "data"
    print(f"Output graphs saved to: {outputs_path.resolve()}")
    print(f"Data files saved to: {data_path.resolve()}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
