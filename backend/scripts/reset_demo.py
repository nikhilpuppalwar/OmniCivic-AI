"""
OmniCivic AI -- Reset Demo Script
Restores all data to pre-demo state in one command.
Run: python -m backend.scripts.reset_demo (from project root)
Also exposed as POST /dev/reset-demo API route.
"""

import json
import os
import sys

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.seed_data import generate_seed_data

DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")


def reset_demo():
    """Reset all data to pre-demo state."""
    print("[RESET] Resetting OmniCivic AI demo data...\n")

    # Regenerate all seed data
    generate_seed_data()

    # Clear uploads directory (keep seed_images intact)
    if os.path.exists(UPLOADS_DIR):
        for f in os.listdir(UPLOADS_DIR):
            filepath = os.path.join(UPLOADS_DIR, f)
            if os.path.isfile(filepath) and f != ".gitkeep":
                os.remove(filepath)
        print("[OK] Cleared uploads directory")
    else:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        print("[OK] Created uploads directory")

    print("\n=== Demo reset complete. Ready for presentation. ===")
    print("   Run the demo script from Section 9 of the spec.")
    print("   Start with: POST /reports (water leakage seed report)")


if __name__ == "__main__":
    reset_demo()
