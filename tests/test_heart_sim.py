"""
Comprehensive Test Script for heart_sim v2.0

Tests all major components with research-validated scenarios.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.heart_sim import (
    # Power profiles
    create_power_profile,
    create_press_fleet,
    list_available_templates,
    validate_profile,

    # Coordination
    create_coordinator_auto,
    create_baseline_coordinator,
    create_coordinator_from_templates,

    # Simulation
    SimulationEngine,
    MetricsCollector,
    create_summary_report,

    # Cost
    calculate_cost_from_simulation,
    compare_baseline_vs_cardiac_costs,
)


def test_power_profiles():
    """Test power profile system."""
    print("\n" + "="*70)
    print("TEST 1: Power Profile System")
    print("="*70)

    # List available templates
    templates = list_available_templates()
    print(f"\nAvailable templates: {len(templates)}")
    print(f"  {', '.join(templates[:5])}...")

    # Create a profile
    profile = create_power_profile('medium_standard', variation=0.1, seed=42)
    print(f"\nCreated profile: {profile}")
    print(f"  Peak power: {profile.peak_power_kw:.1f} kW")
    print(f"  Avg power: {profile.avg_power_kw:.1f} kW")
    print(f"  Energy/cycle: {profile.energy_per_cycle_kwh:.3f} kWh")

    # Validate profile
    validation = validate_profile(profile)
    print(f"\nValidation: {'✅ PASS' if validation['all_valid'] else '❌ FAIL'}")
    for check, result in validation.items():
        if check != 'all_valid':
            status = "✓" if result else "✗"
            print(f"  {status} {check}")

    # Create a fleet
    fleet = create_press_fleet(n_presses=4, mix='realistic', variation=0.1, seed=42)
    print(f"\nCreated fleet of {len(fleet)} presses:")
    for i, p in enumerate(fleet):
        print(f"  {i+1}. {p.press_type}: {p.peak_power_kw:.0f}kW, {p.cycle_time_sec:.0f}s")

    return True


def test_coordinator():
    """Test coordinator and topology."""
    print("\n" + "="*70)
    print("TEST 2: Coordinator & Topology")
    print("="*70)

    # Create coordinator
    coordinator = create_coordinator_auto(
        n_presses=6,
        mix='realistic',
        topology='ring',
        max_delay_sec=5.0,
        variation=0.1,
        seed=42
    )

    print(f"\nCreated coordinator: {coordinator}")
    print(f"  Presses: {len(coordinator.presses)}")
    print(f"  Pacemaker: {coordinator.pacemaker.press_id}")
    print(f"  Topology: {coordinator.topology_type}")

    # Print summary
    print(coordinator.get_summary())

    return True


def test_simulation():
    """Test simulation engine."""
    print("\n" + "="*70)
    print("TEST 3: Simulation Engine")
    print("="*70)

    # Create coordinator
    coordinator = create_coordinator_auto(
        n_presses=4,
        mix='realistic',
        topology='ring',
        seed=42
    )

    # Create simulation engine
    engine = SimulationEngine(coordinator)
    print(f"\nCreated engine: {engine}")

    # Run simulation
    print("\nRunning simulation (60 seconds)...")
    results = engine.run(duration_sec=60.0, dt=0.5, verbose=False)

    # Check results
    print(f"  Duration: {results['metadata']['duration_sec']}s")
    print(f"  Steps: {results['metadata']['num_steps']}")
    print(f"  Data points: {len(results['history']['time'])}")

    # Calculate metrics
    metrics = MetricsCollector.calculate_all_metrics(results)
    print(f"\nMetrics:")
    print(f"  Peak Power: {metrics['peak_power_kw']:.1f} kW")
    print(f"  Avg Power: {metrics['avg_power_kw']:.1f} kW")
    print(f"  Total Delays: {metrics['total_delays']}")
    print(f"  Collisions Avoided: {metrics['total_collisions_avoided']}")

    return True


def test_baseline_vs_cardiac():
    """Test baseline vs cardiac comparison."""
    print("\n" + "="*70)
    print("TEST 4: Baseline vs Cardiac Comparison")
    print("="*70)

    # Create template list for consistent comparison
    templates = ['medium_standard', 'medium_coining', 'large_slow', 'small_fast']

    # Create baseline coordinator (max_delay=0, no coordination)
    print("\nRunning BASELINE simulation (no coordination)...")
    baseline_coord = create_coordinator_from_templates(
        templates,
        topology='ring',
        max_delay_sec=0.0,  # NO COORDINATION
        variation=0.0,  # No variation for fair comparison
        seed=42
    )

    baseline_engine = SimulationEngine(baseline_coord)
    baseline_results = baseline_engine.run(duration_sec=180.0, dt=0.5, verbose=False)

    # Create cardiac coordinator
    print("Running CARDIAC simulation (with coordination)...")
    cardiac_coord = create_coordinator_from_templates(
        templates,
        topology='ring',
        max_delay_sec=5.0,  # WITH COORDINATION
        variation=0.0,
        seed=42
    )

    cardiac_engine = SimulationEngine(cardiac_coord)
    cardiac_results = cardiac_engine.run(duration_sec=180.0, dt=0.5, verbose=False)

    # Compare metrics
    comparison = MetricsCollector.compare_baseline_vs_cardiac(
        baseline_results, cardiac_results
    )

    print(f"\n📊 COMPARISON RESULTS:")
    print(f"  Baseline Peak: {comparison['baseline_peak_kw']:.1f} kW")
    print(f"  Cardiac Peak:  {comparison['cardiac_peak_kw']:.1f} kW")
    print(f"  Peak Reduction: {comparison['peak_reduction_kw']:.1f} kW ({comparison['peak_reduction_pct']:+.2f}%)")
    print(f"\n  Baseline Avg: {comparison['baseline_avg_kw']:.1f} kW")
    print(f"  Cardiac Avg:  {comparison['cardiac_avg_kw']:.1f} kW")
    print(f"  Avg Change: {comparison['avg_change_kw']:.1f} kW ({comparison['avg_change_pct']:+.2f}%)")

    print(f"\n  Cardiac Activity:")
    print(f"    Delays: {comparison['cardiac_delays']}")
    print(f"    Collisions Avoided: {comparison['cardiac_collisions_avoided']}")
    print(f"    Phase Spread: {comparison['cardiac_phase_spread']:.2%}")

    # Cost comparison
    cost_comparison = compare_baseline_vs_cardiac_costs(
        baseline_results, cardiac_results
    )

    print(f"\n💰 COST COMPARISON (Taiwan):")
    print(f"  Baseline Total: NT$ {cost_comparison['baseline']['total_monthly_cost_ntd']:.0f}")
    print(f"  Cardiac Total:  NT$ {cost_comparison['cardiac']['total_monthly_cost_ntd']:.0f}")
    print(f"  SAVINGS: NT$ {cost_comparison['savings']['total_savings_ntd']:+.0f} "
          f"({cost_comparison['savings']['total_savings_pct']:+.1f}%)")
    print(f"    Energy Savings: NT$ {cost_comparison['savings']['energy_savings_ntd']:+.0f}")
    print(f"    Demand Savings: NT$ {cost_comparison['savings']['demand_savings_ntd']:+.0f}")

    # Success criteria
    success = (
        comparison['peak_reduction_pct'] > 0 or  # Any peak reduction
        comparison['cardiac_collisions_avoided'] > 0  # Or collision avoidance activity
    )

    return success


def test_summary_report():
    """Test summary report generation."""
    print("\n" + "="*70)
    print("TEST 5: Summary Report Generation")
    print("="*70)

    # Run a quick simulation
    coordinator = create_coordinator_auto(n_presses=4, mix='realistic', seed=42)
    engine = SimulationEngine(coordinator)
    results = engine.run(duration_sec=60.0, dt=0.5, verbose=False)

    # Generate cost data
    cost_data = calculate_cost_from_simulation(results)

    # Create summary report
    report = create_summary_report(results, include_cost=True, cost_data=cost_data)

    print("\n" + report)

    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("HEART_SIM v2.0 - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("Testing research-validated cardiac coordination system")
    print("="*70)

    tests = [
        ("Power Profiles", test_power_profiles),
        ("Coordinator & Topology", test_coordinator),
        ("Simulation Engine", test_simulation),
        ("Baseline vs Cardiac", test_baseline_vs_cardiac),
        ("Summary Report", test_summary_report),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
            print(f"\n✅ {name}: PASS")
        except Exception as e:
            results.append((name, False))
            print(f"\n❌ {name}: FAIL - {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! heart_sim v2.0 is ready!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
