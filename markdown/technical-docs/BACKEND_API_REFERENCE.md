# 📡 Backend API Reference

## Table of Contents
- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Tenants & Outlets](#tenants--outlets)
- [Products & Categories](#products--categories)
- [Orders & Checkout](#orders--checkout)
- [Payments](#payments)
- [Users & Roles](#users--roles)
- [Promotions](#promotions)
- [Error Handling](#error-handling)

---

## API Overview

### Base URL

```
Development:  http://localhost:8000/api/
Production:   https://api.yourdomain.com/api/
```

### API Documentation

- **Swagger UI**: `/api/docs/` - Interactive API documentation
- **OpenAPI Schema**: `/api/schema/` - Download OpenAPI 3.0 spec

### Request Headers

```http
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
X-Tenant-ID: <TENANT_ID>
X-Outlet-ID: <OUTLET_ID>  (optional)
```

### Response Format

**Success Response**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message",
  "details": {
    "field": ["Validation error"]
  }
}
```

---

## Authentication

### 1. JWT Login (Kiosk/Mobile)

```http
POST /api/auth/token/
```

**Request**:
```json
{
  "username": "cashier1",
  "password": "password123"
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "cashier1",
    "role": "cashier",
    "tenant_id": 123,
    "outlet_id": 456
  }
}
```

### 2. Refresh Token

```http
POST /api/auth/token/refresh/
```

**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Token Login (Admin Panel)

```http
POST /api/auth/login/
```

**Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "tenant": {
      "id": 1,
      "name": "Restaurant Name"
    }
  }
}
```

### 4. Logout

```http
POST /api/auth/logout/
Authorization: Token <TOKEN>
```

---

## Tenants & Outlets

### List Tenants (Public)

```http
GET /api/public/tenants/
```

**Query Parameters**:
- `is_active`: Boolean (default: true)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Ayam Geprek Bensu",
      "slug": "ayam-geprek-bensu",
      "logo": "https://example.com/media/tenants/logo.png",
      "primary_color": "#FF6B35",
      "description": "Best Ayam Geprek in town"
    }
  ]
}
```

### Get Tenant Detail

```http
GET /api/tenants/{id}/
X-Tenant-ID: {id}
```

**Response**:
```json
{
  "id": 1,
  "name": "Ayam Geprek Bensu",
  "slug": "ayam-geprek-bensu",
  "logo": "https://example.com/media/tenants/logo.png",
  "primary_color": "#FF6B35",
  "secondary_color": "#F7931E",
  "tax_rate": "10.00",
  "service_charge_rate": "5.00",
  "phone": "021-12345678",
  "email": "contact@ayamgeprek.com"
}
```

### List Outlets

```http
GET /api/outlets/
X-Tenant-ID: {tenant_id}
```

**Query Parameters**:
- `is_active`: Boolean

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "tenant_id": 1,
      "name": "Tunjungan Plaza",
      "code": "TP-001",
      "address": "Mall Tunjungan Plaza Lt.4",
      "city": "Surabaya",
      "phone": "031-1234567",
      "is_active": true
    }
  ]
}
```

### Get Accessible Outlets (User)

```http
GET /api/outlets/accessible/
Authorization: Bearer <TOKEN>
```

Returns outlets user has access to based on role.

---

## Products & Categories

### List Categories

```http
GET /api/categories/
X-Tenant-ID: {tenant_id}
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "tenant_id": 1,
      "name": "Ayam Geprek",
      "description": "Spicy fried chicken",
      "image": "https://example.com/media/categories/ayam.jpg",
      "sort_order": 1,
      "is_active": true
    }
  ]
}
```

### List Products

```http
GET /api/products/
X-Tenant-ID: {tenant_id}
X-Outlet-ID: {outlet_id}  (optional)
```

**Query Parameters**:
- `category_id`: Filter by category
- `is_active`: Boolean (default: true)
- `is_available`: Boolean (default: true)
- `is_popular`: Boolean
- `has_promo`: Boolean
- `search`: Search by name/description
- `page`: Page number
- `page_size`: Items per page (default: 20)

**Response**:
```json
{
  "success": true,
  "count": 50,
  "next": "http://api/products/?page=2",
  "previous": null,
  "data": [
    {
      "id": 1,
      "tenant_id": 1,
      "outlet_id": null,
      "category": {
        "id": 1,
        "name": "Ayam Geprek"
      },
      "sku": "AGR-001",
      "name": "Ayam Geprek Original",
      "description": "Spicy fried chicken with sambal",
      "image": "https://example.com/media/products/ayam1.jpg",
      "price": "25000.00",
      "promo_price": null,
      "has_promo": false,
      "is_popular": true,
      "is_available": true,
      "preparation_time": 10,
      "modifiers": [
        {
          "id": 1,
          "name": "Level 5 (Extra Spicy)",
          "type": "spicy",
          "price_adjustment": "0.00"
        },
        {
          "id": 2,
          "name": "Extra Keju",
          "type": "extra",
          "price_adjustment": "5000.00"
        }
      ]
    }
  ]
}
```

### Get Product Detail

```http
GET /api/products/{id}/
X-Tenant-ID: {tenant_id}
```

**Response**: Same as product in list, with full details.

### Create Product (Admin)

```http
POST /api/products/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
Content-Type: multipart/form-data
```

**Request**:
```json
{
  "category_id": 1,
  "outlet_id": null,
  "sku": "AGR-002",
  "name": "Ayam Geprek Keju",
  "description": "With extra cheese",
  "price": "30000.00",
  "image": <file>,
  "is_active": true,
  "is_available": true,
  "track_stock": true,
  "stock_quantity": 100
}
```

### Update Product

```http
PUT /api/products/{id}/
PATCH /api/products/{id}/  (partial update)
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

### Delete Product

```http
DELETE /api/products/{id}/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

---

## Orders & Checkout

### List Orders

```http
GET /api/orders/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
X-Outlet-ID: {outlet_id}
```

**Query Parameters**:
- `status`: pending, confirmed, preparing, ready, completed, cancelled
- `payment_status`: unpaid, partial, paid
- `date_from`: YYYY-MM-DD
- `date_to`: YYYY-MM-DD
- `search`: Search by order_number or customer_name
- `page`: Page number

**Response**:
```json
{
  "success": true,
  "count": 120,
  "data": [
    {
      "id": 1,
      "tenant_id": 1,
      "outlet_id": 1,
      "order_number": "ORD-20260103-A1B2",
      "status": "pending",
      "customer_name": "John Doe",
      "customer_phone": "081234567890",
      "table_number": "A-12",
      "subtotal": "50000.00",
      "tax_amount": "5000.00",
      "service_charge_amount": "2500.00",
      "discount_amount": "0.00",
      "total_amount": "57500.00",
      "payment_status": "unpaid",
      "paid_amount": "0.00",
      "items_count": 2,
      "created_at": "2026-01-03T10:30:00Z",
      "cashier": {
        "id": 1,
        "username": "cashier1"
      }
    }
  ]
}
```

### Get Order Detail

```http
GET /api/orders/{id}/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "order_number": "ORD-20260103-A1B2",
    "status": "pending",
    "customer_name": "John Doe",
    "customer_phone": "081234567890",
    "table_number": "A-12",
    "notes": "Extra sambal",
    "subtotal": "50000.00",
    "tax_amount": "5000.00",
    "service_charge_amount": "2500.00",
    "discount_amount": "0.00",
    "total_amount": "57500.00",
    "payment_status": "unpaid",
    "items": [
      {
        "id": 1,
        "product": {
          "id": 1,
          "name": "Ayam Geprek Original",
          "sku": "AGR-001"
        },
        "quantity": 2,
        "unit_price": "25000.00",
        "total_price": "50000.00",
        "modifiers": [
          {
            "name": "Level 5",
            "price_adjustment": "0.00"
          }
        ],
        "notes": "Extra pedas",
        "kitchen_status": "pending"
      }
    ],
    "created_at": "2026-01-03T10:30:00Z",
    "updated_at": "2026-01-03T10:30:00Z"
  }
}
```

### Create Order / Checkout

```http
POST /api/orders/checkout/
Authorization: Bearer <TOKEN>  (optional for kiosk)
X-Tenant-ID: {tenant_id}
X-Outlet-ID: {outlet_id}
```

**Request**:
```json
{
  "customer_name": "John Doe",
  "customer_phone": "081234567890",
  "customer_email": "john@example.com",
  "table_number": "A-12",
  "notes": "Extra sambal please",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "modifiers": [
        {
          "id": 1,
          "name": "Level 5",
          "price_adjustment": "0.00"
        },
        {
          "id": 2,
          "name": "Extra Keju",
          "price_adjustment": "5000.00"
        }
      ],
      "notes": "Extra pedas"
    },
    {
      "product_id": 3,
      "quantity": 1,
      "modifiers": [],
      "notes": ""
    }
  ],
  "promo_code": "DISKON20"  (optional)
}
```

**Response**:
```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "id": 1,
    "order_number": "ORD-20260103-A1B2",
    "status": "pending",
    "total_amount": "57500.00",
    "payment_url": "https://payment-gateway.com/...",  (if payment required)
    "items": [...]
  }
}
```

### Update Order Status

```http
PATCH /api/orders/{id}/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

**Request**:
```json
{
  "status": "confirmed"  // confirmed, preparing, ready, completed
}
```

### Cancel Order

```http
POST /api/orders/{id}/cancel/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

**Response**:
```json
{
  "success": true,
  "message": "Order cancelled successfully"
}
```

---

## Payments

### Create Payment

```http
POST /api/payments/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

**Request**:
```json
{
  "order_id": 1,
  "method": "qris",  // cash, qris, card, ewallet
  "amount": "57500.00",
  "gateway": "midtrans"  (optional, for non-cash)
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "order_id": 1,
    "method": "qris",
    "amount": "57500.00",
    "status": "pending",
    "transaction_id": "TRX-123456",
    "payment_url": "https://payment-gateway.com/...",
    "qr_code": "data:image/png;base64,..."
  }
}
```

### Check Payment Status

```http
GET /api/payments/{id}/status/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "success",  // pending, success, failed
    "transaction_id": "TRX-123456",
    "paid_at": "2026-01-03T10:35:00Z"
  }
}
```

---

## Users & Roles

### List Users

```http
GET /api/users/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

