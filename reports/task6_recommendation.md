# Task 6 — Comparative Synthesis and Recommendation

## Final comparison

| Metric | Linear | Star |
|---|---:|---:|
| Selected parameter | 1.20 mm | 1.50 mm |
| Total route length | 1.400 mm | 3.356 mm |
| Longest route / weakest-path proxy | 0.350 mm | 0.839 mm |
| Crossings | 0 | 0 |
| Airbridges needed | 0 | 0 |
| Minimum route clearance | 0.828 mm | 0.368 mm |
| Maximum graph degree | 2 | 4 |
| Graph diameter | 4 | 2 |
| DRC status | PASS | PASS |

## Interpretation

The Linear Chain is the safer first fabrication-development candidate because it has shorter total routing, a shorter longest-route proxy, larger route clearance, zero crossings, zero airbridges, and lower central congestion.

The Star topology has a smaller graph diameter and direct hub-to-leaf connectivity, so it is useful for GHZ-style or central-control workloads. However, it concentrates routing and coupling around Q1, has smaller route-clearance margin, and carries higher hub-density/crosstalk-risk proxy.

## Final recommendation

Recommend the **Linear Chain** as the first fabrication-development candidate under our route-length, clearance, and DRC metrics.

The **Star** topology remains preferred for experiments dominated by fixed hub-to-leaf interactions.
