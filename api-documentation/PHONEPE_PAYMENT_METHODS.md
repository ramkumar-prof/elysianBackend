# PhonePe Payment Methods Configuration

## Overview

This document outlines the payment method configuration for PhonePe gateway integration, including all supported payment modes and their implementation details.

## Supported PhonePe Payment Modes

### **🎯 PhonePe Gateway Payment Modes**

The following payment modes are supported as per PhonePe gateway specifications:

| Payment Mode | Description | Display Name |
|--------------|-------------|--------------|
| `UPI_INTENT` | UPI Intent-based payments | UPI Intent |
| `UPI_COLLECT` | UPI Collect requests | UPI Collect |
| `UPI_QR` | UPI QR code payments | UPI QR |
| `CARD` | Credit/Debit card payments | Card |
| `TOKEN` | Tokenized card payments | Token |
| `NET_BANKING` | Net banking payments | Net Banking |

### **💰 Additional Payment Methods**

| Payment Mode | Description | Display Name |
|--------------|-------------|--------------|
| `CASH` | Cash on delivery | Cash |

## Database Configuration

### **📊 Payment Model**

```python
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('UPI_INTENT', 'UPI Intent'),
        ('UPI_COLLECT', 'UPI Collect'),
        ('UPI_QR', 'UPI QR'),
        ('CARD', 'Card'),
        ('TOKEN', 'Token'),
        ('NET_BANKING', 'Net Banking'),
    ]
    
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES
    )
```

### **🔄 Migration Applied**

```bash
python manage.py makemigrations common --name update_phonepe_payment_methods
python manage.py migrate
```

**Migration File**: `common/migrations/0003_update_phonepe_payment_methods.py`

## Payment Method Extraction

### **🔧 Gateway Response Processing**

The payment method is extracted from PhonePe gateway response as follows:

```python
# Extract payment method from gateway response
if hasattr(payment_detail, 'payment_mode'):
    payment_mode = payment_detail.payment_mode
    if hasattr(payment_mode, 'value'):
        payment.payment_method = payment_mode.value
    else:
        payment.payment_method = str(payment_mode)
```

### **📋 Example Gateway Response**

```python
payment_detail = PaymentDetail(
    transaction_id='OM2510172011132576300061',
    payment_mode=<PgV2InstrumentType.UPI_QR: 'UPI_QR'>,
    timestamp=1760712167081,
    amount=13900,
    state='COMPLETED',
    # ... other fields
)
```

**Extracted Value**: `payment_mode.value` → `'UPI_QR'`

## Payment Method Mapping

### **🎯 PhonePe to Database Mapping**

| PhonePe Response | Database Value | Display |
|------------------|----------------|---------|
| `UPI_INTENT` | `UPI_INTENT` | UPI Intent |
| `UPI_COLLECT` | `UPI_COLLECT` | UPI Collect |
| `UPI_QR` | `UPI_QR` | UPI QR |
| `CARD` | `CARD` | Card |
| `TOKEN` | `TOKEN` | Token |
| `NET_BANKING` | `NET_BANKING` | Net Banking |

### **✅ Direct Mapping**

The payment modes from PhonePe gateway map directly to database values without any transformation, ensuring consistency and accuracy.

## Usage Examples

### **📊 Creating Payment Records**

```python
# Example: Creating payment with UPI_QR method
payment = Payment.objects.create(
    order=order,
    amount=13900,  # Amount in paisa
    transaction_id='OM2510172011132576300061',
    gateway_order_id='OMO2510172011132576300982',
    payment_status='COMPLETED',
    payment_method='UPI_QR'  # PhonePe payment mode
)
```

### **🔍 Querying by Payment Method**

```python
# Get all UPI payments
upi_payments = Payment.objects.filter(
    payment_method__in=['UPI_INTENT', 'UPI_COLLECT', 'UPI_QR']
)

# Get all card payments
card_payments = Payment.objects.filter(
    payment_method__in=['CARD', 'TOKEN']
)

# Get net banking payments
netbanking_payments = Payment.objects.filter(
    payment_method='NET_BANKING'
)
```

### **📈 Payment Method Analytics**

