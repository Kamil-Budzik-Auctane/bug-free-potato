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
    marketplaceId: Optional[str] = None
    marketplaceCode: Optional[str] = None
    externalUrl: Optional[str] = None
    source: Optional[dict] = None


class ShipStationShipTo(BaseModel):
    isModified: Optional[bool] = None
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    line3: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    countryCode: Optional[str] = None
    residentialIndicator: Optional[str] = None
    verificationStatus: Optional[str] = None
    verificationMessage: Optional[str] = None
    verificationUtc: Optional[str] = None
    lockAddress: Optional[bool] = None


class ShipStationSoldTo(BaseModel):
    customerId: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


class ShipStationItem(BaseModel):
    salesOrderItemId: str
    productId: Optional[str] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    originalQuantity: Optional[int] = None
    quantity: Optional[int] = None
    productThumbnailUrl: Optional[str] = None
    unitPrice: Optional[dict] = None
    totalPrice: Optional[dict] = None
    isGift: Optional[bool] = None
    attributes: Optional[List] = None


class ShipStationAmountSummary(BaseModel):
    productTotal: Optional[dict] = None
    orderTotal: Optional[dict] = None
    shippingPaid: Optional[dict] = None
    taxPaid: Optional[dict] = None
    totalPaid: Optional[dict] = None


class ShipStationSalesOrder(BaseModel):
    fulfillmentPlanIds: List[str]
    salesOrderId: str
    orderNumber: str
    createdDateTime: str
    modifiedDateTime: str
    orderDateTime: str
    paidDateTime: Optional[str] = None
    shipByDateTime: Optional[str] = None
    holdUntilDateTime: Optional[str] = None
    assignedToUser: Optional[str] = None
    assignedToUserId: Optional[str] = None
    requestedService: Optional[str] = None
    isGift: Optional[bool] = None
    isCanceled: Optional[bool] = None
    derivedStatus: str
    items: List[ShipStationItem]
    store: ShipStationStore
    soldTo: ShipStationSoldTo
    shipTos: List[ShipStationShipTo]
    amountSummary: ShipStationAmountSummary
    discounts: Optional[List] = None
    premiumAttributes: Optional[List] = None
    tagIds: Optional[List] = None
    originalSource: Optional[str] = None
    otherIdentifiers: Optional[List] = None
    restrictions: Optional[dict] = None
    # Risk score added by our enrichment
    riskScore: Optional[int] = Field(default=None, ge=0, le=100)


class ShipStationAwaitingShipmentResponse(BaseModel):
    currentPageFulfillmentPlanIds: List[str]
    salesOrders: List[ShipStationSalesOrder]


# Legacy models for backward compatibility
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