# Research Summary - Literature Collection
## Servo-Heart: Servo Press Energy Optimization
**Project**: 2025 SEYI Cup Competition Entry

---

## Executive Summary

Collected **15+ academic and industry sources** with relevant servo press power/force data. Identified key parameters for simulation:
- Typical press capacities: 100-800 tons (1000-8000 kN)
- Typical cycle times: 15-30 seconds per part
- Peak power ranges: 50-500 kW depending on tonnage
- Energy consumption patterns identified
- Taiwan TOU pricing structure documented

---

## Part 1: Key Academic Papers Found

### 1. **Sheet Metal Forming Optimization for Servo Press Control**
- **Source**: Metals (MDPI), 2020
- **URL**: https://www.mdpi.com/2075-4701/10/2/271
- **Key Data**: Die reaction force curves over time, shows stepwise force reduction

### 2. **Optimization of Pulsating Curve for Servo Stamping**
- **Source**: Journal of Manufacturing Processes, 2020
- **URL**: https://www.sciencedirect.com/science/article/abs/pii/S1526612520303777
- **Key Finding**: Pulsating curve produced 92.3% greater forming depth
- **Data Available**: Forming force vs time for different curves

### 3. **Motion Profile Optimization in Deep Drawing**
- **Source**: Int'l Journal of Advanced Manufacturing Technology, 2023
- **URL**: https://link.springer.com/article/10.1007/s00170-023-11699-1
- **Key Data**: Motion curves, forming force data, thinning ratios
- **Material**: SUS 304 stainless steel forming

### 4. **Mechanical Servo Press Technology Review**
- **Source**: CIRP Annals - Manufacturing Technology, 2011
- **URL**: https://www.sciencedirect.com/science/article/abs/pii/S0007850611002095
- **Key Content**: Comprehensive review of servo press designs and applications
- **Citations**: 200+ citations, highly respected

### 5. **Servo Press Force and Energy for AHSS**
- **Source**: AHSS Guidelines (Industry Standard)
- **URL**: https://ahssinsights.org/blog/servo-press-force-and-energy-considerations-when-working-with-ahss/
- **Key Data**: Press force curves, energy curves for 600-ton mechanical press
- **Figures**: Figure 2 (Press-Force curve), Figure 3 (Press-Energy curve)

### 6. **Improvement of Metal Forming Quality by Motion Design**
- **Source**: Robotics and Computer-Integrated Manufacturing, 2017
- **URL**: https://www.sciencedirect.com/science/article/abs/pii/S0736584516303192
- **Key Data**: Soft motion vs constant velocity comparisons at 20 SPM
- **Load**: 12 tons on 1mm Cr-Ni steel

### 7. **Modeling and Implementation of Servo Press**
- **Source**: ResearchGate/Int'l Journal of Advanced Manufacturing, 2017
- **URL**: https://www.researchgate.net/publication/312182861
- **Key Data**: Dynamic modeling, multi-body analysis

### 8. **Reduction of Blanking Noise by Controlling Press Motion**
- **Source**: CIRP Annals, 2003
- **Authors**: M. Otsu, C. Yamagata, K. Osakada
- **Key Data**: Sound wave measurement with press cycles

### 9. **Application of Servo Presses to Sheet Metal Forming**
- **Source**: Scientific.Net, Key Engineering Materials, 2011
- **URL**: https://www.scientific.net/KEM.473.27
- **Key Topics**: Springback reduction, deep drawing, hot stamping

### 10. **Servo Press Forming Applications (Part III)**
- **Source**: The Fabricator / Center for Precision Forming (Ohio State)
- **Authors**: Serhat Kaya, Taylan Altan
- **URL**: https://www.thefabricator.com/thefabricator/article/bending/servo-press-forming-applications
- **Data**: Blanking velocities, SPM comparisons, die life data

---

## Part 2: Energy Consumption Data

### Industry Findings:

**Energy Efficiency Comparisons:**
- Servo presses save **15-20% energy** vs hydraulic (multiple sources)
- Some sources claim up to **50-60% reduction** vs traditional mechanical
- Servo screw presses save ~**60% power** vs friction presses
- Motor idles when inactive (near-zero standby power)

**Typical Power Consumption Ranges:**

| Press Capacity | Est. Peak Power | Est. Avg Power | Cycle Time |
|---------------|----------------|----------------|------------|
| 100 ton (1000 kN) | 50-100 kW | 20-40 kW | 15-25 sec |
| 200 ton (2000 kN) | 100-200 kW | 40-80 kW | 20-30 sec |
| 300 ton (3000 kN) | 150-300 kW | 60-120 kW | 20-35 sec |
| 600 ton (6000 kN) | 300-500 kW | 120-200 kW | 25-40 sec |

**Source Notes:**
- AHSS Guidelines shows 600-ton press with energy curves
- Typical forming time at BDC: 2-5 seconds
- Approach/return speeds much faster than forming phase
- Real cycle includes: descent → slow forming → dwell → fast return

