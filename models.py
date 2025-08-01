from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CarrierType(str, Enum):
    UPS = "UPS"
    FEDEX = "FedEx"
    USPS = "USPS"
    DHL = "DHL"


class ActionType(str, Enum):
    ACCEPT_DELAY = "Accept Delay"
    REQUEST_REFUND = "Request Refund"
    RESEND = "Resend"


class Package(BaseModel):
    package_id: str
    destination_zip: str
    destination_city: str
    carrier: CarrierType
    expected_delivery_date: str
    

class RiskAssessment(BaseModel):
    risk_score: int = Field(ge=0, le=100, description="Risk score from 0-100")
    reasons: List[str] = Field(description="List of risk factors")


class EnrichedPackage(Package):
    risk_score: int = Field(ge=0, le=100)
    reasons: List[str]


class AlertRequest(BaseModel):
    package_id: str
    customer_email: Optional[str] = None


class ActionRequest(BaseModel):
    package_id: str
    action: ActionType
    customer_id: Optional[str] = None
    notes: Optional[str] = None


class AlertResponse(BaseModel):
    success: bool
    message: str
    email_sent: bool = False


class ActionResponse(BaseModel):
    success: bool
    message: str
    action_logged: bool = True