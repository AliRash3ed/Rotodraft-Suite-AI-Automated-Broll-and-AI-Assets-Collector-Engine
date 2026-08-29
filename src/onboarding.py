import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LEADS_FILE = DATA_DIR / "leads.json"

class OnboardingManager:
    """Manages creator onboarding and lead capture vault."""

    @classmethod
    def load_leads(cls) -> List[Dict[str, Any]]:
        if LEADS_FILE.exists():
            try:
                with open(LEADS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    @classmethod
    def register_lead(cls, name: str, email: str, whatsapp: str = "") -> Dict[str, Any]:
        leads = cls.load_leads()
        record = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "whatsapp": whatsapp.strip(),
            "timestamp": datetime.now().isoformat(),
            "source": "stock_media_collector_pro"
        }
        
        # Avoid duplicate emails
        leads = [l for l in leads if l.get("email") != record["email"]]
        leads.append(record)

        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)

        return {"success": True, "message": "Lead registered successfully.", "lead": record}

    @classmethod
    def is_onboarded(cls) -> bool:
        leads = cls.load_leads()
        return len(leads) > 0
