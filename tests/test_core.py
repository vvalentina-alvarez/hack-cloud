import os
import sys
import unittest

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("INCIDENTS_TABLE", "incidents")
os.environ.setdefault("ANTENNAS_TABLE", "antennas")
os.environ.setdefault("ZONE_TABLE", "zones")
os.environ.setdefault("CHAT_TABLE", "chat")
os.environ.setdefault("NOTIFICATIONS_TABLE", "notifications")
os.environ.setdefault("EVENT_BUS", "events")
os.environ.setdefault("CONFIG_SECRET_ARN", "config")
os.environ.setdefault("REPORTS_QUEUE_URL", "https://example.invalid/reports")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from api.create_report import build_report  # noqa: E402
from shared.common import TRANSITIONS, classify, geohash  # noqa: E402


class AntennaClassificationTests(unittest.TestCase):
    def test_exact_boundaries(self):
        cases = {
            0: "INHABILITADA",
            0.01: "CAIDA",
            59.99: "CAIDA",
            60: "NORMAL",
            129: "NORMAL",
            129.01: "SATURADA",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(classify(value), expected)


class ReportValidationTests(unittest.TestCase):
    def setUp(self):
        self.valid = {
            "documentId": "70000001",
            "serviceNumber": "999000001",
            "lat": -12.0464,
            "lon": -77.0428,
            "occurredAt": "2026-11-15T18:00:00Z",
            "problemType": "SIN_INTERNET",
            "description": "Sin conexion",
        }

    def test_valid_report(self):
        report, error = build_report(self.valid)
        self.assertIsNone(error)
        self.assertEqual(report["userId"], "70000001")

    def test_rejects_invalid_coordinates(self):
        report, error = build_report({**self.valid, "lat": 120})
        self.assertIsNone(report)
        self.assertIn("Coordenadas", error)

    def test_rejects_unknown_problem_type(self):
        report, error = build_report({**self.valid, "problemType": "DESCONOCIDO"})
        self.assertIsNone(report)
        self.assertIn("problemType", error)


class DomainModelTests(unittest.TestCase):
    def test_required_lifecycle(self):
        self.assertIn("EN_REVISION", TRANSITIONS["REGISTRADA"])
        self.assertIn("EN_ATENCION", TRANSITIONS["EN_REVISION"])
        self.assertIn("SOLUCIONADA", TRANSITIONS["EN_ATENCION"])
        self.assertIn("CERRADA", TRANSITIONS["SOLUCIONADA"])

    def test_zone_is_stable(self):
        self.assertEqual(geohash(-12.0464, -77.0428), geohash(-12.0464, -77.0428))


if __name__ == "__main__":
    unittest.main()
