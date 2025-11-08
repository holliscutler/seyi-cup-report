"""
Report Generators

Functions for generating reports in various formats (JSON, CSV, Markdown).
"""

import json
import csv
from typing import List, Dict
from datetime import datetime


def generate_json_report(data: Dict, filename: str):
    """
    Generate JSON report.

    Args:
        data: Dictionary to save
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"JSON report saved to: {filename}")


def generate_csv_summary(results_summary: Dict, filename: str):
    """
    Generate CSV summary table.

    Useful for importing into spreadsheets.

    Args:
        results_summary: Summary dictionary (from aggregate_across_seeds or similar)
        filename: Output CSV filename
    """
    # Handle different summary formats
    if 'by_press_count' in results_summary:
        # Press count scaling summary
        rows = []
        for n_presses, data in results_summary['by_press_count'].items():
            rows.append({
                'n_presses': n_presses,
                'n_seeds': data['n_scenarios'],
                'win_rate_pct': f"{data['win_rate']:.1f}",
                'mean_peak_reduction_pct': f"{data['peak_reduction']['mean_pct']:.2f}",
                'std_peak_reduction_pct': f"{data['peak_reduction']['std_pct']:.2f}",
                'mean_baseline_peak_kw': f"{data['baseline_peak']['mean_kw']:.1f}",
                'mean_cardiac_peak_kw': f"{data['cardiac_peak']['mean_kw']:.1f}",
                'mean_annual_savings_usd': f"{data['cost_savings']['mean_annual_usd']:.0f}",
                'mean_delays': f"{data['coordination']['mean_delays']:.0f}",
                'mean_collisions_avoided': f"{data['coordination']['mean_collisions_avoided']:.0f}",
            })

        fieldnames = list(rows[0].keys()) if rows else []

    elif 'n_scenarios' in results_summary:
        # Single aggregation
        rows = [{
            'n_presses': results_summary['config']['n_presses'],
            'mix': results_summary['config']['mix'],
            'topology': results_summary['config']['topology'],
            'n_seeds': results_summary['n_scenarios'],
            'win_rate_pct': f"{results_summary['win_rate']:.1f}",
            'mean_peak_reduction_pct': f"{results_summary['peak_reduction']['mean_pct']:.2f}",
            'std_peak_reduction_pct': f"{results_summary['peak_reduction']['std_pct']:.2f}",
            'mean_baseline_peak_kw': f"{results_summary['baseline_peak']['mean_kw']:.1f}",
            'mean_cardiac_peak_kw': f"{results_summary['cardiac_peak']['mean_kw']:.1f}",
            'mean_annual_savings_usd': f"{results_summary['cost_savings']['mean_annual_usd']:.0f}",
        }]
        fieldnames = list(rows[0].keys())

    else:
        print("Warning: Unknown summary format for CSV generation")
        return

    # Write CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV summary saved to: {filename}")


def generate_markdown_report(results_summary: Dict, filename: str, title: str = "Test Results"):
    """
    Generate human-readable markdown report.

    Args:
        results_summary: Summary dictionary
        filename: Output markdown filename
        title: Report title
    """
    lines = []

    # Header
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Handle different summary formats
    if 'by_press_count' in results_summary:
        # Press count scaling report
        lines.append("## Scaling Analysis: Press Count")
        lines.append("")
        lines.append(f"**Total Scenarios**: {results_summary['summary']['total_scenarios']}")
        lines.append(f"**Press Counts Tested**: {', '.join(map(str, results_summary['summary']['press_counts']))}")
        lines.append("")

        lines.append("### Results by Press Count")
        lines.append("")
        lines.append("| Presses | Seeds | Win Rate | Peak Reduction | Baseline Peak | Cardiac Peak | Annual Savings |")
        lines.append("|---------|-------|----------|----------------|---------------|--------------|----------------|")

        for n_presses in sorted(results_summary['by_press_count'].keys()):
            data = results_summary['by_press_count'][n_presses]
            lines.append(
                f"| {n_presses} | "
                f"{data['n_scenarios']} | "
                f"{data['win_rate']:.1f}% | "
                f"{data['peak_reduction']['mean_pct']:.1f}% ± {data['peak_reduction']['std_pct']:.1f}% | "
                f"{data['baseline_peak']['mean_kw']:.0f} kW | "
                f"{data['cardiac_peak']['mean_kw']:.0f} kW | "
                f"${data['cost_savings']['mean_annual_usd']:.0f} |"
            )

        lines.append("")
        lines.append("### Detailed Statistics by Press Count")
        lines.append("")

        for n_presses in sorted(results_summary['by_press_count'].keys()):
            data = results_summary['by_press_count'][n_presses]
            lines.append(f"#### {n_presses} Presses")
            lines.append("")
            lines.append(f"- **Seeds Tested**: {', '.join(map(str, data['seeds']))}")
            lines.append(f"- **Win Rate**: {data['win_rate']:.1f}%")
            lines.append(f"- **Peak Reduction**: {data['peak_reduction']['mean_pct']:.2f}% (±{data['peak_reduction']['std_pct']:.2f}%)")
            lines.append(f"  - Range: {data['peak_reduction']['min_pct']:.1f}% to {data['peak_reduction']['max_pct']:.1f}%")
            lines.append(f"  - Median: {data['peak_reduction']['median_pct']:.1f}%")
            lines.append(f"- **Baseline Peak**: {data['baseline_peak']['mean_kw']:.1f} kW (±{data['baseline_peak']['std_kw']:.1f} kW)")
            lines.append(f"- **Cardiac Peak**: {data['cardiac_peak']['mean_kw']:.1f} kW (±{data['cardiac_peak']['std_kw']:.1f} kW)")
            lines.append(f"- **Cost Savings**:")
            lines.append(f"  - Monthly: NT$ {data['cost_savings']['mean_monthly_ntd']:,.0f}")
            lines.append(f"  - Annual: ${data['cost_savings']['mean_annual_usd']:,.0f} USD")
            lines.append(f"- **Coordination**:")
            lines.append(f"  - Mean Delays: {data['coordination']['mean_delays']:.0f}")
            lines.append(f"  - Mean Collisions Avoided: {data['coordination']['mean_collisions_avoided']:.0f}")
            lines.append(f"  - Mean Phase Spread: {data['coordination']['mean_phase_spread']:.3f}")
            lines.append("")

    elif 'n_scenarios' in results_summary:
        # Single aggregation
        data = results_summary
        lines.append("## Test Results Summary")
        lines.append("")
        lines.append(f"**Configuration**:")
        lines.append(f"- Presses: {data['config']['n_presses']}")
        lines.append(f"- Mix: {data['config']['mix']}")
        lines.append(f"- Topology: {data['config']['topology']}")
        lines.append(f"- Duration: {data['config']['duration_sec']/60:.0f} minutes")
        lines.append(f"- Max Delay: {data['config']['max_delay_sec']}s")
        lines.append("")

        lines.append(f"**Seeds Tested**: {', '.join(map(str, data['seeds']))}")
        lines.append(f"**Total Scenarios**: {data['n_scenarios']}")
        lines.append("")

        lines.append("### Performance Metrics")
        lines.append("")
        lines.append(f"- **Win Rate**: {data['win_rate']:.1f}%")
        lines.append(f"- **Peak Reduction**: {data['peak_reduction']['mean_pct']:.2f}% (±{data['peak_reduction']['std_pct']:.2f}%)")
        lines.append(f"  - Range: {data['peak_reduction']['min_pct']:.1f}% to {data['peak_reduction']['max_pct']:.1f}%")
        lines.append(f"  - Median: {data['peak_reduction']['median_pct']:.1f}%")
        lines.append(f"- **Baseline Peak**: {data['baseline_peak']['mean_kw']:.1f} kW (±{data['baseline_peak']['std_kw']:.1f} kW)")
        lines.append(f"- **Cardiac Peak**: {data['cardiac_peak']['mean_kw']:.1f} kW (±{data['cardiac_peak']['std_kw']:.1f} kW)")
        lines.append("")

        lines.append("### Cost Savings")
        lines.append("")
        lines.append(f"- **Monthly**: NT$ {data['cost_savings']['mean_monthly_ntd']:,.0f}")
        lines.append(f"- **Annual**: ${data['cost_savings']['mean_annual_usd']:,.0f} USD")
        lines.append("")

        lines.append("### Coordination Activity")
        lines.append("")
        lines.append(f"- **Mean Delays**: {data['coordination']['mean_delays']:.0f}")
        lines.append(f"- **Mean Collisions Avoided**: {data['coordination']['mean_collisions_avoided']:.0f}")
        lines.append(f"- **Mean Phase Spread**: {data['coordination']['mean_phase_spread']:.3f}")
        lines.append("")

    # Write to file
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Markdown report saved to: {filename}")


def generate_summary_table(results_summary: Dict) -> str:
    """
    Generate a quick summary table as a string.

    Useful for console output.

    Args:
        results_summary: Summary dictionary

    Returns:
        Formatted table string
    """
    if 'by_press_count' in results_summary:
        # Press count scaling
        lines = []
        lines.append("")
        lines.append("="*80)
        lines.append("SCALING ANALYSIS: PRESS COUNT")
        lines.append("="*80)
        lines.append("")
        lines.append(f"{'Press':<8} {'Seeds':<8} {'Win%':<8} {'Peak↓%':<12} {'Baseline':<12} {'Cardiac':<12} {'Savings/yr':<12}")
        lines.append("-"*80)

        for n_presses in sorted(results_summary['by_press_count'].keys()):
            data = results_summary['by_press_count'][n_presses]
            lines.append(
                f"{n_presses:<8} "
                f"{data['n_scenarios']:<8} "
                f"{data['win_rate']:>6.1f}% "
                f"{data['peak_reduction']['mean_pct']:>6.1f}±{data['peak_reduction']['std_pct']:.1f}% "
                f"{data['baseline_peak']['mean_kw']:>9.0f}kW "
                f"{data['cardiac_peak']['mean_kw']:>9.0f}kW "
                f"${data['cost_savings']['mean_annual_usd']:>9.0f}"
            )

        lines.append("-"*80)
        lines.append("")

        return '\n'.join(lines)

    elif 'n_scenarios' in results_summary:
        # Single aggregation
        data = results_summary
        lines = []
        lines.append("")
        lines.append("="*60)
        lines.append("TEST RESULTS SUMMARY")
        lines.append("="*60)
        lines.append(f"  Config: {data['config']['n_presses']}p {data['config']['mix']} {data['config']['topology']}")
        lines.append(f"  Seeds: {data['n_scenarios']}")
        lines.append(f"  Win Rate: {data['win_rate']:.1f}%")
        lines.append(f"  Peak Reduction: {data['peak_reduction']['mean_pct']:.1f}% (±{data['peak_reduction']['std_pct']:.1f}%)")
        lines.append(f"  Annual Savings: ${data['cost_savings']['mean_annual_usd']:,.0f} USD")
        lines.append("="*60)
        lines.append("")

        return '\n'.join(lines)

    return ""
