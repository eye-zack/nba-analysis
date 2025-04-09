import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import pandas as pd
import yaml

from Testing.test_utils import add_project_root_to_path
add_project_root_to_path()

from backend.ML_training.predictions import (
    load_target_artifacts,
    load_data_from_db
)

class TestPredictions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("config.yaml", "r") as f:
            cls.config = yaml.safe_load(f)
        cls.targets = cls.config.get("targets", [])
        cls.model_dir = cls.config.get("output_dir", "models")
        cls.ref_table = "historical_data_table"

    def test_model_artifacts_load(self):
        for target in self.targets:
            model, scaler, selector = load_target_artifacts(target, model_dir=self.model_dir)
            self.assertIsNotNone(model, f"Model not loaded for {target}")
            self.assertIsNotNone(scaler, f"Scaler not loaded for {target}")
            self.assertIsNotNone(selector, f"Selector not loaded for {target}")

    def test_reference_data_loads(self):
        df = load_data_from_db(self.ref_table)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty, "Reference data should not be empty")
        self.assertIn("Player", df.columns, "Missing 'Player' column in reference data")

if __name__ == "__main__":
    unittest.main()
