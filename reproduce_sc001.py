import sys
import os
from datetime import date

# Add project root to path
sys.path.append('/Users/evanmounaud/Documents/Antigravity')

# Setup Django (needed if models/enums depend on it, though schemas might be standalone)
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.schemas import SimulationInput
from pydantic import ValidationError

sc001_input = {
    "matrimonial_regime": "SEPARATION",
    "assets": [
        {
            "id": "maison",
            "estimated_value": 500000,
            "ownership_mode": "FULL_OWNERSHIP",
            "asset_origin": "PERSONAL_PROPERTY"
        }
    ],
    "members": [
        {
            "id": "enfant1",
            "birth_date": "1990-01-01",
            "relationship": "CHILD",
            "is_from_current_union": True,
            "is_disabled": False
        }
    ],
    "wishes": {
        "has_spouse_donation": False,
        "testament_distribution": "LEGAL"
    }
}

try:
    sim = SimulationInput(**sc001_input)
    print("✅ Validation successful!")
    print(sim.model_dump_json(indent=2))
except ValidationError as e:
    print("❌ Validation failed!")
    print(e.json(indent=2))
except Exception as e:
    print(f"❌ Unexpected error: {e}")
