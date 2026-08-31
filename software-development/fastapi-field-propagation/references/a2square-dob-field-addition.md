# A2Square — DOB Field Addition to Admin Update Profile

## Context
A2Square Tapease Portal Backend, version 3.3.14 on `openclaw_auto` branch. Deployed version 4.1.07 on `card-integration` branch.

## Error Cascade
Four errors reported from frontend (localhost:3000/admin/cards-management):

1. `/admin/update_user_profile` → `"Extra inputs are not permitted"` on `dob` field
2. `/admin/cards/assign` → `"Missing required KYC fields: dob, license_no, license_expiry"`
3. `/admin/cards/assign` → `"Unexpected connection error: UnsupportedProtocol"`
4. `/admin/cards/5/kyc` → `"No card has been assigned to this user"`

Root cause: `AdminUpdateUserProfileRequest` model had `extra="forbid"` and no `dob` field.

## Files Changed

### app/models/admin.py
Added 3 fields to `AdminUpdateUserProfileRequest`:
- `dob: Optional[str]` (max_length=50, YYYY-MM-DD format)
- `middle_name: Optional[str]` (max_length=100)
- `street_number: Optional[str]` (max_length=20)

### app/routers/admin_users.py
Added to service call:
```python
dob=update_data.dob,
middle_name=update_data.middle_name,
street_number=update_data.street_number,
```

### app/services/admin_user_service.py
Added 3 params + 3 SQL update blocks following the dynamic query builder pattern.

## Still Open
- Card 502 `UnsupportedProtocol` — needs CARD_SERVICE_BASE_URL config or merge from card-integration branch
