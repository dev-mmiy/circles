"""
FastAPI local dev stub for a rare-disease community MVP (no auth)
- Tech: FastAPI + SQLModel (SQLite)
- Features:
  * Journals (daily logs with optional symptom entries)
  * Medications + intake logs
  * Groups + Posts (basic community)
  * Reports (content moderation: report posts)
- Notes:
  * No authentication. Treat all data as public in this stub.
  * CORS is open for http://localhost and http://127.0.0.1 for local dev.
  * Safe for local prototyping only. Do not use in production.

Run locally:
  uvicorn app:app --reload

Install deps (example):
  pip install fastapi==0.111.0 uvicorn[standard]==0.30.1 sqlmodel==0.0.21 pydantic==2.*
"""
from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField, Relationship, create_engine, Session, select

# ----------------------------------------------------------------------------
# Database setup
# ----------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


# ----------------------------------------------------------------------------
# Models (SQLModel)
# ----------------------------------------------------------------------------
class JournalSymptom(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    journal_id: int = SQLField(foreign_key="journal.id")
    name: str
    score: int = SQLField(ge=0, le=10)


class Journal(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    log_date: date = SQLField(index=True, default_factory=lambda: datetime.utcnow().date())
    note: Optional[str] = None
    weight_kg: Optional[float] = SQLField(default=None, ge=0)
    systolic_bp: Optional[int] = SQLField(default=None, ge=0)
    diastolic_bp: Optional[int] = SQLField(default=None, ge=0)
    mood: Optional[int] = SQLField(default=None, ge=0, le=10)

    symptoms: List[JournalSymptom] = Relationship(back_populates="journal")


JournalSymptom.journal = Relationship(back_populates="symptoms", sa_relationship_kwargs={"lazy": "joined"})


class Medication(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    dosage: Optional[str] = None  # e.g., "5 mg"
    schedule: Optional[str] = None  # free text for stub (e.g., "8:00, 20:00 daily")

    logs: List[MedicationLog] = Relationship(back_populates="medication")


class MedicationLog(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    medication_id: int = SQLField(foreign_key="medication.id")
    taken_at: datetime = SQLField(default_factory=datetime.utcnow, index=True)
    status: str = SQLField(default="taken")  # taken / missed / delayed (free text for stub)


MedicationLog.medication = Relationship(back_populates="logs")


class GroupVisibility(str, Enum):
    public = "public"
    private = "private"  # stub only; no auth/ACL enforced


class Group(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    visibility: GroupVisibility = SQLField(default=GroupVisibility.public)

    posts: List[Post] = Relationship(back_populates="group")


class Post(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    group_id: int = SQLField(foreign_key="group.id")
    created_at: datetime = SQLField(default_factory=datetime.utcnow, index=True)
    title: str
    body: str
    anon: bool = SQLField(default=True)

    group: Optional[Group] = Relationship(back_populates="posts")


class ReportTargetType(str, Enum):
    post = "post"


class ReportReason(str, Enum):
    abuse = "abuse"
    medical_misinformation = "medical_misinformation"
    spam = "spam"
    other = "other"


class Report(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    target_type: ReportTargetType
    target_id: int
    reason: ReportReason = SQLField(default=ReportReason.other)
    detail: Optional[str] = None
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    status: str = SQLField(default="open")  # open / reviewed / actioned


# ----------------------------------------------------------------------------
# Schemas (Pydantic request/response)
# ----------------------------------------------------------------------------
class SymptomIn(BaseModel):
    name: str
    score: int = Field(ge=0, le=10)


class JournalCreate(BaseModel):
    log_date: Optional[date] = None
    note: Optional[str] = None
    weight_kg: Optional[float] = Field(default=None, ge=0)
    systolic_bp: Optional[int] = Field(default=None, ge=0)
    diastolic_bp: Optional[int] = Field(default=None, ge=0)
    mood: Optional[int] = Field(default=None, ge=0, le=10)
    symptoms: List[SymptomIn] = []


class JournalRead(BaseModel):
    id: int
    log_date: date
    note: Optional[str]
    weight_kg: Optional[float]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    mood: Optional[int]
    symptoms: List[SymptomIn]

    class Config:
        from_attributes = True


class MedicationCreate(BaseModel):
    name: str
    dosage: Optional[str] = None
    schedule: Optional[str] = None


class MedicationRead(BaseModel):
    id: int
    name: str
    dosage: Optional[str]
    schedule: Optional[str]

    class Config:
        from_attributes = True


class MedicationLogCreate(BaseModel):
    status: Optional[str] = Field(default="taken")
    taken_at: Optional[datetime] = None


class MedicationLogRead(BaseModel):
    id: int
    medication_id: int
    status: str
    taken_at: datetime

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    visibility: GroupVisibility = GroupVisibility.public


class GroupRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    visibility: GroupVisibility

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    group_id: int
    title: str
    body: str
    anon: bool = True


class PostRead(BaseModel):
    id: int
    group_id: int
    created_at: datetime
    title: str
    body: str
    anon: bool

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    target_type: ReportTargetType
    target_id: int
    reason: ReportReason = ReportReason.other
    detail: Optional[str] = None


class ReportRead(BaseModel):
    id: int
    target_type: ReportTargetType
    target_id: int
    reason: ReportReason
    detail: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------------------------------------------------------
# FastAPI app
# ----------------------------------------------------------------------------
app = FastAPI(title="Rare Community Dev Stub (no-auth)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# ----------------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}


# ----------------------------------------------------------------------------
# Journals
# ----------------------------------------------------------------------------
@app.post("/journals", response_model=JournalRead)
def create_journal(payload: JournalCreate, session: Session = Depends(get_session)):
    journal = Journal(
        log_date=payload.log_date or datetime.utcnow().date(),
        note=payload.note,
        weight_kg=payload.weight_kg,
        systolic_bp=payload.systolic_bp,
        diastolic_bp=payload.diastolic_bp,
        mood=payload.mood,
    )
    session.add(journal)
    session.flush()  # to get journal.id

    for s in payload.symptoms:
        session.add(JournalSymptom(journal_id=journal.id, name=s.name, score=s.score))

    session.commit()
    session.refresh(journal)

    return JournalRead(
        id=journal.id,
        log_date=journal.log_date,
        note=journal.note,
        weight_kg=journal.weight_kg,
        systolic_bp=journal.systolic_bp,
        diastolic_bp=journal.diastolic_bp,
        mood=journal.mood,
        symptoms=[SymptomIn(name=s.name, score=s.score) for s in journal.symptoms],
    )


@app.get("/journals", response_model=List[JournalRead])
def list_journals(
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    stmt = select(Journal).order_by(Journal.log_date.desc(), Journal.id.desc())
    if date_from:
        stmt = stmt.where(Journal.log_date >= date_from)
    if date_to:
        stmt = stmt.where(Journal.log_date <= date_to)
    stmt = stmt.offset(offset).limit(limit)

    rows = session.exec(stmt).all()
    out: List[JournalRead] = []
    for j in rows:
        out.append(
            JournalRead(
                id=j.id,
                log_date=j.log_date,
                note=j.note,
                weight_kg=j.weight_kg,
                systolic_bp=j.systolic_bp,
                diastolic_bp=j.diastolic_bp,
                mood=j.mood,
                symptoms=[SymptomIn(name=s.name, score=s.score) for s in j.symptoms],
            )
        )
    return out


@app.get("/journals/{journal_id}", response_model=JournalRead)
def get_journal(journal_id: int, session: Session = Depends(get_session)):
    j = session.get(Journal, journal_id)
    if not j:
        raise HTTPException(404, "Journal not found")
    return JournalRead(
        id=j.id,
        log_date=j.log_date,
        note=j.note,
        weight_kg=j.weight_kg,
        systolic_bp=j.systolic_bp,
        diastolic_bp=j.diastolic_bp,
        mood=j.mood,
        symptoms=[SymptomIn(name=s.name, score=s.score) for s in j.symptoms],
    )


@app.delete("/journals/{journal_id}")
def delete_journal(journal_id: int, session: Session = Depends(get_session)):
    j = session.get(Journal, journal_id)
    if not j:
        raise HTTPException(404, "Journal not found")
    session.delete(j)
    session.commit()
    return {"deleted": journal_id}


# ----------------------------------------------------------------------------
# Medications
# ----------------------------------------------------------------------------
@app.post("/medications", response_model=MedicationRead)
def create_medication(payload: MedicationCreate, session: Session = Depends(get_session)):
    m = Medication(name=payload.name, dosage=payload.dosage, schedule=payload.schedule)
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


@app.get("/medications", response_model=List[MedicationRead])
def list_medications(session: Session = Depends(get_session)):
    rows = session.exec(select(Medication).order_by(Medication.id.desc())).all()
    return rows


@app.post("/medications/{medication_id}/log", response_model=MedicationLogRead)
def log_medication(medication_id: int, payload: MedicationLogCreate, session: Session = Depends(get_session)):
    m = session.get(Medication, medication_id)
    if not m:
        raise HTTPException(404, "Medication not found")
    log = MedicationLog(
        medication_id=medication_id,
        status=payload.status or "taken",
        taken_at=payload.taken_at or datetime.utcnow(),
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@app.get("/medications/{medication_id}/logs", response_model=List[MedicationLogRead])
def list_medication_logs(medication_id: int, session: Session = Depends(get_session)):
    m = session.get(Medication, medication_id)
    if not m:
        raise HTTPException(404, "Medication not found")
    rows = session.exec(select(MedicationLog).where(MedicationLog.medication_id == medication_id).order_by(MedicationLog.taken_at.desc(), MedicationLog.id.desc())).all()
    return rows


# ----------------------------------------------------------------------------
# Groups & Posts
# ----------------------------------------------------------------------------
@app.post("/groups", response_model=GroupRead)
def create_group(payload: GroupCreate, session: Session = Depends(get_session)):
    g = Group(name=payload.name, description=payload.description, visibility=payload.visibility)
    session.add(g)
    session.commit()
    session.refresh(g)
    return g


@app.get("/groups", response_model=List[GroupRead])
def list_groups(session: Session = Depends(get_session)):
    rows = session.exec(select(Group).order_by(Group.id.desc())).all()
    return rows


@app.post("/posts", response_model=PostRead)
def create_post(payload: PostCreate, session: Session = Depends(get_session)):
    g = session.get(Group, payload.group_id)
    if not g:
        raise HTTPException(404, "Group not found")
    p = Post(group_id=payload.group_id, title=payload.title, body=payload.body, anon=payload.anon)
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


@app.get("/groups/{group_id}/posts", response_model=List[PostRead])
def list_posts(group_id: int, session: Session = Depends(get_session)):
    g = session.get(Group, group_id)
    if not g:
        raise HTTPException(404, "Group not found")
    rows = session.exec(select(Post).where(Post.group_id == group_id).order_by(Post.created_at.desc(), Post.id.desc())).all()
    return rows


# ----------------------------------------------------------------------------
# Reports (for moderation)
# ----------------------------------------------------------------------------
@app.post("/reports", response_model=ReportRead)
def create_report(payload: ReportCreate, session: Session = Depends(get_session)):
    # Minimal validation for stub: ensure target exists for posts
    if payload.target_type == ReportTargetType.post:
        target = session.get(Post, payload.target_id)
        if not target:
            raise HTTPException(404, "Target post not found")
    r = Report(
        target_type=payload.target_type,
        target_id=payload.target_id,
        reason=payload.reason,
        detail=payload.detail,
    )
    session.add(r)
    session.commit()
    session.refresh(r)
    return r


@app.get("/reports", response_model=List[ReportRead])
def list_reports(
    session: Session = Depends(get_session),
    status: Optional[str] = None,
    reason: Optional[ReportReason] = None,
):
    stmt = select(Report).order_by(Report.created_at.desc(), Report.id.desc())
    if status:
        stmt = stmt.where(Report.status == status)
    if reason:
        stmt = stmt.where(Report.reason == reason)
    rows = session.exec(stmt).all()
    return rows


# ----------------------------------------------------------------------------
# Dev utilities (optional)
# ----------------------------------------------------------------------------
@app.post("/dev/seed")
def dev_seed(session: Session = Depends(get_session)):
    """Create a sample group for quick testing."""
    g = Group(name="General", description="General discussion for the community")
    session.add(g)
    session.commit()
    session.refresh(g)
    return {"group_id": g.id}