```python
from django.db.models import Count

# Payment method distribution
payment_distribution = Payment.objects.values('payment_method').annotate(
    count=Count('id')
).order_by('-count')

# Example result:
# [
#     {'payment_method': 'UPI_QR', 'count': 150},
#     {'payment_method': 'CARD', 'count': 89},
#     {'payment_method': 'UPI_INTENT', 'count': 67},
#     {'payment_method': 'NET_BANKING', 'count': 23},
#     {'payment_method': 'UPI_COLLECT', 'count': 12},
#     {'payment_method': 'TOKEN', 'count': 8},
#     {'payment_method': 'CASH', 'count': 5}
# ]
```

## API Response Format

### **📊 Payment Serializer Response**

```json
{
    "id": 12,
    "order": 8,
    "amount": 13900,
    "transaction_id": "OM2510172011132576300061",
    "gateway_order_id": "OMO2510172011132576300982",
    "payment_status": "COMPLETED",
    "payment_method": "UPI_QR",
    "additional_info": {
        "timestamp": 1760712167081,
        "error_code": null,
        "error_detail": null,
        "upi_transaction_id": "YBL5bc011fa9f8644558b52b96a29a96627",
        "gateway_order_id": "OMO2510172011132576300982",
        "gateway_state": "COMPLETED",
        "gateway_amount": 13900,
        "last_checked": "2025-10-17T15:44:55.863725+00:00"
    },
    "created_at": "2025-10-17T15:30:00.000000Z",
    "updated_at": "2025-10-17T15:44:55.863725Z"
}
```

## Testing

### **🧪 Test Coverage**

All PhonePe payment modes have been tested for:

- ✅ **Model Validation**: All payment modes are valid choices
- ✅ **Payment Creation**: Payments can be created with all modes
- ✅ **Extraction Logic**: Payment modes are correctly extracted from gateway responses
- ✅ **Database Storage**: All modes are properly stored and retrieved

### **📋 Test Results**

```
✅ UPI_INTENT   → Payment ID: 12
✅ UPI_COLLECT  → Payment ID: 13
✅ UPI_QR       → Payment ID: 14
✅ CARD         → Payment ID: 15
✅ TOKEN        → Payment ID: 16
✅ NET_BANKING  → Payment ID: 17
```

## Migration History

### **📝 Migration Timeline**

1. **Initial Payment Methods** (Migration 0001)
   - Basic payment methods: CASH, CARD, UPI, WALLET

2. **PhonePe Integration** (Migration 0002)
   - Added: UPI_QR, NET_BANKING
   - Updated for initial PhonePe support

3. **Complete PhonePe Support** (Migration 0003)
   - Added: UPI_INTENT, UPI_COLLECT, TOKEN
   - Removed: UPI (generic), WALLET
   - Final PhonePe gateway alignment

### **🔄 Migration Commands**

```bash
# Create migration
python manage.py makemigrations common --name update_phonepe_payment_methods

# Apply migration
python manage.py migrate

# Verify migration
python manage.py showmigrations common
```

## Best Practices

### **✅ Implementation Guidelines**

1. **Direct Mapping**: Use PhonePe payment modes directly without transformation
2. **Validation**: Always validate payment_method against PAYMENT_METHOD_CHOICES
3. **Error Handling**: Handle cases where payment_mode might be missing or invalid
4. **Logging**: Log payment method extraction for debugging
5. **Testing**: Test all payment modes in development environment

### **🚫 Common Pitfalls**

1. **Don't Transform**: Avoid transforming PhonePe payment modes
2. **Don't Assume**: Don't assume payment_mode will always have .value attribute
3. **Don't Hardcode**: Use model choices instead of hardcoded strings
4. **Don't Skip Validation**: Always validate payment methods before saving

## Monitoring

### **📊 Recommended Metrics**

- Payment method distribution
- Success rates by payment method
- Transaction amounts by payment method
- Error rates by payment method
- Processing times by payment method

### **🔍 Logging**

```python
logger.info(f"Payment method extracted: {payment_method} for order {order_id}")
logger.warning(f"Unknown payment method: {payment_method} for order {order_id}")
```

---

**Status**: ✅ **IMPLEMENTED**  
**Version**: 1.0  
**Last Updated**: 2025-10-17  
**Migration**: 0003_update_phonepe_payment_methods
