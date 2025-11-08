# Quick Reference: Servo Press Power Profiles
## For Simulation Development - Servo-Heart Project

---

## Standard Profile Template

### Typical 200-Ton Servo Press Cycle (25 seconds total)

```
Phase 1: APPROACH (0-7 sec)
- Rapid descent from top dead center to workpiece
- Power: 30-50 kW (20% of peak)
- Purpose: Position ram quickly

Phase 2: FORMING (7-15 sec)
- Contact, deformation, and optional dwell
- Power: 150-200 kW (80-100% of peak) 
- Purpose: Metal deformation
- Sub-phases:
  * Initial contact: 7-9 sec (power ramps up)
  * Peak forming: 9-12 sec (max power)
  * Dwell (optional): 12-14 sec (sustained force)
  * Release: 14-15 sec (power drops)

Phase 3: RETURN (15-21 sec)
- Fast return to top dead center
- Power: 40-70 kW (25-35% of peak)
- Purpose: Retract ram

Phase 4: IDLE (21-25 sec)
- Waiting for next cycle/part feed
- Power: ~5 kW (motor idling)
- Purpose: Part removal, feeding

TOTAL CYCLE: 25 seconds
AVERAGE POWER: ~65 kW
PEAK POWER: 200 kW
ENERGY PER CYCLE: ~0.45 kWh
```

---

## Profile Variations by Press Capacity

### Small Press (100 tons / 1000 kN)
- **Peak Power**: 75-100 kW
- **Cycle Time**: 15-20 seconds
- **Typical SPM**: 30-60
- **Applications**: Small stampings, electronics
- **Energy/Cycle**: ~0.25 kWh

### Medium Press (200 tons / 2000 kN)
- **Peak Power**: 150-200 kW
- **Cycle Time**: 20-25 seconds
- **Typical SPM**: 20-40
- **Applications**: Automotive parts, general stamping
- **Energy/Cycle**: ~0.45 kWh

### Large Press (300 tons / 3000 kN)
- **Peak Power**: 225-300 kW
- **Cycle Time**: 25-35 seconds
- **Typical SPM**: 15-25
- **Applications**: Heavy structural parts, deep draw
- **Energy/Cycle**: ~0.75 kWh

### Heavy Press (600 tons / 6000 kN)
- **Peak Power**: 400-600 kW
- **Cycle Time**: 30-45 seconds
- **Typical SPM**: 8-15
- **Applications**: Large body panels, thick steel
- **Energy/Cycle**: ~2.0 kWh

---

## Motion Profile Types

### 1. Standard Sinusoidal (Crank-like)
```
Power curve: Smooth bell shape
Peak at: Mid-stroke
Duration: Shortest cycle time
Use case: Simple blanking, high volume
```

### 2. Pulsating (with pause)
```
Power curve: Ramp → plateau → drop → resume → plateau → drop
Peak at: Multiple peaks
Duration: +10-20% vs standard
Use case: Complex forming, re-lubrication
Advantage: +92% forming depth (literature)
```

### 3. Coining (with dwell)
```
Power curve: Ramp → sustained peak → drop
Peak at: Bottom dead center
Duration: +20-30% vs standard
Use case: High-precision, springback control
Dwell time: 2-5 seconds typical
```

### 4. Stepping (multi-stage)
```
Power curve: Multiple steps/plateaus
Peaks at: Sequential operations
Duration: +30-50% vs standard
Use case: Multi-operation forming, assembly
```

---

## Power-to-Force Conversion

### Formula
```
Power (kW) = Force (kN) × Velocity (m/s)
```

### Typical Velocities
- **Approach**: 0.1-0.3 m/s
- **Forming**: 0.01-0.05 m/s (slow, controlled)
- **Return**: 0.15-0.4 m/s
- **At BDC**: Near zero (dwell)

### Example Calculation
```
200-ton press = 2000 kN
Forming velocity = 0.1 m/s
Peak Power = 2000 × 0.1 = 200 kW ✓
```

---

## Energy Consumption Patterns

### Daily Production Scenario
```
Press: 200-ton servo
Shift: 8 hours
SPM: 30 (2-second cycle)
Parts/shift: 30 × 60 min × 8 hr = 14,400 parts

Energy per cycle: 0.45 kWh
Total daily energy: 14,400 × 0.45 = 6,480 kWh
```

### Cost Analysis (Taiwan)
```
Base rate: NT$4.27/kWh
Daily cost (off-peak): 6,480 × 4.27 = NT$27,670 (~USD $850)

Peak rate: NT$9.9/kWh (3-9 PM)
If 50% in peak hours:
Cost = (3,240 × 4.27) + (3,240 × 9.9) 
     = 13,835 + 32,076
     = NT$45,911 (~USD $1,410)

Savings with coordination: 20-30% reduction in peak
Estimated savings: NT$4,000-6,000/day per press
```

