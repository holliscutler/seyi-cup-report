"""
Taiwan Electricity Pricing Calculator

Based on Taiwan Power Company (Taipower) industrial rates.
All values from research documentation.

Sources:
- research/DAY1_RESEARCH_SUMMARY.md (Part 3: Taiwan Electricity Pricing)
- research/QUICK_REFERENCE.md (Energy Consumption Patterns)
"""

import numpy as np
from typing import Dict, Optional
from ..utils.constants import TAIWAN_RATES, TOU_HOURS, DEMAND_CHARGE_RATE_NTD, AVG_TOU_MULTIPLIER


class TaiwanCostCalculator:
    """
    Calculator for Taiwan industrial electricity costs.

    Based on Taipower 2025 rates:
    - Base rate: NT$4.27/kWh
    - Peak hours: NT$7.50/kWh (10 AM-12 PM, 1-5 PM)
    - Super-peak hours: NT$9.90/kWh (3-9 PM for large users)
    - Demand charge: NT$230/kW per month (based on 15-min peak)

    Demand charges account for 30-40% of total bill and are the primary
    target for cardiac coordination optimization.
    """

    def __init__(
        self,
        base_rate: float = TAIWAN_RATES['base'],
        peak_rate: float = TAIWAN_RATES['peak'],
        super_peak_rate: float = TAIWAN_RATES['super_peak'],
        demand_charge_rate: float = DEMAND_CHARGE_RATE_NTD
    ):
        """
        Initialize cost calculator.

        Args:
            base_rate: Base/off-peak rate (NT$/kWh)
            peak_rate: Peak hours rate (NT$/kWh)
            super_peak_rate: Super-peak hours rate (NT$/kWh)
            demand_charge_rate: Demand charge (NT$/kW per month)
        """
        self.base_rate = base_rate
        self.peak_rate = peak_rate
        self.super_peak_rate = super_peak_rate
        self.demand_charge_rate = demand_charge_rate

    def get_rate_for_hour(self, hour: int) -> float:
        """
        Get electricity rate for a specific hour of day.

        Args:
            hour: Hour of day (0-23)

        Returns:
            Rate in NT$/kWh
        """
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour must be 0-23, got {hour}")

        if hour in TOU_HOURS['super_peak']:
            return self.super_peak_rate
        elif hour in TOU_HOURS['peak']:
            return self.peak_rate
        else:
            return self.base_rate

    def calculate_energy_cost(
        self,
        energy_kwh: float,
        hour: Optional[int] = None,
        use_avg_tou: bool = True
    ) -> float:
        """
        Calculate energy cost for given consumption.

        Args:
            energy_kwh: Energy consumed (kWh)
            hour: Hour of day (0-23), if known
            use_avg_tou: If hour not provided, use average TOU multiplier

        Returns:
            Cost in NT$
        """
        if hour is not None:
            rate = self.get_rate_for_hour(hour)
        elif use_avg_tou:
            # Use average multiplier from research
            rate = self.base_rate * AVG_TOU_MULTIPLIER
        else:
            rate = self.base_rate

        return energy_kwh * rate

    def calculate_demand_charge(self, peak_power_kw: float) -> float:
        """
        Calculate monthly demand charge based on peak power.

        Demand charge is based on highest 15-minute average power
        consumption during the month.

        Args:
            peak_power_kw: Peak power consumption (kW)

        Returns:
            Monthly demand charge in NT$
        """
        return peak_power_kw * self.demand_charge_rate

    def calculate_total_cost(
        self,
        energy_kwh: float,
        peak_power_kw: float,
        hour: Optional[int] = None,
        use_avg_tou: bool = True
    ) -> Dict[str, float]:
        """
        Calculate total monthly electricity cost.

        Args:
            energy_kwh: Total energy consumed (kWh)
            peak_power_kw: Peak power demand (kW)
            hour: Hour of day for energy cost calculation
            use_avg_tou: Use average TOU multiplier if hour not provided

        Returns:
            Dictionary with cost breakdown
        """
        energy_cost = self.calculate_energy_cost(energy_kwh, hour, use_avg_tou)
        demand_charge = self.calculate_demand_charge(peak_power_kw)
        total_cost = energy_cost + demand_charge

        # Calculate what percentage is demand charge
        demand_pct = (demand_charge / total_cost * 100) if total_cost > 0 else 0

        return {
            'energy_cost_ntd': energy_cost,
            'monthly_demand_charge_ntd': demand_charge,
            'total_monthly_cost_ntd': total_cost,
            'demand_charge_percentage': demand_pct,
        }

    def calculate_from_simulation(
        self,
        results: Dict,
        hour: Optional[int] = None,
        use_avg_tou: bool = True
    ) -> Dict[str, float]:
        """
        Calculate costs from simulation results.

        Args:
            results: Simulation results from SimulationEngine
            hour: Hour of day for TOU pricing
            use_avg_tou: Use average TOU if hour not provided

        Returns:
            Dictionary with cost breakdown
        """
        # Extract power metrics from results
        # (Assuming metrics have been calculated)
        history = results['history']
        aggregate_power = np.array(history['aggregate_power'])
        time_array = np.array(history['time'])

        # Calculate peak power (15-minute average approximation)
        # For simplicity, we use the peak from the entire simulation
        # In reality, would calculate 15-minute rolling average
        peak_power_kw = float(np.max(aggregate_power))

        # Calculate total energy
        total_energy_kwh = float(np.trapz(aggregate_power, time_array) / 3600.0)

        return self.calculate_total_cost(
            total_energy_kwh,
            peak_power_kw,
            hour,
            use_avg_tou
        )

    def compare_costs(
        self,
        baseline_results: Dict,
        cardiac_results: Dict,
        hour: Optional[int] = None,
        use_avg_tou: bool = True
    ) -> Dict:
        """
        Compare costs between baseline and cardiac coordination.

        Args:
            baseline_results: Results from baseline simulation
            cardiac_results: Results from cardiac simulation
            hour: Hour of day for TOU pricing
            use_avg_tou: Use average TOU if hour not provided

        Returns:
            Dictionary with cost comparison
        """
        baseline_cost = self.calculate_from_simulation(
            baseline_results, hour, use_avg_tou
        )
        cardiac_cost = self.calculate_from_simulation(
            cardiac_results, hour, use_avg_tou
        )

        # Calculate savings
        energy_savings = baseline_cost['energy_cost_ntd'] - cardiac_cost['energy_cost_ntd']
        demand_savings = (baseline_cost['monthly_demand_charge_ntd'] -
                         cardiac_cost['monthly_demand_charge_ntd'])
        total_savings = baseline_cost['total_monthly_cost_ntd'] - cardiac_cost['total_monthly_cost_ntd']

        # Calculate percentage savings
        total_savings_pct = (total_savings / baseline_cost['total_monthly_cost_ntd'] * 100
                            if baseline_cost['total_monthly_cost_ntd'] > 0 else 0)

        return {
            'baseline': baseline_cost,
            'cardiac': cardiac_cost,
            'savings': {
                'energy_savings_ntd': energy_savings,
                'demand_savings_ntd': demand_savings,
                'total_savings_ntd': total_savings,
                'total_savings_pct': total_savings_pct,
            }
        }

    def estimate_annual_savings(self, monthly_savings_ntd: float) -> Dict:
        """
        Estimate annual savings and ROI metrics.

        Args:
            monthly_savings_ntd: Monthly cost savings (NT$)

        Returns:
            Dictionary with annual projections
        """
        annual_savings_ntd = monthly_savings_ntd * 12
        annual_savings_usd = annual_savings_ntd / 31.0  # Approximate conversion

        return {
            'annual_savings_ntd': annual_savings_ntd,
            'annual_savings_usd': annual_savings_usd,
            'monthly_savings_ntd': monthly_savings_ntd,
        }

    def __repr__(self) -> str:
        return (f"TaiwanCostCalculator(base={self.base_rate:.2f}, "
                f"peak={self.peak_rate:.2f}, "
                f"super_peak={self.super_peak_rate:.2f}, "
                f"demand_charge={self.demand_charge_rate:.0f})")


# Singleton instance with default Taiwan rates
DEFAULT_CALCULATOR = TaiwanCostCalculator()


# Convenience functions

def calculate_cost_from_simulation(results: Dict, **kwargs) -> Dict:
    """
    Convenience function to calculate costs using default calculator.

    Args:
        results: Simulation results
        **kwargs: Additional arguments for calculate_from_simulation

    Returns:
        Cost breakdown dictionary
    """
    return DEFAULT_CALCULATOR.calculate_from_simulation(results, **kwargs)


def compare_baseline_vs_cardiac_costs(
    baseline_results: Dict,
    cardiac_results: Dict,
    **kwargs
) -> Dict:
    """
    Convenience function to compare costs using default calculator.

    Args:
        baseline_results: Baseline simulation results
        cardiac_results: Cardiac simulation results
        **kwargs: Additional arguments

    Returns:
        Cost comparison dictionary
    """
    return DEFAULT_CALCULATOR.compare_costs(
        baseline_results, cardiac_results, **kwargs
    )
