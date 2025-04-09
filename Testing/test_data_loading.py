import unittest
from backend.ML_training.db_loader import load_data_from_rds
import pandas as pd

class TestDataLoading(unittest.TestCase):
    def setUp(self):
        self.df = load_data_from_rds()

    def test_data_is_not_empty(self):
        self.assertIsInstance(self.df, pd.DataFrame)
        self.assertFalse(self.df.empty, "Loaded DataFrame is empty")

    def test_removes_team_totals(self):
        self.assertNotIn("Team Totals", self.df["Player"].values, "Team Totals still present")

    def test_expected_columns_exist(self):
        expected_columns = {"Player", "TEAM", "3P", "3PA"}
        missing = expected_columns - set(self.df.columns)
        self.assertFalse(missing, f"Missing columns: {missing}")

    def test_no_nulls_in_important_columns(self):
        self.assertFalse(self.df["3P"].isnull().any(), "Nulls found in '3P'")
        self.assertFalse(self.df["3PA"].isnull().any(), "Nulls found in '3PA'")

if __name__ == "__main__":
    unittest.main()