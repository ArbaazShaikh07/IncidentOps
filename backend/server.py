from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

class IncidentType(str, Enum):
    failure_spike = "failure_spike"
    bank_outage = "bank_outage"
    merchant_complaint = "merchant_complaint"

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class IncidentStatus(str, Enum):
    open = "open"
    under_audit = "under_audit"
    closed = "closed"

class AuditStatus(str, Enum):
    in_progress = "in_progress"
    awaiting_action = "awaiting_action"
    closed = "closed"

class AuditOwner(str, Enum):
    Ops = "Ops"
    Product = "Product"
    Tech = "Tech"

class ChecklistResponse(str, Enum):
    yes = "yes"
    no = "no"
    not_applicable = "not_applicable"
    pending = "pending"

class FindingCategory(str, Enum):
    process_gap = "process_gap"
    tech_issue = "tech_issue"
    bank_issue = "bank_issue"
    monitoring_gap = "monitoring_gap"

class ActionStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"

class OwnerTeam(str, Enum):
    BankOps = "Bank Ops"
    Engineering = "Engineering"
    Product = "Product"

class PaymentIncident(BaseModel):
    model_config = ConfigDict(extra="ignore")
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_type: IncidentType
    detected_at: str
    affected_bank: str
    payment_method: str
    severity: Severity
    status: IncidentStatus

class AuditCase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    audit_owner: AuditOwner
    audit_start_date: str
    audit_status: AuditStatus
    summary: Optional[str] = ""

class AuditChecklistItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    checklist_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str
    question: str
    response: ChecklistResponse = ChecklistResponse.pending
    evidence_link: Optional[str] = ""

class AuditFinding(BaseModel):
    model_config = ConfigDict(extra="ignore")
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str
    category: FindingCategory
    description: str
    severity: Severity
    evidence_reference: Optional[str] = ""

class ActionItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    finding_id: str
    action_description: str
    owner_team: OwnerTeam
    due_date: str
    status: ActionStatus

class ClosureValidation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    audit_id: str
    validation_done: bool
    validation_notes: str
    validated_by: str
    validated_at: str

class ChecklistUpdateRequest(BaseModel):
    checklist_id: str
    response: ChecklistResponse
    evidence_link: Optional[str] = ""

class FindingCreateRequest(BaseModel):
    audit_id: str
    category: FindingCategory
    description: str
    severity: Severity
    evidence_reference: Optional[str] = ""

class ActionCreateRequest(BaseModel):
    finding_id: str
    audit_id: str
    action_description: str
    owner_team: OwnerTeam
    due_date: str

class ActionUpdateRequest(BaseModel):
    action_id: str
    status: ActionStatus

class ValidationRequest(BaseModel):
    audit_id: str
    validation_notes: str
    validated_by: str

