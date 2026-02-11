"""
Visualization Module for Traffic Light System
Generates graphs and plots for performance analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict


class TrafficVisualizer:
    """Handles all visualization and plotting for the simulation"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            # Get absolute path relative to this script
            script_dir = Path(__file__).parent
            output_dir = script_dir.parent / "outputs"
        else:
            output_dir = Path(output_dir)
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 11
    
    def plot_performance_comparison(self, results: Dict[str, Dict], save_name: str = "performance_comparison.png"):
        """
        Compare performance metrics across scenarios
        
        Args:
            results: Dict with scenario names as keys and metrics as values
            save_name: Output filename
        """
        scenarios = list(results.keys())
        metrics = ['avg_wait_time', 'throughput', 'total_vehicles']
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Traffic Light System Performance Comparison', fontsize=16, fontweight='bold')
        
        # Average Wait Time
        wait_times = [results[s]['avg_wait_time'] for s in scenarios]
        axes[0].bar(scenarios, wait_times, color=['#2ecc71', '#e74c3c', '#3498db'])
        axes[0].set_ylabel('Average Wait Time (seconds)')
        axes[0].set_title('Vehicle Wait Time')
        axes[0].tick_params(axis='x', rotation=15)
        
        # Throughput
        throughputs = [results[s]['throughput'] for s in scenarios]
        axes[1].bar(scenarios, throughputs, color=['#2ecc71', '#e74c3c', '#3498db'])
        axes[1].set_ylabel('Vehicles per Minute')
        axes[1].set_title('System Throughput')
        axes[1].tick_params(axis='x', rotation=15)
        
        # Total Vehicles Processed
        totals = [results[s]['total_vehicles'] for s in scenarios]
        axes[2].bar(scenarios, totals, color=['#2ecc71', '#e74c3c', '#3498db'])
        axes[2].set_ylabel('Total Vehicles')
        axes[2].set_title('Total Vehicles Processed')
        axes[2].tick_params(axis='x', rotation=15)
        
        plt.tight_layout()
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
    
    def plot_wait_time_distribution(self, data: Dict[str, List[float]], save_name: str = "wait_time_distribution.png"):
        """
        Plot distribution of wait times for different scenarios
        
        Args:
            data: Dict mapping scenario names to list of wait times
            save_name: Output filename
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for scenario, wait_times in data.items():
            ax.hist(wait_times, bins=30, alpha=0.6, label=scenario)
        
        ax.set_xlabel('Wait Time (seconds)')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Vehicle Wait Times', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
    
    def plot_traffic_light_timeline(self, light_histories: Dict, duration: int = 100, 
                                   save_name: str = "light_timeline.png"):
        """
        Visualize traffic light state changes over time
        
        Args:
            light_histories: Dict mapping direction to state history
            duration: Simulation duration
            save_name: Output filename
        """
        fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
        directions = ['NORTH', 'SOUTH', 'EAST', 'WEST']
        colors = {'RED': '#e74c3c', 'YELLOW': '#f39c12', 'GREEN': '#2ecc71'}
        
        for idx, direction in enumerate(directions):
            ax = axes[idx]
            
            if direction in light_histories and light_histories[direction]:
                history = light_histories[direction]
                
                # Plot state blocks
                current_time = 0
                for event in history:
                    state = event['to']
                    next_time = event.get('timestamp', current_time + event.get('duration', 0))
                    
                    ax.barh(0, next_time - current_time, left=current_time, 
                           height=0.8, color=colors.get(state, '#95a5a6'),
                           edgecolor='black', linewidth=0.5)
                    current_time = next_time
            
            ax.set_ylabel(direction.capitalize(), fontweight='bold')
            ax.set_ylim(-0.5, 0.5)
            ax.set_yticks([])
            ax.grid(True, alpha=0.3, axis='x')
        
        axes[-1].set_xlabel('Time (seconds)')
        axes[0].set_title('Traffic Light State Timeline', fontsize=14, fontweight='bold')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=colors['GREEN'], label='Green'),
                          Patch(facecolor=colors['YELLOW'], label='Yellow'),
                          Patch(facecolor=colors['RED'], label='Red')]
        axes[0].legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
    
    def plot_sensor_data_comparison(self, actual_data: Dict, reported_data: Dict,
                                   save_name: str = "sensor_accuracy.png"):
        """
        Compare actual vs reported sensor data to visualize attacks
        
        Args:
            actual_data: Dict mapping time to actual vehicle counts
            reported_data: Dict mapping time to reported counts
            save_name: Output filename
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        times = sorted(actual_data.keys())
        actual_values = [actual_data[t] for t in times]
        reported_values = [reported_data[t] for t in times]
        
        ax.plot(times, actual_values, label='Actual Traffic', color='#2ecc71', 
               linewidth=2, marker='o', markersize=4)
        ax.plot(times, reported_values, label='Reported Traffic', color='#e74c3c',
               linewidth=2, marker='s', markersize=4, linestyle='--')
        
        ax.fill_between(times, actual_values, reported_values, alpha=0.2, color='#95a5a6')
        
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Vehicle Count')
        ax.set_title('Sensor Data: Actual vs Reported (Attack Visualization)', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
    
    def plot_tolerance_effectiveness(self, attack_results: Dict, tolerance_results: Dict,
                                    save_name: str = "tolerance_effectiveness.png"):
        """
        Show effectiveness of tolerance mechanisms
        
        Args:
            attack_results: Metrics under attack without tolerance
            tolerance_results: Metrics under attack with tolerance
            save_name: Output filename
        """
        metrics = ['avg_wait_time', 'throughput']
        metric_labels = ['Avg Wait Time (s)', 'Throughput (vehicles/min)']
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Tolerance Mechanism Effectiveness', fontsize=16, fontweight='bold')
        
        for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
            attack_value = attack_results.get(metric, 0)
            tolerance_value = tolerance_results.get(metric, 0)
            
            bars = axes[idx].bar(['Under Attack\n(No Tolerance)', 'Under Attack\n(With Tolerance)'],
                                [attack_value, tolerance_value],
                                color=['#e74c3c', '#3498db'])
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                axes[idx].text(bar.get_x() + bar.get_width()/2., height,
                             f'{height:.1f}',
                             ha='center', va='bottom', fontweight='bold')
            
            axes[idx].set_ylabel(label)
            axes[idx].set_title(label.split('(')[0].strip())
            axes[idx].grid(True, alpha=0.3, axis='y')
            
            # Add improvement percentage
            if metric == 'avg_wait_time' and attack_value > 0:
                improvement = ((attack_value - tolerance_value) / attack_value) * 100
                axes[idx].text(0.5, max(attack_value, tolerance_value) * 0.9,
                             f'{improvement:.1f}% improvement',
                             ha='center', fontsize=10, style='italic',
                             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            elif metric == 'throughput' and tolerance_value > 0:
                improvement = ((tolerance_value - attack_value) / attack_value) * 100
                axes[idx].text(0.5, max(attack_value, tolerance_value) * 0.9,
                             f'{improvement:.1f}% improvement',
                             ha='center', fontsize=10, style='italic',
                             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
    
    def plot_attack_comparison(self, results: Dict[str, Dict], save_name: str = "attack_comparison.png"):
        """
        Compare different attack scenarios
        
        Args:
            results: Dict mapping attack types to performance metrics
            save_name: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Cyberattack Impact Analysis', fontsize=16, fontweight='bold')
        
        attack_types = list(results.keys())
        
        # Wait Time
        wait_times = [results[a]['avg_wait_time'] for a in attack_types]
        axes[0, 0].barh(attack_types, wait_times, color=['#95a5a6', '#e74c3c', '#e67e22', '#9b59b6'])
        axes[0, 0].set_xlabel('Average Wait Time (seconds)')
        axes[0, 0].set_title('Impact on Wait Time')
        axes[0, 0].grid(True, alpha=0.3, axis='x')
        
        # Throughput
        throughputs = [results[a]['throughput'] for a in attack_types]
        axes[0, 1].barh(attack_types, throughputs, color=['#95a5a6', '#e74c3c', '#e67e22', '#9b59b6'])
        axes[0, 1].set_xlabel('Throughput (vehicles/min)')
        axes[0, 1].set_title('Impact on Throughput')
        axes[0, 1].grid(True, alpha=0.3, axis='x')
        
        # Total Vehicles
        totals = [results[a]['total_vehicles'] for a in attack_types]
        axes[1, 0].barh(attack_types, totals, color=['#95a5a6', '#e74c3c', '#e67e22', '#9b59b6'])
        axes[1, 0].set_xlabel('Total Vehicles Processed')
        axes[1, 0].set_title('Processing Efficiency')
        axes[1, 0].grid(True, alpha=0.3, axis='x')
        
        # Severity Score (normalized combination)
        # Higher wait time = worse, lower throughput = worse
        baseline_wait = results[attack_types[0]]['avg_wait_time']
        baseline_throughput = results[attack_types[0]]['throughput']
        
        severity_scores = []
        for attack in attack_types:
            wait_impact = (results[attack]['avg_wait_time'] - baseline_wait) / max(baseline_wait, 1)
            throughput_impact = (baseline_throughput - results[attack]['throughput']) / max(baseline_throughput, 1)
            severity = (wait_impact + throughput_impact) * 50  # Scale to percentage
            severity_scores.append(max(0, severity))
        
        bars = axes[1, 1].barh(attack_types, severity_scores, 
                              color=['#95a5a6', '#e74c3c', '#e67e22', '#9b59b6'])
        axes[1, 1].set_xlabel('Severity Score (%)')
        axes[1, 1].set_title('Overall Attack Severity')
        axes[1, 1].grid(True, alpha=0.3, axis='x')
        
        # Color code by severity
        for i, bar in enumerate(bars):
            if severity_scores[i] > 50:
                bar.set_color('#c0392b')  # Dark red for high severity
            elif severity_scores[i] > 25:
                bar.set_color('#e74c3c')  # Red for medium severity
            elif severity_scores[i] > 10:
                bar.set_color('#f39c12')  # Orange for low severity
            else:
                bar.set_color('#95a5a6')  # Gray for minimal impact
        
        plt.tight_layout()
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
    
    def create_summary_report_data(self, all_results: Dict) -> pd.DataFrame:
        """
        Create a summary DataFrame for the report
        
        Args:
            all_results: Dict with all simulation results
            
        Returns:
            pandas DataFrame with formatted results
        """
        data = []
        for scenario, metrics in all_results.items():
            data.append({
                'Scenario': scenario,
                'Avg Wait Time (s)': f"{metrics['avg_wait_time']:.2f}",
                'Throughput (veh/min)': f"{metrics['throughput']:.2f}",
                'Total Vehicles': metrics['total_vehicles'],
                'Cycles': f"{metrics.get('cycle_count', 0):.1f}"
            })
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        csv_path = self.output_dir.parent / 'data' / 'simulation_results.csv'
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"Saved: {csv_path}")
        
        return df
