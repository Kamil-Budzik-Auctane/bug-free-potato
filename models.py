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


# New models for enhanced risk assessment API
class RiskFactor(BaseModel):
    score: int = Field(ge=0, le=100, description="Factor risk score 0-100")
    weight: int = Field(ge=0, le=100, description="Weight percentage in overall calculation")
    status: str = Field(description="Human readable status description")
    level: str = Field(description="Risk level: high, medium, low")


class EnhancedRiskAssessment(BaseModel):
    score: int = Field(ge=0, le=100, description="Overall risk score 0-100")
    confidenceLevel: int = Field(ge=0, le=100, description="AI model confidence percentage")
    predictedDelayDays: int = Field(ge=0, description="Number of days delay predicted")
    
    factors: dict[str, RiskFactor] = Field(description="Individual risk factors breakdown")
    
    originalDeliveryDate: str = Field(description="Original expected delivery date (ISO 8601)")
    revisedDeliveryDate: str = Field(description="Revised delivery date if delay predicted")


# ShipStation Integration Models
class ShipStationWeight(BaseModel):
    unit: str
    value: float


class ShipStationStore(BaseModel):
    storeGuid: str
    marketplaceCode: Optional[str] = None


class ShipStationShipment(BaseModel):
    salesOrderId: str
    fulfillmentPlanId: str
    orderNumber: str
    recipientName: str
    orderDateTime: str
    shipByDateTime: str
    countryCode: str
    state: str
    derivedStatus: str
    store: ShipStationStore
    serviceId: str
    serviceName: Optional[str] = None
    shipFromId: str
    shipFromName: str
    weight: ShipStationWeight
    requestedService: str
    # Risk score added by our enrichment
    riskScore: Optional[int] = Field(default=None, ge=0, le=100)


class ShipStationResponse(BaseModel):
    page: int
    pageSize: int
    totalCount: int
    pageData: List[ShipStationShipment]