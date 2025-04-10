import unittest
import os
import yaml
from backend.ML_training.training_program import train_and_save_models
from db_loader import load_data_from_rds
from backend.ML_training.predictions import get_latest_model_prefix

# Test class for validating model training, file existence, and output directory contents
class TestModelTraining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run once before all tests.
        # add more target variables to config.yaml to test on more variables.
        with open("config.yaml", "r") as file:
            cls.config = yaml.safe_load(file)
        cls.output_dir = cls.config.get("output_dir", "models")
        cls.staging_dir = os.path.join(cls.output_dir, "staging")
        cls.targets = cls.config.get("targets", [])
        cls.df = load_data_from_rds()
        cls.model_dir = os.path.join(cls.output_dir, "staging")

        # Ensure models directory exists
        os.makedirs(cls.output_dir, exist_ok=True)

        # Run the training once for all test methods
        train_and_save_models(cls.df, cls.config)

    def test_model_files_exist(self):
        for target in self.targets:
            prefix = get_latest_model_prefix(target, self.model_dir)
            for suffix in ["_best_model.pkl", "_scaler.pkl", "_selector.pkl"]:
                model_path = os.path.join(self.model_dir, f"{prefix}{suffix}")
                self.assertTrue(os.path.exists(model_path), f"Missing model file: {model_path}")

    def test_model_output_dir_not_empty(self):
        # Make sure that the output directory isn't empty.
        files = os.listdir(self.output_dir)
        self.assertTrue(len(files) > 0, "Model output directory is empty")

    @classmethod
    def tearDownClass(cls):
        # Clean up model files after tests.
        cleanup = False  # Set to True to auto-delete generated files
        if cleanup:
            for target in cls.targets:
                for suffix in ["best_model.pkl", "scaler.pkl", "selector.pkl"]:
                    path = os.path.join(cls.output_dir, f"{target}_{suffix}")
                    if os.path.exists(path):
                        os.remove(path)

if __name__ == "__main__":
    unittest.main()
