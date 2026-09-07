import unittest
import pandas as pd
from src.optimizer import best_by_topology, best_overall
from src.geometry_metrics import segments_intersect, segment_distance
from src.drc_check import edge_to_edge_gap


class RegressionTests(unittest.TestCase):
    def test_infeasible_candidate_cannot_win(self):
        df = pd.DataFrame([dict(topology='star',cost=0,drc_violations=1),
                           dict(topology='star',cost=.8,drc_violations=0),
                           dict(topology='linear',cost=.4,drc_violations=0)])
        self.assertTrue((best_by_topology(df).drc_violations == 0).all())
        self.assertEqual(best_overall(df).topology,'linear')

    def test_no_feasible_candidate_is_explicit(self):
        with self.assertRaisesRegex(ValueError,'No DRC-feasible'):
            best_overall(pd.DataFrame([dict(topology='star',cost=0,drc_violations=1)]))

    def test_crossings_and_collinear_overlap(self):
        self.assertTrue(segments_intersect((0,0),(1,1),(0,1),(1,0)))
        self.assertTrue(segments_intersect((0,0),(2,0),(1,0),(3,0)))
        self.assertAlmostEqual(segment_distance((0,0),(1,0),(0,2),(1,2)),2)

    def test_pocket_spacing_uses_edges(self):
        self.assertAlmostEqual(edge_to_edge_gap((0,0,1,1),(1.2,0,2.2,1)),.2)
        self.assertLess(edge_to_edge_gap((0,0,1,1),(.5,.5,1.5,1.5)),0)


if __name__ == '__main__':
    unittest.main()
