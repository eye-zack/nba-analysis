# This script automates moving the latest models from staging to production.
# run using python promote_models.py

import os
import shutil
import yaml
import re

def get_latest_versioned_prefix(target, staging_dir):
    pattern = re.compile(rf"^{target}_v(\d+)_\d{{8}}_\d{{4}}_best_model\.pkl$")
    max_version = -1
    latest_prefix = None

    for fname in os.listdir(staging_dir):
        match = pattern.match(fname)
        if match:
            version = int(match.group(1))
            if version > max_version:
                max_version = version
                # remove the _best_model.pkl part
                latest_prefix = fname.replace("_best_model.pkl", "")

    return latest_prefix

def promote_models():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    targets = config.get("targets", [])
    base_dir = config.get("output_dir", "models")
    staging_dir = "backend/ML_training/models/staging"
    production_dir = "backend/ML_training/models/production"
    os.makedirs(production_dir, exist_ok=True)

    print("\nPromoting latest versioned models from staging to production...\n")

    for target in targets:
        prefix = get_latest_versioned_prefix(target, staging_dir)
        if not prefix:
            print(f"No versions found for target '{target}' — skipped.")
            continue

        for suffix in ["best_model.pkl", "scaler.pkl", "selector.pkl", "json"]:
            versioned_filename = f"{prefix}_{suffix}"
            cleaned_filename = f"{target}_{suffix}"

            src = os.path.join(staging_dir, versioned_filename)
            dst = os.path.join(production_dir, cleaned_filename)

            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"Promoted: {cleaned_filename}")
            else:
                print(f"Missing file: {versioned_filename} (skipped)")

    print("\nPromotion complete.\n")

if __name__ == "__main__":
    promote_models()
