# Settings Management - Complete Implementation

## Overview

Complete Settings Management feature for the POS Admin Panel, providing comprehensive tenant configuration and outlet management capabilities. This feature allows administrators to manage business settings, branding, financial configurations, and multiple outlet locations.

**Access URL**: http://localhost:5175/settings

## What's Included

### Backend API

#### 1. Tenant Settings ViewSet (`backend/apps/tenants/views_admin.py`)

**TenantSettingsViewSet**
- Full CRUD operations for tenant settings
- Logo upload and management
- Multi-tenant isolation
- Permission: `IsAdminOrTenantOwnerOrManager`

**Features**:
- Get current tenant settings
- Update tenant information
- Upload tenant logo (images, max 2MB)
- Delete tenant logo
- Automatic tenant filtering based on user context

#### 2. Outlet Management ViewSet (`backend/apps/tenants/views_admin.py`)

**OutletManagementViewSet**
- Full CRUD operations for outlets
- Advanced filtering and search
- Statistics and analytics
- Bulk operations support

**Features**:
- List outlets with filters
- Create new outlets
- Update outlet information
- Soft delete outlets
- Bulk activate/deactivate
- Outlet statistics by city and province

### API Endpoints

#### Tenant Settings Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/settings/tenant/` | GET | Get current tenant settings |
| `/api/admin/settings/tenant/{id}/` | PUT/PATCH | Update tenant settings |
| `/api/admin/settings/tenant/{id}/upload_logo/` | POST | Upload tenant logo |
| `/api/admin/settings/tenant/{id}/delete_logo/` | DELETE | Delete tenant logo |

