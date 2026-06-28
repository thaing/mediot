from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.app.deps import get_current_user, get_db, get_device_api_key
from src.app.schemas.reading import ReadingIn, ReadingOut
from src.app.services.kafka_producer import KafkaException, get_producer
from src.models.device import Device
from src.models.user import User
from src.models.vitals import Vitals

router = APIRouter(prefix="/readings", tags=["readings"])


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_reading(
    payload: ReadingIn,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_device_api_key),
):
    try:
        producer = get_producer()
        producer.publish(
            topic="device-readings",
            key=payload.d_id,
            value=payload.model_dump(),
        )
        return {"status": "accepted", "ts": payload.ts}
    except KafkaException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get("/")
async def get_readings(
    d_id: str = Query(..., description="Device identifier"),
    from_ts: int | None = Query(None, description="Start timestamp"),
    to_ts: int | None = Query(None, description="End timestamp"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = db.query(Device).filter_by(d_id=d_id).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    if device.user_id is not None and device.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: device belongs to another user",
        )

    query = (
        db.query(Vitals)
        .filter(Vitals.device_id == device.id)
        .order_by(Vitals.ts.asc())
    )

    if from_ts is not None:
        query = query.filter(Vitals.ts >= from_ts)
    if to_ts is not None:
        query = query.filter(Vitals.ts <= to_ts)

    vitals = query.limit(1000).all()

    return [
        ReadingOut(
            id=v.id,
            ts=v.ts,
            d_id=d_id,
            hr=v.hr,
            spo2=v.spo2,
            bp_sys=v.bp_sys,
            bp_dia=v.bp_dia,
            bat=v.bat,
            recorded_at=v.recorded_at.isoformat() if v.recorded_at else None,
        )
        for v in vitals
    ]
