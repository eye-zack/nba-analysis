import sys, os
import unittest
import pandas as pd
import yaml
from Testing.test_utils import add_project_root_to_path
# add project root to system path for module imports
add_project_root_to_path()

from backend.ML_training.predictions import load_data_from_db

# helper function to maintain model prefix
def get_latest_model_prefix(target, staging_dir):
    # list files in the directory which match the target
    matching_files = [
        f for f in os.listdir(staging_dir)
        if f.startswith(target) and f.endswith("_best_model.pkl")
    ]
    # raise error if no files are found
    if not matching_files:
        raise FileNotFoundError(f"No model files found for target '{target}' in {staging_dir}")
    # sort in descending order (latest file should be first)
    matching_files.sort(reverse=True)
    latest = matching_files[0]
    # removes last two aspects of the file name
    return "_".join(latest.split("_")[:-2])

"""
Set up class-level variables. This method is run once before any tests.
Loads configuration settings and prepares paths for the model directory and reference table.
"""
class TestPredictions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("config.yaml", "r") as f:
            cls.config = yaml.safe_load(f)

        # set paths for the model directory and reference table
        cls.targets = cls.config.get("targets", [])
        cls.model_dir = os.path.join(cls.config.get("output_dir", "models"), "staging")
        cls.ref_table = "historical_data_table"

    def test_model_artifacts_load(self):
        for target in self.targets:
            prefix = get_latest_model_prefix(target, self.model_dir)
            # define paths for model, scaler, and selector files
            model_path = os.path.join(self.model_dir, f"{prefix}_best_model.pkl")
            scaler_path = os.path.join(self.model_dir, f"{prefix}_scaler.pkl")
            selector_path = os.path.join(self.model_dir, f"{prefix}_selector.pkl")
            # checks that each file exists, raise error if not exists
            self.assertTrue(os.path.exists(model_path), f"Missing model for {target}")
            self.assertTrue(os.path.exists(scaler_path), f"Missing scaler for {target}")
            self.assertTrue(os.path.exists(selector_path), f"Missing selector for {target}")

    """
    Test that the reference data is loaded successfully from the database.
    It checks that the data is returned as a pandas DataFrame, is not empty,
    and contains the expected 'Player' column.
    """
    def test_reference_data_loads(self):
        df = load_data_from_db(self.ref_table)
        # assertion to validate the loaded data
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty, "Reference data should not be empty")
        self.assertIn("Player", df.columns, "Missing 'Player' column in reference data")


if __name__ == "__main__":
    unittest.main()
