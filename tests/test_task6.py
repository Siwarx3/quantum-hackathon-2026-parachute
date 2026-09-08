"""Unit and regression tests for Task 6 comparative synthesis and recommendation."""

import unittest
from pathlib import Path
import pandas as pd

from src.task6_synthesis import (
    graph_diameter,
    average_shortest_path,
    build_task6_synthesis,
    write_task6_recommendation,
)


class TestTask6Synthesis(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def test_graph_theory_metrics(self):
        """Verify graph diameter and average shortest path calculations for 5 qubits."""
        # Linear chain: 0-1-2-3-4
        self.assertEqual(graph_diameter("linear"), 4)
        self.assertAlmostEqual(average_shortest_path("linear"), 2.0)

        # Star hub: 0 connected to 1,2,3,4
        self.assertEqual(graph_diameter("star"), 2)
        self.assertAlmostEqual(average_shortest_path("star"), 1.6)

    def test_task6_synthesis_builder(self):
        """Test build_task6_synthesis with synthetic data to verify structure."""
        best_df = pd.DataFrame([
            {
                "topology": "linear",
                "layout_parameter_mm": 1.2,
                "total_route_length_mm": 1.40,
                "longest_route_mm": 0.35,
                "crossings": 0,
                "min_route_clearance_mm": 0.828,
                "drc_violations": 0,
            },
            {
                "topology": "star",
                "layout_parameter_mm": 1.5,
                "total_route_length_mm": 3.356,
                "longest_route_mm": 0.839,
                "crossings": 0,
                "min_route_clearance_mm": 0.368,
                "drc_violations": 0,
            }
        ])

        em_df = pd.DataFrame([
            {
                "topology": "linear",
                "crossing_airbridges_needed": 0,
                "crosstalk_risk_proxy": "lower: distributed local routing",
                "resonator_interpretation": "linear interpretation",
            },
            {
                "topology": "star",
                "crossing_airbridges_needed": 0,
                "crosstalk_risk_proxy": "watch: close-route geometric crosstalk risk",
                "resonator_interpretation": "star interpretation",
            }
        ])

        synthesis_df = build_task6_synthesis(best_df, em_df)
        self.assertEqual(len(synthesis_df), 2)

        required_columns = [
            "topology",
            "selected_layout_parameter_mm",
            "number_of_qubits",
            "number_of_edges",
            "max_degree",
            "graph_diameter",
            "average_shortest_path",
            "total_route_length_mm",
            "longest_route_or_weakest_path_proxy_mm",
            "crossings",
            "airbridges_needed",
            "min_route_clearance_mm",
            "drc_status",
            "crosstalk_risk_proxy",
            "workload_fit",
            "fabrication_recommendation_role",
            "final_fabrication_recommendation",
        ]
        for col in required_columns:
            self.assertIn(col, synthesis_df.columns, f"Missing column: {col}")

        linear_row = synthesis_df[synthesis_df["topology"] == "linear"].iloc[0]
        star_row = synthesis_df[synthesis_df["topology"] == "star"].iloc[0]

        self.assertEqual(linear_row["drc_status"], "PASS")
        self.assertEqual(star_row["drc_status"], "PASS")
        self.assertEqual(linear_row["crossings"], 0)
        self.assertEqual(star_row["crossings"], 0)
        self.assertEqual(linear_row["airbridges_needed"], 0)
        self.assertEqual(star_row["airbridges_needed"], 0)
        self.assertEqual(linear_row["max_degree"], 2)
        self.assertEqual(star_row["max_degree"], 4)

    def test_task6_artifacts_exist_and_consistent(self):
        """Verify the generated Task-6 CSV and Markdown files exist and match."""
        csv_path = self.root / "results" / "task6_synthesis.csv"
        md_path = self.root / "reports" / "task6_recommendation.md"

        self.assertTrue(csv_path.exists(), f"{csv_path} does not exist")
        self.assertTrue(md_path.exists(), f"{md_path} does not exist")

        df = pd.read_csv(csv_path)
        self.assertEqual(set(df["topology"]), {"linear", "star"})
        self.assertTrue((df["drc_status"] == "PASS").all())
        self.assertTrue((df["crossings"] == 0).all())
        self.assertTrue((df["airbridges_needed"] == 0).all())

        md_content = md_path.read_text()
        self.assertIn("Task 6 — Comparative Synthesis and Recommendation", md_content)
        self.assertIn("Recommend the **Linear Chain**", md_content)
        self.assertIn("The **Star** topology remains preferred", md_content)


if __name__ == "__main__":
    unittest.main()
