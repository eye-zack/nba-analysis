import logging
from dotenv import load_dotenv
import yaml
from db_loader import load_data_from_rds
from training_program import train_and_save_models
import os

def main():
    load_dotenv()
    required_env_vars = ["DB_USER", "DB_PASS", "DB_HOST"]
    missing = [var for var in required_env_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing critical environment variables: {', '.join(missing)}")

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    logging.info("Starting ML training pipeline...")

    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    df = load_data_from_rds()
    train_and_save_models(df, config)

    logging.info("Pipeline complete.")

if __name__ == "__main__":
    main()