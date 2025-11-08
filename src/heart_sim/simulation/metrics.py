"""
Metrics Collector

Calculates performance metrics from simulation results.
"""

import numpy as np
from typing import Dict


class MetricsCollector:
    """
    Collects and calculates performance metrics from simulation data.

    Metrics categories:
    - Power metrics (peak, average, percentiles)
    - Coordination metrics (delays, collisions avoided, phase spread)
    - Efficiency metrics (comparing baseline vs cardiac)
    """

    @staticmethod
    def calculate_power_metrics(history: Dict) -> Dict:
        """
        Calculate power-related metrics.

        Args:
            history: Simulation history dictionary

        Returns:
            Dictionary of power metrics
        """
        aggregate = np.array(history['aggregate_power'])
        time_array = np.array(history['time'])

        if len(aggregate) == 0:
            return {'error': 'No data'}

        # Basic power statistics
        peak_power = float(np.max(aggregate))
        peak_time = float(time_array[np.argmax(aggregate)])
        avg_power = float(np.mean(aggregate))
        min_power = float(np.min(aggregate))

        # Percentiles
        p90 = float(np.percentile(aggregate, 90))
        p95 = float(np.percentile(aggregate, 95))
        p99 = float(np.percentile(aggregate, 99))

        # Standard deviation and coefficient of variation
        std_power = float(np.std(aggregate))
        cv_power = std_power / avg_power if avg_power > 0 else 0

        # Energy calculation (kWh)
        # Integrate power over time, convert from kW·s to kWh
        total_energy_kwh = float(np.trapz(aggregate, time_array) / 3600.0)

        return {
            'peak_power_kw': peak_power,
            'peak_time_sec': peak_time,
            'avg_power_kw': avg_power,
            'min_power_kw': min_power,
            'std_power_kw': std_power,
            'cv_power': cv_power,
            'p90_power_kw': p90,
            'p95_power_kw': p95,
            'p99_power_kw': p99,
            'total_energy_kwh': total_energy_kwh,
        }

    @staticmethod
    def calculate_coordination_metrics(results: Dict) -> Dict:
        """
        Calculate coordination-related metrics.

        Args:
            results: Complete simulation results

        Returns:
            Dictionary of coordination metrics
        """
        final_stats = results['final_press_stats']
        history = results['history']

        # Total coordination activity
        total_delays = sum(stats['delay_count'] for stats in final_stats.values())
        total_cycles = sum(stats['cycle_count'] for stats in final_stats.values())
        total_collisions_avoided = sum(stats['collisions_avoided']
                                       for stats in final_stats.values())
        total_delay_time = sum(stats['total_delay_added']
                              for stats in final_stats.values())

        # Average collision risk over time
        avg_collision_risk = np.mean([
            np.mean(history['collision_risks'][press_id])
            for press_id in history['collision_risks'].keys()
        ])

        # Phase spread (measure of desynchronization)
        final_phases = [stats['final_phase'] for stats in final_stats.values()]
        phase_variance = float(np.var(final_phases))

        # Calculate average phase separation
        n = len(final_phases)
        if n > 1:
            sorted_phases = sorted(final_phases)
            phase_gaps = []
            for i in range(n):
                gap = sorted_phases[(i + 1) % n] - sorted_phases[i]
                if gap < 0:
                    gap += 1.0  # Handle wraparound
                phase_gaps.append(gap)

            avg_phase_gap = np.mean(phase_gaps)
            ideal_gap = 1.0 / n
            # Score: 1.0 = perfect spacing, 0.0 = bad spacing
            phase_spread_score = 1.0 - abs(avg_phase_gap - ideal_gap) / ideal_gap
        else:
            avg_phase_gap = 0.0
            phase_spread_score = 1.0

        return {
            'total_delays': total_delays,
            'total_cycles': total_cycles,
            'total_collisions_avoided': total_collisions_avoided,
            'total_delay_time_sec': total_delay_time,
            'avg_collision_risk': float(avg_collision_risk),
            'phase_variance': phase_variance,
            'avg_phase_gap': avg_phase_gap,
            'phase_spread_score': float(phase_spread_score),
            'delay_rate': total_delays / total_cycles if total_cycles > 0 else 0,
        }

    @staticmethod
    def calculate_all_metrics(results: Dict) -> Dict:
        """
        Calculate all metrics from simulation results.

        Args:
            results: Complete simulation results from SimulationEngine

        Returns:
            Dictionary with all calculated metrics
        """
        power_metrics = MetricsCollector.calculate_power_metrics(results['history'])
        coord_metrics = MetricsCollector.calculate_coordination_metrics(results)

        return {
            **power_metrics,
            **coord_metrics,
        }

    @staticmethod
    def compare_baseline_vs_cardiac(baseline_results: Dict, cardiac_results: Dict) -> Dict:
        """
        Compare baseline (no coordination) vs cardiac coordination results.

        Args:
            baseline_results: Results from baseline simulation
            cardiac_results: Results from cardiac coordination simulation

        Returns:
            Dictionary with comparison metrics
        """
        baseline_metrics = MetricsCollector.calculate_all_metrics(baseline_results)
        cardiac_metrics = MetricsCollector.calculate_all_metrics(cardiac_results)

        # Peak reduction
        baseline_peak = baseline_metrics['peak_power_kw']
        cardiac_peak = cardiac_metrics['peak_power_kw']
        peak_reduction_kw = baseline_peak - cardiac_peak
        peak_reduction_pct = (peak_reduction_kw / baseline_peak * 100
                             if baseline_peak > 0 else 0)

        # Average power change
        baseline_avg = baseline_metrics['avg_power_kw']
        cardiac_avg = cardiac_metrics['avg_power_kw']
        avg_change_kw = baseline_avg - cardiac_avg
        avg_change_pct = (avg_change_kw / baseline_avg * 100
                         if baseline_avg > 0 else 0)

        # Energy change
        baseline_energy = baseline_metrics['total_energy_kwh']
        cardiac_energy = cardiac_metrics['total_energy_kwh']
        energy_change_kwh = baseline_energy - cardiac_energy
        energy_change_pct = (energy_change_kwh / baseline_energy * 100
                            if baseline_energy > 0 else 0)

        # Variability change (CV = coefficient of variation)
        baseline_cv = baseline_metrics['cv_power']
        cardiac_cv = cardiac_metrics['cv_power']
        cv_change = baseline_cv - cardiac_cv
        cv_change_pct = (cv_change / baseline_cv * 100
                        if baseline_cv > 0 else 0)

        return {
            'baseline_peak_kw': baseline_peak,
            'cardiac_peak_kw': cardiac_peak,
            'peak_reduction_kw': peak_reduction_kw,
            'peak_reduction_pct': peak_reduction_pct,

            'baseline_avg_kw': baseline_avg,
            'cardiac_avg_kw': cardiac_avg,
            'avg_change_kw': avg_change_kw,
            'avg_change_pct': avg_change_pct,

            'baseline_energy_kwh': baseline_energy,
            'cardiac_energy_kwh': cardiac_energy,
            'energy_change_kwh': energy_change_kwh,
            'energy_change_pct': energy_change_pct,

            'baseline_cv': baseline_cv,
            'cardiac_cv': cardiac_cv,
            'cv_change': cv_change,
            'cv_reduction_pct': cv_change_pct,

            # Cardiac-specific metrics
            'cardiac_delays': cardiac_metrics['total_delays'],
            'cardiac_collisions_avoided': cardiac_metrics['total_collisions_avoided'],
            'cardiac_phase_spread': cardiac_metrics['phase_spread_score'],
        }

    @staticmethod
    def calculate_ai_features(results: Dict) -> Dict:
        """
        Calculate features useful for AI/ML training.

        Args:
            results: Complete simulation results

        Returns:
            Dictionary of AI-ready features
        """
        history = results['history']
        metadata = results['metadata']
        final_stats = results['final_press_stats']

        # Power features
        aggregate = np.array(history['aggregate_power'])
        peak_frequency = np.sum(aggregate > 0.9 * np.max(aggregate)) / len(aggregate)

        # Phase coherence (how synchronized are the presses?)
        phases_over_time = np.array([history['phases'][press_id]
                                     for press_id in history['phases'].keys()])
        phase_std_over_time = np.std(phases_over_time, axis=0)
        avg_phase_std = float(np.mean(phase_std_over_time))

        # Collision density (collisions per unit time)
        total_collisions_avoided = sum(stats['collisions_avoided']
                                       for stats in final_stats.values())
        collision_density = total_collisions_avoided / metadata['duration_sec']

        # Delay efficiency (how much delay per collision avoided)
        total_delay_time = sum(stats['total_delay_added']
                              for stats in final_stats.values())
        delay_per_collision = (total_delay_time / total_collisions_avoided
                              if total_collisions_avoided > 0 else 0)

        # Network activity
        num_presses = metadata['num_presses']
        avg_cycles_per_press = sum(stats['cycle_count']
                                   for stats in final_stats.values()) / num_presses

        return {
            'peak_frequency': float(peak_frequency),
            'avg_phase_std': avg_phase_std,
            'collision_density': float(collision_density),
            'delay_per_collision_avoided': float(delay_per_collision),
            'avg_cycles_per_press': float(avg_cycles_per_press),
            'coordination_efficiency': (total_collisions_avoided /
                                       (total_delay_time + 1e-6)),  # Avoid div by zero
        }