---

## Swarm Coordination Scenarios

### Scenario 1: NO COORDINATION (Baseline)
```
4 presses, random start times
Peak aggregate: 4 × 200 kW = 800 kW (all peak simultaneously)
15-min average peak: ~650 kW
Demand charge basis: 650 kW
```

### Scenario 2: SIMPLE DELAY
```
4 presses, staggered by 6 seconds
Peak aggregate: 3 × 200 + 1 × 100 = 700 kW (partial overlap)
15-min average peak: ~480 kW
Reduction: 26%
```

### Scenario 3: SWARM COORDINATION
```
4 presses, adaptive coordination
- Press 1 at peak: Press 2,3,4 delay if possible
- Press 2 at peak: Others in approach/return/idle
- Dynamic adjustment based on:
  * TOU pricing (avoid 3-9 PM peaks)
  * Production priority
  * Neighbor states

Peak aggregate: 2.5 × 200 kW = 500 kW (smart overlap)
15-min average peak: ~380 kW
Reduction: 42%
```

---

## Profile Generation Strategy

### For 8-10 Profiles:

**Base Profiles (4)**:
1. Standard 100-ton (fast cycle)
2. Standard 200-ton (medium)
3. Standard 300-ton (slower, heavy)
4. Standard 200-ton with dwell (coining)

**Variations (4-6)**:
5. 200-ton pulsating (pause mid-stroke)
6. 150-ton stepping (multi-operation)
7. 250-ton slow forming (AHSS)
8. 100-ton high-speed (60 SPM)
9. 200-ton with extended dwell
10. 300-ton progressive die (multiple hits)

### Variation Parameters:
- Cycle time: ±20%
- Peak power: ±15%
- Dwell duration: 0-5 seconds
- Phase timing: shift by ±10%

---

## CSV Format for Profiles

```csv
time_sec,power_kw,phase,notes
0.0,10.0,idle,motor startup
1.0,35.0,approach,accelerating
2.0,45.0,approach,full descent speed
...
9.0,180.0,forming,peak forming force
10.0,200.0,forming,maximum power
11.0,195.0,forming,sustained
12.0,150.0,forming,release starting
...
25.0,5.0,idle,cycle complete
```

---

## Key Assumptions to Document

1. **Motor Efficiency**: 90-95% (servo motors)
2. **Transmission Efficiency**: 85-90% (ball screw, gears)
3. **Idle Power**: 3-8 kW (cooling, controls)
4. **Power Factor**: 0.85-0.95 (for AC motors)
5. **Regenerative Braking**: 10-20% energy recovery (return stroke)

---

## Validation Checkpoints

✅ **Peak power reasonable?**
   - Rule of thumb: ~1 kW per kN of force
   - 200-ton press ≈ 200 kW peak ✓

✅ **Cycle energy matches literature?**
   - Compare to published efficiency data
   - Should align with ±20%

✅ **Phase durations realistic?**
   - Approach: 20-30% of cycle
   - Forming: 30-40% of cycle
   - Return: 20-30% of cycle
   - Idle: 10-20% of cycle

✅ **Multiple profiles show variation?**
   - Coefficient of variation: 15-25%
   - Reflects real factory diversity

---

## Common Pitfalls to Avoid

❌ **Unrealistic simultaneity**
   - Don't assume all presses always peak together
   - Real factories have some natural variation

❌ **Ignoring idle time**
   - Presses don't run continuously
   - Factor in part loading/unloading

❌ **Perfect square waves**
   - Power ramps up/down gradually
   - Use smooth transitions

❌ **Forgetting regeneration**
   - Some energy recovered during return stroke
   - Can reduce apparent power draw

---

## Ready-to-Use Profile Parameters

Profile templates for simulation code:

```python
PROFILE_TEMPLATES = {
    'small_fast': {
        'capacity_tons': 100,
        'peak_power_kw': 85,
        'cycle_time_sec': 18,
        'forming_time_sec': 6,
        'dwell_time_sec': 0
    },
    'medium_standard': {
        'capacity_tons': 200,
        'peak_power_kw': 180,
        'cycle_time_sec': 25,
        'forming_time_sec': 8,
        'dwell_time_sec': 0
    },
    'medium_coining': {
        'capacity_tons': 200,
        'peak_power_kw': 190,
        'cycle_time_sec': 30,
        'forming_time_sec': 10,
        'dwell_time_sec': 3
    },
    'large_slow': {
        'capacity_tons': 300,
        'peak_power_kw': 270,
        'cycle_time_sec': 35,
        'forming_time_sec': 12,
        'dwell_time_sec': 2
    }
}
```

---

*Quick Reference Guide v1.0*  