**Query Parameters**:
- `role`: super_admin, admin, tenant_owner, manager, cashier, kitchen
- `outlet_id`: Filter by outlet
- `is_active`: Boolean

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "cashier1",
      "email": "cashier1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "cashier",
      "phone_number": "081234567890",
      "tenant": {
        "id": 1,
        "name": "Restaurant Name"
      },
      "outlet": {
        "id": 1,
        "name": "Outlet Name"
      },
      "is_active": true
    }
  ]
}
```

### Create User

```http
POST /api/users/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

**Request**:
```json
{
  "username": "cashier2",
  "email": "cashier2@example.com",
  "password": "securepassword123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "cashier",
  "phone_number": "081234567891",
  "outlet_id": 1
}
```

### Update User

```http
PATCH /api/users/{id}/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

### Get Current User Profile

```http
GET /api/users/me/
Authorization: Bearer <TOKEN>
```

---

## Promotions

### List Promotions

```http
GET /api/promotions/
Authorization: Bearer <TOKEN>
X-Tenant-ID: {tenant_id}
```

**Query Parameters**:
- `is_active`: Boolean
- `type`: percentage, fixed, buy_x_get_y, bundle

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "tenant_id": 1,
      "name": "Diskon 20%",
      "description": "Discount 20% for all items",
      "type": "percentage",
      "code": "DISKON20",
      "discount_value": "20.00",
      "min_purchase": "50000.00",
      "max_discount": "10000.00",
      "start_date": "2026-01-01T00:00:00Z",
      "end_date": "2026-01-31T23:59:59Z",
      "is_active": true,
      "applicable_products": [1, 2, 3]
    }
  ]
}
```

