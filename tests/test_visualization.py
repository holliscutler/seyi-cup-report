"""
Test Visualization Components

Tests plot generation and component creation without running the full app.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.heart_sim import (
    create_coordinator_auto,
    SimulationEngine,
    MetricsCollector,
)
from src.heart_sim.visualization.plots import (
    create_aggregate_power_plot,
    create_individual_power_plot,
    create_phase_evolution_plot,
    create_state_timeline_plot,
    create_collision_risk_plot,
    create_refractory_timeline_plot,
    create_power_histogram,
)
from src.heart_sim.visualization.components import (
    create_header,
    create_control_panel,
    create_metrics_card,
    create_comparison_card,
    create_info_card,
)
from src.heart_sim.visualization import create_app


def test_run_simulation():
    """Test running a quick simulation for visualization."""
    print("\n" + "="*70)
    print("TEST: Run Simulation for Visualization")
    print("="*70)

    # Create coordinator
    coordinator = create_coordinator_auto(
        n_presses=4,
        mix='realistic',
        topology='ring',
        max_delay_sec=5.0,
        seed=42
    )

    print(f"\n✓ Created coordinator with {len(coordinator.presses)} presses")

    # Run simulation
    print("  Running 30-second simulation...")
    engine = SimulationEngine(coordinator)
    results = engine.run(duration_sec=30.0, dt=0.5, verbose=False)

    print(f"✓ Simulation complete: {len(results['history']['time'])} timesteps")

    return results


def test_plot_generation(results):
    """Test all plot generation functions."""
    print("\n" + "="*70)
    print("TEST: Plot Generation")
    print("="*70)

    tests = [
        ("Aggregate Power", lambda: create_aggregate_power_plot(cardiac_results=results)),
        ("Individual Power", lambda: create_individual_power_plot(results)),
        ("Phase Evolution", lambda: create_phase_evolution_plot(results)),
        ("State Timeline", lambda: create_state_timeline_plot(results)),
        ("Collision Risk", lambda: create_collision_risk_plot(results)),
        ("Refractory Timeline", lambda: create_refractory_timeline_plot(results)),
        ("Power Histogram", lambda: create_power_histogram(cardiac_results=results)),
    ]

    for name, plot_func in tests:
        try:
            fig = plot_func()
            print(f"✅ {name}: {len(fig.data)} trace(s)")
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
            return False

    return True


def test_component_generation():
    """Test UI component generation."""
    print("\n" + "="*70)
    print("TEST: Component Generation")
    print("="*70)

    components = [
        ("Header", create_header),
        ("Control Panel", create_control_panel),
        ("Info Card", lambda: create_info_card("💡", "Test", "Content")),
        ("Metrics Card", lambda: create_metrics_card(
            "Test Metrics",
            {'Metric 1': '100', 'Metric 2': '200'}
        )),
        ("Comparison Card", lambda: create_comparison_card({
            'baseline_peak_kw': 500,
            'cardiac_peak_kw': 450,
            'peak_reduction_pct': 10.0,
            'cardiac_delays': 42,
            'cardiac_collisions_avoided': 38,
        })),
    ]

    for name, component_func in components:
        try:
            component = component_func()
            print(f"✅ {name}: Created")
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
            return False

    return True


def test_app_creation():
    """Test Dash app creation."""
    print("\n" + "="*70)
    print("TEST: App Creation")
    print("="*70)

    try:
        app = create_app()
        print(f"✅ App created successfully")
        print(f"  Title: {app.title}")
        print(f"  Layout components: {len(app.layout.children)}")
        return True
    except Exception as e:
        print(f"❌ App creation FAILED: {e}")
        return False


def test_baseline_vs_cardiac_visualization():
    """Test baseline vs cardiac comparison visualization."""
    print("\n" + "="*70)
    print("TEST: Baseline vs Cardiac Visualization")
    print("="*70)

    # Run baseline
    print("  Running baseline simulation...")
    baseline_coord = create_coordinator_auto(
        n_presses=4,
        mix='realistic',
        topology='ring',
        max_delay_sec=0.0,  # No coordination
        seed=42
    )
    baseline_engine = SimulationEngine(baseline_coord)
    baseline_results = baseline_engine.run(duration_sec=30.0, dt=0.5, verbose=False)

    # Run cardiac
    print("  Running cardiac simulation...")
    cardiac_coord = create_coordinator_auto(
        n_presses=4,
        mix='realistic',
        topology='ring',
        max_delay_sec=5.0,  # With coordination
        seed=42
    )
    cardiac_engine = SimulationEngine(cardiac_coord)
    cardiac_results = cardiac_engine.run(duration_sec=30.0, dt=0.5, verbose=False)

    # Create comparison plot
    try:
        fig = create_aggregate_power_plot(
            baseline_results=baseline_results,
            cardiac_results=cardiac_results,
            show_baseline=True,
            show_cardiac=True
        )
        print(f"✅ Comparison plot created: {len(fig.data)} traces")

        # Calculate comparison
        comparison = MetricsCollector.compare_baseline_vs_cardiac(
            baseline_results, cardiac_results
        )
        print(f"✅ Comparison metrics calculated")
        print(f"  Peak reduction: {comparison['peak_reduction_pct']:+.2f}%")
        print(f"  Cardiac delays: {comparison['cardiac_delays']}")
        print(f"  Collisions avoided: {comparison['cardiac_collisions_avoided']}")

        return True
    except Exception as e:
        print(f"❌ Comparison visualization FAILED: {e}")
        return False


def run_all_tests():
    """Run all visualization tests."""
    print("\n" + "="*70)
    print("VISUALIZATION MODULE - TEST SUITE")
    print("="*70)

    results = []

    # Test 1: Simulation
    cardiac_results = test_run_simulation()
    results.append(("Simulation", cardiac_results is not None))

    if cardiac_results:
        # Test 2: Plots
        plot_success = test_plot_generation(cardiac_results)
        results.append(("Plot Generation", plot_success))

    # Test 3: Components
    component_success = test_component_generation()
    results.append(("Component Generation", component_success))

    # Test 4: App Creation
    app_success = test_app_creation()
    results.append(("App Creation", app_success))

    # Test 5: Comparison Visualization
    comparison_success = test_baseline_vs_cardiac_visualization()
    results.append(("Baseline vs Cardiac", comparison_success))

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
        print("\n🎉 ALL VISUALIZATION TESTS PASSED!")
        print("\n🚀 Ready to launch:")
        print("   python run_visualization.py")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