async def seed_data():
    count = await db.incidents.count_documents({})
    if count > 0:
        return
    
    logger.info("Seeding database with initial data...")
    
    banks = ["HDFC Bank", "ICICI Bank", "Axis Bank", "SBI", "Kotak Mahindra", "Yes Bank", "IDFC First"]
    payment_methods = ["UPI", "NEFT", "IMPS", "Credit Card", "Debit Card", "Net Banking"]
    
    incidents_data = [
        {
            "incident_type": "failure_spike",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
            "affected_bank": "HDFC Bank",
            "payment_method": "UPI",
            "severity": "critical",
            "status": "closed"
        },
        {
            "incident_type": "bank_outage",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=12)).isoformat(),
            "affected_bank": "ICICI Bank",
            "payment_method": "IMPS",
            "severity": "high",
            "status": "closed"
        },
        {
            "incident_type": "merchant_complaint",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
            "affected_bank": "Axis Bank",
            "payment_method": "Credit Card",
            "severity": "medium",
            "status": "under_audit"
        },
        {
            "incident_type": "failure_spike",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
            "affected_bank": "SBI",
            "payment_method": "Net Banking",
            "severity": "high",
            "status": "under_audit"
        },
        {
            "incident_type": "bank_outage",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            "affected_bank": "Kotak Mahindra",
            "payment_method": "UPI",
            "severity": "critical",
            "status": "under_audit"
        },
        {
            "incident_type": "merchant_complaint",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
            "affected_bank": "Yes Bank",
            "payment_method": "NEFT",
            "severity": "low",
            "status": "open"
        },
        {
            "incident_type": "failure_spike",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
            "affected_bank": "HDFC Bank",
            "payment_method": "Debit Card",
            "severity": "medium",
            "status": "open"
        },
        {
            "incident_type": "bank_outage",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
            "affected_bank": "ICICI Bank",
            "payment_method": "UPI",
            "severity": "high",
            "status": "under_audit"
        },
        {
            "incident_type": "failure_spike",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
            "affected_bank": "Axis Bank",
            "payment_method": "IMPS",
            "severity": "critical",
            "status": "under_audit"
        },
        {
            "incident_type": "merchant_complaint",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
            "affected_bank": "SBI",
            "payment_method": "Credit Card",
            "severity": "medium",
            "status": "open"
        },
        {
            "incident_type": "bank_outage",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
            "affected_bank": "IDFC First",
            "payment_method": "UPI",
            "severity": "high",
            "status": "closed"
        },
        {
            "incident_type": "failure_spike",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=18)).isoformat(),
            "affected_bank": "HDFC Bank",
            "payment_method": "Net Banking",
            "severity": "medium",
            "status": "closed"
        },
        {
            "incident_type": "merchant_complaint",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=16)).isoformat(),
            "affected_bank": "Kotak Mahindra",
            "payment_method": "Debit Card",
            "severity": "low",
            "status": "under_audit"
        },
        {
            "incident_type": "failure_spike",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=14)).isoformat(),
            "affected_bank": "Yes Bank",
            "payment_method": "NEFT",
            "severity": "high",
            "status": "closed"
        },
        {
            "incident_type": "bank_outage",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=13)).isoformat(),
            "affected_bank": "ICICI Bank",
            "payment_method": "UPI",
            "severity": "critical",
            "status": "closed"
        },
        {
            "incident_type": "merchant_complaint",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=11)).isoformat(),
            "affected_bank": "Axis Bank",
            "payment_method": "IMPS",
            "severity": "medium",
            "status": "open"
        },
        {
            "incident_type": "failure_spike",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=9)).isoformat(),
            "affected_bank": "SBI",
            "payment_method": "Credit Card",
            "severity": "high",
            "status": "under_audit"
        },
        {
            "incident_type": "bank_outage",
            "detected_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "affected_bank": "HDFC Bank",
            "payment_method": "UPI",
            "severity": "critical",
            "status": "open"
        },
        {
            "incident_type": "merchant_complaint",
            "detected_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
            "affected_bank": "ICICI Bank",
            "payment_method": "Net Banking",
            "severity": "low",
            "status": "open"
        },
        {
            "incident_type": "failure_spike",
            "detected_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "affected_bank": "Kotak Mahindra",
            "payment_method": "Debit Card",
            "severity": "medium",
            "status": "open"
        }
    ]
    
    for incident_data in incidents_data:
        incident = PaymentIncident(**incident_data)
        await db.incidents.insert_one(incident.model_dump())
        
        audit = AuditCase(
            incident_id=incident.incident_id,
            audit_owner=AuditOwner.Ops if incident.incident_type == "failure_spike" else (AuditOwner.Tech if incident.incident_type == "bank_outage" else AuditOwner.Product),
            audit_start_date=incident.detected_at,
            audit_status=AuditStatus.closed if incident.status == "closed" else AuditStatus.in_progress,
            summary=f"Audit for {incident.incident_type} on {incident.affected_bank}"
        )
        await db.audits.insert_one(audit.model_dump())
        
        checklist_questions = [
            "Was the incident detected within SLA timeframe?",
            "Were all stakeholders notified promptly?",
            "Was root cause analysis completed?",
            "Were impacted transactions identified?",
            "Was customer communication sent out?",
            "Were monitoring alerts functioning correctly?",
            "Has preventive action been identified?"
        ]
        
        for question in checklist_questions[:6]:
            checklist_item = AuditChecklistItem(
                audit_id=audit.audit_id,
                question=question,
                response=ChecklistResponse.yes if audit.audit_status == AuditStatus.closed else ChecklistResponse.pending
            )
            await db.checklist.insert_one(checklist_item.model_dump())
        
        if audit.audit_status == AuditStatus.closed:
            finding = AuditFinding(
                audit_id=audit.audit_id,
                category=FindingCategory.tech_issue if incident.incident_type == "bank_outage" else FindingCategory.process_gap,
                description=f"Root cause identified for {incident.incident_type}",
                severity=incident.severity,
                evidence_reference="Internal logs and monitoring data"
            )
            await db.findings.insert_one(finding.model_dump())
            
            action = ActionItem(
                finding_id=finding.finding_id,
                action_description="Implement fix and monitor",
                owner_team=OwnerTeam.Engineering if incident.incident_type == "bank_outage" else OwnerTeam.BankOps,
                due_date=(datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                status=ActionStatus.completed
            )
            await db.actions.insert_one(action.model_dump())
            
            validation = ClosureValidation(
                audit_id=audit.audit_id,
                validation_done=True,
                validation_notes="Audit completed successfully",
                validated_by="Audit Manager",
                validated_at=datetime.now(timezone.utc).isoformat()
            )
            await db.validations.insert_one(validation.model_dump())
    
    logger.info("Database seeded successfully")

@app.on_event("startup")
async def startup_event():
    await seed_data()

@api_router.get("/")
async def root():
    return {"message": "Payment Operations Audit System"}

@api_router.get("/incidents")
async def get_incidents():
    incidents = await db.incidents.find({}, {"_id": 0}).to_list(1000)
    return incidents

@api_router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    incident = await db.incidents.find_one({"incident_id": incident_id}, {"_id": 0})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@api_router.post("/audits")
async def create_audit(incident_id: str):
    incident = await db.incidents.find_one({"incident_id": incident_id}, {"_id": 0})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    existing_audit = await db.audits.find_one({"incident_id": incident_id}, {"_id": 0})
    if existing_audit:
        return existing_audit
    
    audit = AuditCase(
        incident_id=incident_id,
        audit_owner=AuditOwner.Ops,
        audit_start_date=datetime.now(timezone.utc).isoformat(),
        audit_status=AuditStatus.in_progress,
        summary=f"New audit for incident {incident_id}"
    )
    await db.audits.insert_one(audit.model_dump())
    
    checklist_questions = [
        "Was the incident detected within SLA timeframe?",
        "Were all stakeholders notified promptly?",
        "Was root cause analysis completed?",
        "Were impacted transactions identified?",
        "Was customer communication sent out?",
        "Were monitoring alerts functioning correctly?",
        "Has preventive action been identified?"
    ]
    
    for question in checklist_questions[:6]:
        checklist_item = AuditChecklistItem(
            audit_id=audit.audit_id,
            question=question,
            response=ChecklistResponse.pending
        )
        await db.checklist.insert_one(checklist_item.model_dump())
    
    await db.incidents.update_one(
        {"incident_id": incident_id},
        {"$set": {"status": "under_audit"}}
    )
    
    return audit.model_dump()

@api_router.get("/audits/{audit_id}")
async def get_audit(audit_id: str):
    audit = await db.audits.find_one({"audit_id": audit_id}, {"_id": 0})
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    incident = await db.incidents.find_one({"incident_id": audit["incident_id"]}, {"_id": 0})
    checklist = await db.checklist.find({"audit_id": audit_id}, {"_id": 0}).to_list(100)
    findings = await db.findings.find({"audit_id": audit_id}, {"_id": 0}).to_list(100)
    
    actions = []
    for finding in findings:
        finding_actions = await db.actions.find({"finding_id": finding["finding_id"]}, {"_id": 0}).to_list(100)
        actions.extend(finding_actions)
    
    validation = await db.validations.find_one({"audit_id": audit_id}, {"_id": 0})
    
    return {
        "audit": audit,
        "incident": incident,
        "checklist": checklist,
        "findings": findings,
        "actions": actions,
        "validation": validation
    }

@api_router.post("/checklist")
async def update_checklist(request: ChecklistUpdateRequest):
    result = await db.checklist.update_one(
        {"checklist_id": request.checklist_id},
        {"$set": {
            "response": request.response,
            "evidence_link": request.evidence_link
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    return {"success": True}

@api_router.post("/findings")
async def create_finding(request: FindingCreateRequest):
    finding = AuditFinding(
        audit_id=request.audit_id,
        category=request.category,
        description=request.description,
        severity=request.severity,
        evidence_reference=request.evidence_reference
    )
    await db.findings.insert_one(finding.model_dump())
    return finding.model_dump()

@api_router.post("/actions")
async def create_or_update_action(request: ActionCreateRequest):
    action = ActionItem(
        finding_id=request.finding_id,
        action_description=request.action_description,
        owner_team=request.owner_team,
        due_date=request.due_date,
        status=ActionStatus.open
    )
    await db.actions.insert_one(action.model_dump())
    return action.model_dump()

@api_router.post("/actions/update")
async def update_action(request: ActionUpdateRequest):
    result = await db.actions.update_one(
        {"action_id": request.action_id},
        {"$set": {"status": request.status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Action item not found")
    return {"success": True}

@api_router.post("/validate")
async def validate_audit(request: ValidationRequest):
    validation = ClosureValidation(
        audit_id=request.audit_id,
        validation_done=True,
        validation_notes=request.validation_notes,
        validated_by=request.validated_by,
        validated_at=datetime.now(timezone.utc).isoformat()
    )
    await db.validations.insert_one(validation.model_dump())
    return validation.model_dump()

@api_router.post("/close-audit")
async def close_audit(audit_id: str):
    audit = await db.audits.find_one({"audit_id": audit_id}, {"_id": 0})
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    checklist = await db.checklist.find({"audit_id": audit_id}, {"_id": 0}).to_list(100)
    pending_checklist = [item for item in checklist if item["response"] == "pending"]
    if pending_checklist:
        raise HTTPException(status_code=400, detail="All checklist items must be completed")
    
    findings = await db.findings.find({"audit_id": audit_id}, {"_id": 0}).to_list(100)
    if not findings:
        raise HTTPException(status_code=400, detail="At least one finding must exist")
    
    all_actions = []
    for finding in findings:
        actions = await db.actions.find({"finding_id": finding["finding_id"]}, {"_id": 0}).to_list(100)
        all_actions.extend(actions)
    
    incomplete_actions = [action for action in all_actions if action["status"] != "completed"]
    if incomplete_actions:
        raise HTTPException(status_code=400, detail="All action items must be completed")
    
    validation = await db.validations.find_one({"audit_id": audit_id}, {"_id": 0})
    if not validation or not validation.get("validation_done"):
        raise HTTPException(status_code=400, detail="Closure validation must be done")
    
    await db.audits.update_one(
        {"audit_id": audit_id},
        {"$set": {"audit_status": "closed"}}
    )
    
    incident = await db.incidents.find_one({"incident_id": audit["incident_id"]}, {"_id": 0})
    if incident:
        await db.incidents.update_one(
            {"incident_id": audit["incident_id"]},
            {"$set": {"status": "closed"}}
        )
    
    return {"success": True, "message": "Audit closed successfully"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
