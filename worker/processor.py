import logging
import uuid
from sqlalchemy.orm import Session

from src.models.device import Device
from src.models.vitals import Vitals

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {"ts", "d_id", "hr", "spo2", "bp_sys", "bp_dia", "bat"}

VALUE_RANGES = {
    "hr": (30, 250),
    "spo2": (50, 100),
    "bp_sys": (60, 250),
    "bp_dia": (40, 150),
    "bat": (0, 100),
}


def validate_payload(payload: dict) -> list[str]:
    errors = []

    missing = REQUIRED_KEYS - set(payload.keys())
    if missing:
        errors.append(f"Missing keys: {', '.join(sorted(missing))}")

    for key, (lo, hi) in VALUE_RANGES.items():
        val = payload.get(key)
        if val is not None and not (lo <= val <= hi):
            errors.append(
                f"{key}={val} out of range [{lo}, {hi}]"
            )

    return errors


def process_reading(db_session: Session, payload: dict) -> bool:
    errors = validate_payload(payload)
    if errors:
        for err in errors:
            logger.warning(f"Invalid payload: {err}")
        return False

    try:
        # Lookup or create device
        device = (
            db_session.query(Device)
            .filter_by(d_id=payload["d_id"])
            .first()
        )
        if device is None:
            device = Device(
                id=str(uuid.uuid4()),
                d_id=payload["d_id"],
                user_id=None,
            )
            db_session.add(device)
            db_session.flush()

        # Insert vitals record
        vitals = Vitals(
            id=str(uuid.uuid4()),
            device_id=device.id,
            ts=payload["ts"],
            hr=payload.get("hr"),
            spo2=payload.get("spo2"),
            bp_sys=payload.get("bp_sys"),
            bp_dia=payload.get("bp_dia"),
            bat=payload.get("bat"),
        )
        db_session.add(vitals)
        db_session.commit()
        return True

    except Exception as e:
        logger.error(f"DB error processing reading: {e}")
        db_session.rollback()
        return False