**GET /api/admin/settings/tenant/**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/tenant/
```

Response:
```json
{
  "id": 1,
  "name": "My Restaurant",
  "slug": "my-restaurant",
  "description": "Premium dining experience",
  "logo_url": "http://localhost:8000/media/tenants/logos/logo.png",
  "primary_color": "#FF6B35",
  "secondary_color": "#F7931E",
  "phone": "+1234567890",
  "email": "contact@restaurant.com",
  "website": "https://restaurant.com",
  "tax_rate": "10.00",
  "service_charge_rate": "5.00",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "outlet_count": 3,
  "outlets": [...]
}
```

**PATCH /api/admin/settings/tenant/{id}/**
```bash
curl -X PATCH http://localhost:8000/api/admin/settings/tenant/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Restaurant Name",
    "primary_color": "#FF0000",
    "tax_rate": "11.00"
  }'
```

**POST /api/admin/settings/tenant/{id}/upload_logo/**
```bash
curl -X POST http://localhost:8000/api/admin/settings/tenant/1/upload_logo/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "logo=@/path/to/logo.png"
```

Response:
```json
{
  "status": "success",
  "message": "Logo uploaded successfully",
  "data": { ...tenant_with_new_logo... }
}
```

**DELETE /api/admin/settings/tenant/{id}/delete_logo/**
```bash
curl -X DELETE http://localhost:8000/api/admin/settings/tenant/1/delete_logo/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Outlet Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/settings/outlets/` | GET | List outlets with filters |
| `/api/admin/settings/outlets/` | POST | Create new outlet |
| `/api/admin/settings/outlets/{id}/` | GET | Get outlet detail |
| `/api/admin/settings/outlets/{id}/` | PUT/PATCH | Update outlet |
| `/api/admin/settings/outlets/{id}/` | DELETE | Delete outlet (soft) |
| `/api/admin/settings/outlets/stats/` | GET | Get outlet statistics |
| `/api/admin/settings/outlets/bulk_update/` | POST | Bulk update outlets |

**GET /api/admin/settings/outlets/**

Query Parameters:
- `search`: Search in name, address, city, phone, email
- `is_active`: Filter by status (true/false)
- `city`: Filter by city
- `province`: Filter by province
- `ordering`: Sort field (name, city, created_at)
- `page`: Page number
- `page_size`: Items per page

Example:
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/admin/settings/outlets/?city=Jakarta&is_active=true&page_size=20"
```

Response:
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/admin/settings/outlets/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant": 1,
      "tenant_name": "My Restaurant",
      "name": "Downtown Branch",
      "slug": "downtown-branch",
      "address": "123 Main Street",
      "city": "Jakarta",
      "province": "DKI Jakarta",
      "postal_code": "12345",
      "phone": "+6281234567890",
      "email": "downtown@restaurant.com",
      "latitude": "-6.200000",
      "longitude": "106.816666",
      "opening_time": "10:00:00",
      "closing_time": "22:00:00",
      "operating_hours": "10:00 - 22:00",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**POST /api/admin/settings/outlets/**
```bash
curl -X POST http://localhost:8000/api/admin/settings/outlets/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Branch",
    "address": "456 Oak Avenue",
    "city": "Jakarta",
    "province": "DKI Jakarta",
    "postal_code": "54321",
    "phone": "+6289876543210",
    "email": "newbranch@restaurant.com",
    "latitude": "-6.250000",
    "longitude": "106.850000",
    "opening_time": "09:00:00",
    "closing_time": "23:00:00",
    "is_active": true
  }'
```

**GET /api/admin/settings/outlets/stats/**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/outlets/stats/
```

Response:
```json
{
  "total": 10,
  "active": 8,
  "inactive": 2,
  "by_city": {
    "Jakarta": 5,
    "Bandung": 3,
    "Surabaya": 2
  },
  "by_province": {
    "DKI Jakarta": 5,
    "West Java": 3,
    "East Java": 2
  }
}
```

**POST /api/admin/settings/outlets/bulk_update/**
```bash
curl -X POST http://localhost:8000/api/admin/settings/outlets/bulk_update/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "outlet_ids": [1, 2, 3],
    "updates": {
      "is_active": false
    }
  }'
```

Response:
```json
{
  "status": "success",
  "message": "3 outlets updated successfully",
  "updated_count": 3
}
```

### Frontend Implementation

#### Settings Page (`admin/src/routes/settings/+page.svelte`)

**Two-Tab Interface**:
1. **Tenant Settings Tab**: Business and branding configuration
2. **Outlets Tab**: Outlet management and statistics

#### Tenant Settings Tab

**1. Logo Management Section**
- Display current logo (if exists) or placeholder
- Upload logo button with file picker
- Logo preview before upload
- Delete logo functionality
- File validation:
  - Must be image file
  - Maximum size: 2MB
  - Supported formats: PNG, JPG, JPEG, GIF

**2. Business Information Section**
- **Tenant Name** (required): Business name
- **Phone**: Contact phone number
- **Email**: Contact email with format validation
- **Website**: Business website URL
- **Description**: Multi-line business description

**3. Branding Colors Section**
- **Primary Color**: Main brand color with color picker
- **Secondary Color**: Secondary brand color with color picker
- Color validation: Must be valid hex format (#RRGGBB)
- Visual color pickers for easy selection
- Text input for manual hex code entry

**4. Financial Settings Section**
- **Tax Rate**: Percentage tax rate (e.g., 10.00%)
- **Service Charge**: Percentage service charge (e.g., 5.00%)
- Decimal precision up to 2 places
- Range: 0.00 to 100.00

**Features**:
- Real-time form validation
- Save button to update all settings
- Loading states during save
- Success/error notifications
- Auto-populate from current settings

#### Outlets Tab

**1. Statistics Dashboard**
- **Total Outlets**: Count of all outlets
- **Active Outlets**: Count of active outlets
- **Inactive Outlets**: Count of inactive outlets
- **Cities**: Count of unique cities

**2. Filter System**
- **Search**: Search by name, address, city, phone, email
- **Status Filter**: All, Active, Inactive
- **City Filter**: Dropdown of available cities
- **Province Filter**: Dropdown of available provinces
- Real-time filtering with debouncing

**3. Outlets Table**

Columns:
- **Checkbox**: Multi-select for bulk operations
- **Outlet**: Name with icon and ID
- **Location**: City, province, and address
- **Contact**: Phone and email
- **Operating Hours**: Formatted time range
- **Status**: Active/Inactive badge
- **Actions**: Edit, Delete buttons

**4. Bulk Operations**
- Select multiple outlets with checkboxes
- "Activate Selected" button
- "Deactivate Selected" button
- Selection counter display
- Shift-click for range selection

**5. Create/Edit Outlet Modal**

Form Fields:
- **Outlet Name** (required)
- **Status**: Active checkbox
- **Address** (required): Full address textarea
- **City** (required)
- **Province**
- **Postal Code**
- **Phone** (required)
- **Email**: With format validation
- **Latitude**: GPS coordinate
- **Longitude**: GPS coordinate
- **Opening Time**: Time picker
- **Closing Time**: Time picker

Validation:
- Required field checks
- Email format validation
- Prevents submission with errors
- Shows error messages inline

**6. Delete Confirmation Modal**
- Shows outlet name for confirmation
- Warning message about deactivation
- Confirm/Cancel buttons

**7. Pagination**
- Page size selector (10, 25, 50 items)
- Previous/Next navigation
- Current page indicator
- Total count display

#### API Client (`admin/src/lib/api/settings.js`)

**Tenant Settings Functions**:
```javascript
// Get tenant settings
await getTenantSettings();

// Update tenant settings
await updateTenantSettings(tenantId, {
  name: 'New Name',
  primary_color: '#FF0000'
});

// Upload logo
await uploadTenantLogo(tenantId, logoFile);

// Delete logo
await deleteTenantLogo(tenantId);
```

**Outlet Management Functions**:
```javascript
// List outlets with filters
await getOutlets({
  search: 'downtown',
  city: 'Jakarta',
  is_active: true,
  page: 1,
  page_size: 10
});

// Get statistics
await getOutletStats();

// Create outlet
await createOutlet({
  name: 'New Branch',
  address: '123 Main St',
  city: 'Jakarta',
  phone: '+6281234567890',
  is_active: true
});

// Update outlet
await updateOutlet(outletId, { name: 'Updated Name' });

// Delete outlet
await deleteOutlet(outletId);

// Bulk update
await bulkUpdateOutlets([1, 2, 3], { is_active: false });
```

**Utility Functions**:
```javascript
// Format operating hours
formatOperatingHours('10:00:00', '22:00:00');
// Returns: "10:00 AM - 10:00 PM"

// Format address
formatAddress(outlet);
// Returns: "123 Main St, Jakarta, DKI Jakarta, 12345"

// Validate hex color
isValidHexColor('#FF6B35');
// Returns: true

// Get status badge
getStatusBadge(true);
// Returns: { label: 'Active', colorClass: 'bg-green-100 text-green-800' }

// Extract cities list
getCitiesList(outlets);
// Returns: ['Jakarta', 'Bandung', 'Surabaya']
```

## Key Features

### Tenant Settings
✅ **Logo Management** - Upload, preview, and delete tenant logos
✅ **Business Info** - Name, contact details, website
✅ **Brand Customization** - Primary and secondary colors with pickers
✅ **Financial Config** - Tax rate and service charge settings
✅ **Form Validation** - Required fields, email format, color format
✅ **Real-time Preview** - See changes before saving
✅ **Auto-save** - Single save button for all settings

### Outlet Management
✅ **CRUD Operations** - Create, Read, Update, Delete outlets
✅ **Statistics Dashboard** - Real-time outlet counts and distribution
✅ **Advanced Filtering** - Search, status, city, province filters
✅ **Bulk Operations** - Multi-select and bulk activate/deactivate
✅ **Operating Hours** - Time pickers for opening and closing times
✅ **Location Tracking** - GPS coordinates (latitude/longitude)
✅ **Soft Delete** - Deactivate instead of permanent deletion
✅ **Pagination** - Handle large numbers of outlets efficiently

### Multi-tenant Support
✅ **Tenant Isolation** - Users only see their tenant's data
✅ **Super Admin Access** - Super admin can manage all tenants
✅ **Auto-assignment** - Outlets automatically assigned to user's tenant
✅ **Permission Control** - Admin, Owner, Manager only

## Testing Guide

### Prerequisites
```bash
# Ensure backend is running
cd /home/user/webapp
docker-compose up backend -d

# Ensure admin frontend is running
docker-compose up admin -d

# Restart backend to load new endpoints
docker-compose restart backend
docker-compose logs -f backend
```

### Backend Testing

#### 1. Test Get Tenant Settings
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/tenant/
```

Expected: JSON with tenant details

#### 2. Test Update Tenant Settings
```bash
curl -X PATCH http://localhost:8000/api/admin/settings/tenant/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Restaurant", "tax_rate": "12.00"}'
```

Expected: Updated tenant object

#### 3. Test Upload Logo
```bash
# Create a test image first
curl -X POST http://localhost:8000/api/admin/settings/tenant/1/upload_logo/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "logo=@/path/to/test-logo.png"
```

Expected: Success message with logo URL

#### 4. Test List Outlets
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/outlets/
```

Expected: Paginated list of outlets

#### 5. Test Create Outlet
```bash
curl -X POST http://localhost:8000/api/admin/settings/outlets/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Branch",
    "address": "123 Test Street",
    "city": "Jakarta",
    "province": "DKI Jakarta",
    "postal_code": "12345",
    "phone": "+6281234567890",
    "is_active": true
  }'
```

Expected: Created outlet object

#### 6. Test Outlet Statistics
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/outlets/stats/
```

Expected: Statistics object with counts

#### 7. Test Bulk Update
```bash
curl -X POST http://localhost:8000/api/admin/settings/outlets/bulk_update/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"outlet_ids": [1, 2], "updates": {"is_active": false}}'
```

Expected: Success message with updated count

### Frontend Testing

#### 1. Access Settings Page
1. Open http://localhost:5175/settings
2. Should see two tabs: "Tenant Settings" and "Outlets"
3. Default tab should be active

#### 2. Test Tenant Settings Tab

**Logo Management**:
- [ ] If no logo: Should see placeholder with "Upload Logo" button
- [ ] Click "Upload Logo" button
- [ ] File picker should open
- [ ] Select image file (PNG/JPG)
- [ ] Should see preview of selected image
- [ ] Click "Upload" button
- [ ] Logo should upload and display
- [ ] "Delete Logo" button should appear
- [ ] Click "Delete Logo"
- [ ] Logo should be removed

**Business Information**:
- [ ] All fields should be populated with current data
- [ ] Modify Tenant Name
- [ ] Modify Phone, Email, Website
- [ ] Edit Description in textarea
- [ ] Try invalid email format → should show error
- [ ] Try empty tenant name → should show error

**Branding Colors**:
- [ ] Click primary color picker
- [ ] Select new color
- [ ] Color should update in text field
- [ ] Manually type hex code (e.g., #FF0000)
- [ ] Color picker should update
- [ ] Try invalid hex code → should show error
- [ ] Repeat for secondary color

**Financial Settings**:
- [ ] Modify Tax Rate (e.g., 11.50)
- [ ] Modify Service Charge (e.g., 6.00)
- [ ] Values should accept decimals

**Save Settings**:
- [ ] Click "Save Settings" button
- [ ] Button should show "Saving..." during request
- [ ] Success alert should appear
- [ ] Refresh page to verify changes persisted

#### 3. Test Outlets Tab

**Statistics Dashboard**:
- [ ] Total Outlets count displayed
- [ ] Active Outlets count displayed
- [ ] Inactive Outlets count displayed
- [ ] Cities count displayed
- [ ] All counts should be accurate

**Filter System**:
- [ ] Type in search box
- [ ] Wait for debounce (500ms)
- [ ] Table should filter results
- [ ] Select status filter (Active/Inactive)
- [ ] Table should update
- [ ] Select city filter
- [ ] Table should filter by city
- [ ] Clear filters → all outlets shown

**Outlets Table**:
- [ ] Outlets displayed in table
- [ ] Checkbox column for selection
- [ ] Outlet name and ID shown
- [ ] Location details (city, province, address)
- [ ] Contact info (phone, email)
- [ ] Operating hours formatted correctly
- [ ] Status badge color-coded (green=active, red=inactive)
- [ ] Edit and Delete buttons present

**Create Outlet**:
- [ ] Click "Add Outlet" button
- [ ] Modal should open
- [ ] Fill required fields: Name, Address, City, Phone
- [ ] Fill optional fields
- [ ] Set opening and closing times
- [ ] Check "Active" checkbox
- [ ] Click "Create Outlet"
- [ ] New outlet should appear in table
- [ ] Success alert shown

**Edit Outlet**:
- [ ] Click Edit button on an outlet
- [ ] Modal should open with outlet data
- [ ] Modify outlet name
- [ ] Change operating hours
- [ ] Click "Update Outlet"
- [ ] Changes should reflect in table
- [ ] Success alert shown

**Delete Outlet**:
- [ ] Click Delete button on test outlet
- [ ] Confirmation modal should open
- [ ] Outlet name should be shown
- [ ] Click "Cancel" → modal closes, no deletion
- [ ] Click Delete again
- [ ] Click "Delete Outlet" → outlet removed
- [ ] Success alert shown

**Bulk Operations**:
- [ ] Check checkboxes for 2-3 outlets
- [ ] Bulk actions toolbar should appear
- [ ] Shows count of selected outlets
- [ ] Click "Deactivate Selected"
- [ ] Selected outlets become inactive
- [ ] Status badges update to red
- [ ] Check them again
- [ ] Click "Activate Selected"
- [ ] Outlets become active again

**Select All**:
- [ ] Click checkbox in table header
- [ ] All outlets on page selected
- [ ] Click again → all deselected

**Pagination**:
- [ ] If more than 10 outlets, pagination appears
- [ ] Click "Next" → shows next page
- [ ] Click "Previous" → goes back
- [ ] Change page size (25, 50)
- [ ] Table updates with new page size
- [ ] Counter shows "Showing X-Y of Z" correctly

#### 4. Test Form Validations

**Tenant Settings**:
- [ ] Clear tenant name → error shown
- [ ] Enter invalid email → error shown
- [ ] Enter invalid hex color → error shown
- [ ] Form prevents submission with errors

**Outlet Form**:
- [ ] Try to save without name → error shown
- [ ] Try to save without address → error shown
- [ ] Try to save without city → error shown
- [ ] Try to save without phone → error shown
- [ ] Enter invalid email → error shown
- [ ] Form prevents submission with errors

#### 5. Test Responsive Design
- [ ] Resize browser window
- [ ] Mobile view: Filters stack vertically
- [ ] Mobile view: Table scrolls horizontally
- [ ] Mobile view: Modal is full-screen
- [ ] Desktop view: Layout uses grid properly

## Troubleshooting

### Issue: 404 Error on Settings Endpoints

**Cause**: Backend container not restarted after adding new views

**Solution**:
```bash
cd /home/user/webapp
docker-compose restart backend
docker-compose logs -f backend
```

### Issue: Settings Page Not Loading

**Cause**: Frontend not detecting new route

**Solution**:
```bash
cd /home/user/webapp
docker-compose restart admin
# Hard refresh browser: Ctrl+Shift+R
```

### Issue: "No tenant found" Error

**Cause**: User not associated with a tenant

**Solution**: Verify user has tenant association:
```bash
# Check user's tenant
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/tenants/me/
```

### Issue: Logo Upload Failing

**Cause**: File size too large or wrong format

**Solution**:
- Ensure image file is less than 2MB
- Use supported formats: PNG, JPG, JPEG, GIF
- Check media directory permissions

### Issue: Outlet Creation Fails

**Cause**: Tenant auto-assignment not working

**Solution**: Verify TenantMiddleware is setting tenant context:
```python
# In backend/apps/tenants/middleware.py
def process_request(self, request):
    tenant_id = request.META.get('HTTP_X_TENANT_ID')
    if tenant_id:
        set_current_tenant(int(tenant_id))
```

### Issue: Colors Not Updating

**Cause**: Invalid hex format

**Solution**: Ensure color format is #RRGGBB (6 hex digits with # prefix)

### Issue: Statistics Not Loading

**Cause**: Outlets query returning empty

**Solution**:
```bash
# Test stats endpoint directly
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/outlets/stats/
```

## Security Considerations

### File Upload Security
- File type validation (images only)
- File size limit (2MB)
- Secure file storage in media directory
- Automatic deletion of old logo on replacement

### Data Validation
- Required field validation
- Email format validation
- Hex color format validation
- Phone number validation
- Decimal precision for financial settings

### Access Control
- Authentication required for all endpoints
- Role-based permissions (Admin, Owner, Manager)
- Multi-tenant data isolation
- Super admin bypass for maintenance

### Soft Delete
- Outlets use soft delete (is_active=False)
- Data preserved for audit trail
- Can be reactivated if needed

## Performance Optimization

### Backend
- Efficient queryset filtering
- select_related for tenant joins
- Pagination to limit data transfer
- Database indexes on commonly filtered fields

### Frontend
- Debounced search (500ms)
- Lazy loading of tabs
- Efficient re-rendering with Svelte
- Pagination to limit DOM size

### Recommended Indexes
```python
class Outlet(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['tenant', 'city']),
            models.Index(fields=['city', 'province']),
            models.Index(fields=['name']),
        ]
```

## Future Enhancements

### Short-term
- [ ] Outlet map view with Google Maps integration
- [ ] Import outlets from CSV
- [ ] Export outlets to CSV
- [ ] Outlet photos/gallery
- [ ] Operating hours by day of week

### Medium-term
- [ ] Multi-language support
- [ ] Outlet performance metrics
- [ ] Delivery radius configuration
- [ ] Staff assignment per outlet
- [ ] Equipment/inventory per outlet

### Long-term
- [ ] Franchise management features
- [ ] Regional manager assignments
- [ ] Advanced analytics per outlet
- [ ] Customer reviews per outlet
- [ ] Automated outlet reporting

## Conclusion

The Settings Management feature provides a comprehensive solution for managing tenant and outlet configurations. It offers an intuitive interface for business settings, branding customization, and multi-location management.

**Key Benefits**:
✅ Centralized configuration management
✅ Easy branding customization
✅ Efficient multi-outlet management
✅ Comprehensive filtering and search
✅ Bulk operations for productivity
✅ Real-time statistics and insights
✅ Mobile-responsive design
✅ Secure file upload handling

**Next Steps**:
1. Restart backend container to load new endpoints
2. Test all functionality using the testing guide
3. Configure production media storage (S3, etc.)
4. Set up CDN for logo delivery
5. Configure backup for uploaded images

---
**Documentation Version**: 1.0
**Last Updated**: 2024-12-28
**Feature Completion**: 100%
