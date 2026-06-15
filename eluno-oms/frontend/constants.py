"""Shared UI constants (mirrors backend workflow config)."""

LENS_TYPES = ["Single Vision", "Bifocal", "Progressive", "Blue Cut", "Photochromic"]
LENS_INDICES = ["1.50", "1.56", "1.61", "1.67", "1.74"]
COATINGS = ["Anti-Reflective", "Blue Cut", "Scratch Resistant", "UV Protection", "Hydrophobic"]
STORE_LOCATIONS = ["HSR Layout", "Indiranagar", "Koramangala", "Whitefield", "Jayanagar"]

ORDER_STATUSES = [
    "Order Placed",
    "Prescription Verified",
    "Lens Allocated",
    "Manufacturing",
    "Quality Check",
    "Quality Check Failed",
    "Reorder Required",
    "Dispatched",
    "Delivered",
]

VALID_TRANSITIONS = {
    "Order Placed": ["Prescription Verified"],
    "Prescription Verified": ["Lens Allocated"],
    "Lens Allocated": ["Manufacturing"],
    "Manufacturing": ["Quality Check"],
    "Quality Check": ["Dispatched", "Quality Check Failed"],
    "Quality Check Failed": ["Reorder Required"],
    "Reorder Required": ["Manufacturing"],
    "Dispatched": ["Delivered"],
    "Delivered": [],
}


def get_valid_next_statuses(current: str) -> list[str]:
    return VALID_TRANSITIONS.get(current, [])
