"""Regression tests for cleaning and fault-detection rules."""
import os
import tempfile
import unittest

from pipeline import AnalyticsPipeline


class PipelineTestCase(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.pipeline = AnalyticsPipeline(self.path)
        self.pipeline.bootstrap()

    def tearDown(self):
        os.unlink(self.path)

    def test_dst_duplicate_intervals_are_not_counted_twice(self):
        """Each timestamp/zone pair appears only once in the zone-hour roll-up."""
        rows = self.pipeline.hourly_rows()
        studio_hour = [r for r in rows if r["zone"] == "Studio" and r["hour"] == "2026-01-11T01:00:00"]
        self.assertEqual(len(studio_hour), 1)
        self.assertEqual(studio_hour[0]["n"], 4)

    def test_sensor_gap_is_not_converted_to_zero_energy(self):
        """A missing Studio day is absent, preserving missingness for downstream use."""
        rows = self.pipeline.hourly_rows()
        gap = [r for r in rows if r["zone"] == "Studio" and r["hour"].startswith("2026-01-15")]
        self.assertEqual(gap, [])

    def test_cumulative_meter_reset_never_creates_negative_hourly_energy(self):
        rows = self.pipeline.hourly_rows()
        south = [r["kwh"] for r in rows if r["zone"] == "South Office"]
        self.assertTrue(all(value >= 0 for value in south))

    def test_simultaneous_heating_and_cooling_is_ranked_for_studio(self):
        _, stats, _ = self.pipeline.analyse()
        self.assertGreater(stats["Studio"]["heating_cooling"], 0)

    def test_after_hours_setback_failure_is_detected(self):
        _, stats, _ = self.pipeline.analyse()
        self.assertGreater(stats["North Office"]["setback"], 0)

    def test_unoccupied_energy_mismatch_is_detected(self):
        _, stats, _ = self.pipeline.analyse()
        self.assertGreater(stats["Meeting Room"]["occupancy"], 0)

    def test_dashboard_report_has_actionable_roi_fields(self):
        report = self.pipeline.report()
        self.assertEqual(len(report["zones"]), 4)
        self.assertGreater(report["total_cost"], 0)
        self.assertTrue(all(zone["payback"] > 0 for zone in report["zones"]))


if __name__ == "__main__":
    unittest.main()
