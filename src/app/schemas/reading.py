from pydantic import BaseModel, Field


class ReadingIn(BaseModel):
    ts: int
    d_id: str
    hr: int = Field(ge=30, le=250)
    spo2: int = Field(ge=50, le=100)
    bp_sys: int = Field(ge=60, le=250)
    bp_dia: int = Field(ge=40, le=150)
    bat: int = Field(ge=0, le=100)


class ReadingOut(BaseModel):
    id: str
    ts: int
    d_id: str
    hr: int | None = None
    spo2: int | None = None
    bp_sys: int | None = None
    bp_dia: int | None = None
    bat: int | None = None
    recorded_at: str | None = None

    class Config:
        from_attributes = True
