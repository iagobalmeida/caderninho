from datetime import datetime
from enum import Enum
from functools import partial
from typing import Optional

from httpx import AsyncClient
from loguru import logger
from pydantic import BaseModel

from env import getenv

BASE_URL = getenv('ASAAS_BASE_URL', 'https://www.asaas.com/api/v3')
ACCESS_TOKEN = getenv('ASAAS_ACCESS_TOKEN', None)


class ChargeType(Enum):
    DETACHED = 'DETACHED'
    RECURRENT = 'RECURRENT'
    INSTALLMENT = 'INSTALLMENT'


class BillingType(Enum):
    UNDEFINED = 'UNDEFINED'
    BOLETO = 'BOLETO'
    CREDIT_CARD = 'CREDIT_CARD'
    PIX = 'PIX'


class SubscriptionCycle(Enum):
    WEEKLY = 'WEEKLY'
    BIWEEKLY = 'BIWEEKLY'
    MONTHLY = 'MONTHLY'
    BIMONTHLY = 'BIMONTHLY'
    QUARTERLY = 'QUARTERLY'
    SEMIANNUALLY = 'SEMIANNUALLY'
    YEARLY = 'YEARLY'


class CreditCard(BaseModel):
    creditCardNumber: str
    creditCardBrand: str
    creditCardToken: str


class Payment(BaseModel):
    class ChargeBack(BaseModel):
        status: str
        reason: str
    object: str
    id: str                     # ID do pagamento
    dateCreated: str
    customer: str               # ID do cliente no ASAAS
    subscription: Optional[str] = None
    installment: str
    paymentLink: str            # ID do link de pagamento
    dueDate: str
    originalDueDate: str
    value: float
    netValue: float
    originalValue: Optional[float] = None
    interestValue: float
    description: str
    externalReference: str
    billingType: str
    status: str
    confirmedDate: str
    paymentDate: str
    clientPaymentDate: str
    creditDate: str
    estimatedCreditDate: str
    invoiceUrl: str
    transactionReceiptUrl: str
    invoiceNumber: str
    deleted: bool
    anticipated: bool
    anticipable: bool
    lastInvoiceViewedDate: str
    postalService: bool
    creditCard: CreditCard
    chargeback: ChargeBack


class WebhookData(BaseModel):
    id: str
    event: str
    dateCreated: datetime
    payment: Payment


class PaymentLink(BaseModel):
    id: str
    name: str
    value: float
    active: bool
    chargeType: ChargeType
    url: str
    billingType: BillingType
    # subscriptionCycle: SubscriptionCycle
    # description: str
    # endDate: datetime
    # deleted: bool
    # viewCount: int
    # maxInstallmentCount: int
    # dueDateLimitDays: int
    # notificationEnabled: bool
    # isAddressRequired: bool
    externalReference: str


async def api_request(method: str, url: str, json: dict = None, data: dict = None):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'KDerninho',
        'access_token': ACCESS_TOKEN
    }
    async with AsyncClient() as client:
        result = await client.request(method, f'{BASE_URL}{url}', headers=headers, json=json, data=data)
    return result


async def api_create_payment_link(externalReference: str, name: str, value: float, callback_url: str, description: str = None, charge_type: str = ChargeType.RECURRENT.value, auto_redirect: bool = True) -> PaymentLink:
    api_result = await api_request('POST', '/paymentLinks', json={
        'name': name,
        'chargeType': charge_type,
        'value': value,
        'description': description,
        'dueDateLimitDays': 7,
        'billingType': BillingType.UNDEFINED.value,
        'callback': {
            'successUrl': callback_url,
            'autoRedirect': auto_redirect
        },
        'isAddressRequired': False,
        'externalReference': externalReference
    })
    api_json = api_result.json()
    return PaymentLink(**api_json)
