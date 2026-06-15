"""Order status workflow definitions and transitions."""

from enum import Enum


class OrderStatus(str, Enum):
    ORDER_PLACED = "Order Placed"
    PRESCRIPTION_VERIFIED = "Prescription Verified"
    LENS_ALLOCATED = "Lens Allocated"
    MANUFACTURING = "Manufacturing"
    QUALITY_CHECK = "Quality Check"
    QUALITY_CHECK_FAILED = "Quality Check Failed"
    REORDER_REQUIRED = "Reorder Required"
    DISPATCHED = "Dispatched"
    DELIVERED = "Delivered"


LENS_TYPES = ["Single Vision", "Bifocal", "Progressive", "Blue Cut", "Photochromic"]
LENS_INDICES = ["1.50", "1.56", "1.61", "1.67", "1.74"]
COATINGS = ["Anti-Reflective", "Blue Cut", "Scratch Resistant", "UV Protection", "Hydrophobic"]
STORE_LOCATIONS = ["HSR Layout", "Indiranagar", "Koramangala", "Whitefield", "Jayanagar"]

LENS_TYPE_SLA: dict[str, int] = {
    "Single Vision": 5,
    "Bifocal": 7,
    "Progressive": 10,
    "Blue Cut": 6,
    "Photochromic": 8,
}

VALID_TRANSITIONS: dict[str, list[str]] = {
    OrderStatus.ORDER_PLACED: [OrderStatus.PRESCRIPTION_VERIFIED],
    OrderStatus.PRESCRIPTION_VERIFIED: [OrderStatus.LENS_ALLOCATED],
    OrderStatus.LENS_ALLOCATED: [OrderStatus.MANUFACTURING],
    OrderStatus.MANUFACTURING: [OrderStatus.QUALITY_CHECK],
    OrderStatus.QUALITY_CHECK: [
        OrderStatus.DISPATCHED,
        OrderStatus.QUALITY_CHECK_FAILED,
    ],
    OrderStatus.QUALITY_CHECK_FAILED: [OrderStatus.REORDER_REQUIRED],
    OrderStatus.REORDER_REQUIRED: [OrderStatus.MANUFACTURING],
    OrderStatus.DISPATCHED: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
}


def can_transition(current: str, new_status: str) -> bool:
    return new_status in VALID_TRANSITIONS.get(current, [])


def default_sla_days(lens_type: str) -> int:
    return LENS_TYPE_SLA.get(lens_type, 7)


def get_valid_next_statuses(current: str) -> list[str]:
    return VALID_TRANSITIONS.get(current, [])