---

## Part 3: Taiwan Electricity Pricing

### Current Taiwan Industrial Electricity Rates (2025):

**Base Rates:**
- Industrial average: **NT$4.27 per kWh** (≈ USD $0.14/kWh)
- Household average: NT$2.77 per kWh
- Overall average: NT$3.76 per kWh

**Time-of-Use (TOU) Structure:**
- **Peak hours** (expensive): 10 AM - 12 PM, 1 PM - 5 PM weekdays
- **New super-peak rate**: 3-9 PM at **NT$9.9/kWh** for large users
- **Off-peak** (cheap): Nights and weekends

**Demand Charges:**
- Based on highest 15-minute average power consumption
- Billing period: monthly
- Can account for 30-40% of total electricity bill
- Critical for manufacturing cost control

**Sources:**
1. Taiwan Power Company (Taipower) official data
2. Taiwan News (Jan 2025): New TOU rates for large users
3. Focus Taiwan (Mar 2025): Rate freeze announcement
4. GlobalPetrolPrices.com (Mar 2025): International comparison

---

## Part 4: Servo Press Characteristics Summary

### Key Technical Features:

**Programmability:**
- Fully programmable slide motion curves
- Can adjust: speed, position, dwell time, force
- Multiple motion profiles: sinusoidal, pulsating, coining, stepping
- Real-time adjustments possible

**Force Availability:**
- Full force available throughout stroke (unlike mechanical presses)
- Mechanical presses de-rate at distance from BDC
- Example: 600-ton press → only 250 tons at 3" from BDC

**Speed Ranges:**
- Variable SPM (strokes per minute): 0-1,500 SPM
- Typical production: 20-60 SPM
- Can slow during forming, fast during approach/return

**Control Precision:**
- Position accuracy: ±0.025 mm
- Force control: down to 0.1N for micro applications
- Closed-loop feedback systems

**Energy Management:**
- Only consumes power during active forming
- Regenerative systems store energy in capacitors
- AIDA E.C.O. System: 20+ year capacitor life

---

## Part 5: Manufacturing Context

### Taiwan Manufacturing Landscape:

**Industry Priorities:**
- Industry 4.0 transformation
- Smart manufacturing initiatives
- Energy efficiency mandates
- Sustainability goals

**Pain Points:**
- High electricity costs (demand charges)
- Need for flexible, adaptive production
- Quality requirements increasing
- Competition from automation

**SEYI Cup Competition Alignment:**
- Servo stamping innovation focus
- AI application emphasis
- Energy efficiency value
- Real industrial problem

---

## Part 6: Data Digitization Strategy

### Papers with Graphical Data to Digitize:

**Priority 1 - Best Graphs:**
1. ✅ AHSS Guidelines - Press force curve (Figure 2)
2. ✅ AHSS Guidelines - Press energy curve (Figure 3)
3. ✅ MDPI Metals paper - Die reaction force curves (Figure 29)
4. ✅ Pulsating curve paper - Force profiles comparison

**Priority 2 - Good Supporting Data:**
5. Motion profile optimization - Thinning ratio vs parameters
6. Blanking noise reduction - Force-time synchronized data
7. Improvement by motion design - Soft motion vs constant velocity

**Priority 3 - Additional Context:**
8. Various papers with cycle time data
9. Energy consumption comparisons
10. Speed/tonnage relationships

---

## Part 7: Typical Power Profile Structure

Based on literature synthesis, a typical servo press power profile follows:

```
Phase 1: Approach (2-5 sec)
- Rapid descent to workpiece
- Low power (motor accelerating slide)
- ~10-20% of peak power

Phase 2: Contact & Forming (3-8 sec)
- Slow, controlled deformation
- PEAK POWER here
- 80-100% of rated power
- Can include "dwell" at BDC

Phase 3: Return (2-4 sec)
- Fast return to top
- Moderate power
- ~20-40% of peak

Phase 4: Idle
- Waiting for next part/cycle
- Near-zero power (motor idles)

Total Cycle: 15-30 seconds typical
```

---

## Part 8: Key Parameters for Simulation

### Values to Use in MVP:

**Press Fleet Configuration:**
- Number of presses: 4-8 units
- Capacity range: 100-300 tons each
- Assumed peak power: 100-250 kW per press
- Cycle time: 20-25 seconds average

**Swarm Coordination Parameters:**
- Sensing radius: 2-3 neighbor connections
- Coordination delay tolerance: ±3-5 seconds
- Priority weights: TOU pricing, neighbor state, production queue

**Energy Metrics:**
- Taiwan industrial rate: NT$4.27/kWh base
- Peak rate: NT$9.9/kWh (super-peak hours)
- Demand charge: critical for 15-min windows
- Target reduction: 20-30% peak demand

---