### Validate Promo Code

```http
POST /api/promotions/validate/
X-Tenant-ID: {tenant_id}
```

**Request**:
```json
{
  "code": "DISKON20",
  "subtotal": "75000.00",
  "product_ids": [1, 2]
}
```

**Response**:
```json
{
  "success": true,
  "valid": true,
  "discount_amount": "10000.00",
  "message": "Promo code applied successfully"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "success": false,
  "error": "Validation error",
  "details": {
    "name": ["This field is required"],
    "price": ["Must be a positive number"]
  },
  "code": "VALIDATION_ERROR"
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Invalid credentials
- `PERMISSION_DENIED`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `TENANT_MISMATCH`: Resource doesn't belong to tenant
- `INSUFFICIENT_STOCK`: Product out of stock
- `INVALID_PROMO_CODE`: Promo code invalid or expired

---

## Rate Limiting

### Default Limits

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Admin**: 5000 requests/hour

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641024000
```

---

## Pagination

### Query Parameters

```
?page=2&page_size=20
```

### Response Format

```json
{
  "count": 150,
  "next": "http://api/products/?page=3",
  "previous": "http://api/products/?page=1",
  "data": [...]
}
```

---

**For complete API documentation, visit**: `/api/docs/` (Swagger UI)

**Last Updated**: January 3, 2026
