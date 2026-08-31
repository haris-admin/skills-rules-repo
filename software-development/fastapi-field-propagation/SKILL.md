---
name: fastapi-field-propagation
description: "Add a new field end-to-end through a FastAPI backend: Pydantic model → router → service → database. Covers the 3-layer propagation pattern and Pydantic extra='forbid' gotcha."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [fastapi, pydantic, backend, python, field-propagation]
    related_skills: [systematic-debugging, writing-plans, github-pr-workflow]
---

# FastAPI Field Propagation

## When to Use

Use this skill when you need to add a new database-backed field to an existing FastAPI endpoint. Specifically when:

- A request to an API endpoint fails with `"Extra inputs are not permitted"` — the field is being sent by the frontend but the Pydantic model rejects it
- Signup accepts a field but admin update doesn't (misaligned schemas)
- A downstream feature (KYC, card assignment, payout) requires a field that can't be saved through the admin interface

## The Three-Layer Propagation Pattern

Every database-backed field in a FastAPI app with a service layer must pass through **three files**:

```
┌─────────────────────────────────────────────────────────┐
│  1. MODEL (Pydantic schema)         models/admin.py      │
│     → Define the field + validation                      │
├─────────────────────────────────────────────────────────┤
│  2. ROUTER (API handler)           routers/admin_xxx.py  │
│     → Accept model → pass to service                     │
├─────────────────────────────────────────────────────────┤
│  3. SERVICE (business logic)    services/xxx_service.py  │
│     → Accept param → build SQL UPDATE → execute          │
└─────────────────────────────────────────────────────────┘
```

If any layer is missed, the field will be rejected (`extra="forbid"`), silently dropped, or won't reach the database.

---

## Step-by-Step Procedure

### Step 1: Check the Model

Look at the Pydantic request model for the endpoint. Every field must be explicitly defined — `extra="forbid"` rejects any undeclared field.

```python
# In app/models/admin.py:
class AdminUpdateUserProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # ← THIS IS THE GOTCHA
    user_id: int = Field(...)
    # ... existing fields ...
    # new_field: Optional[str] = Field(None, ...)  # ← NEEDS TO BE ADDED
```

**Action:** Add the new field as `Optional[...]` with appropriate `max_length` and `description`.

```python
    dob: Optional[str] = Field(
        None,
        max_length=50,
        description="Date of birth (max 50 characters, format: YYYY-MM-DD)",
        json_schema_extra={"example": "1983-01-06"},
    )
```

### Step 2: Check the Router

The router handler extracts the field from the request model and passes it to the service.

```python
# In app/routers/admin_xxx.py:
result = await some_service.update_profile(
    user_id=update_data.user_id,
    # ... existing fields ...
    dob=update_data.dob,  # ← NEEDS TO BE ADDED
)
```

**Action:** Add the `new_field=update_data.new_field` keyword argument to the service call.

### Step 3: Check the Service

The service method must:
1. Accept the new parameter (add it to the method signature)
2. Build a dynamic SQL UPDATE clause using it
3. Track it in the `updated_fields` list

```python
# In app/services/xxx_service.py:

# Step 3a: Add parameter to method signature
async def update_profile(
    self,
    user_id: int,
    # ... existing params ...
    dob: Optional[str] = None,  # ← ADD THIS
) -> Dict[str, Any]:

    # Step 3b: Add SQL update block in the dynamic query builder
    if dob is not None:
        update_fields.append(f"dob = ${param_index}")
        update_params.append(dob)
        param_index += 1
        updated_fields.append("dob")
```

**Action:** Add the parameter + SQL update block + field tracking.

---

## Verification

After making all three changes, verify compilation:

```bash
python3 -m py_compile app/models/admin.py
python3 -m py_compile app/routers/admin_xxx.py
python3 -m py_compile app/services/xxx_service.py
```

Then run a quick test against the endpoint to confirm the field is accepted and persisted.

---

## Common Pitfalls

### Pitfall 1: Missing a Layer
The most common mistake — adding the field to the model but forgetting the router or service. Each layer independently gates the field:
- **Model missing** → field rejected with `"Extra inputs are not permitted"`
- **Router missing** → field silently dropped (never reaches service)
- **Service missing** → field accepted by HTTP but never saved to database

### Pitfall 2: `extra="forbid"` in Pydantic
This config (used in most Tapease request models) means Pydantic actively rejects undeclared fields. If the field isn't in the model, the endpoint returns a 422 validation error before the router handler even runs. You can't work around this — the field must be declared.

### Pitfall 3: Field Exists in DB but Not in Signup or Admin
When adding a field, check BOTH the signup model (`models/auth.py`) and the admin update model (`models/admin.py`). If they diverge, the admin can't set fields that signup collects, blocking downstream flows like KYC.

### Pitfall 4: Dynamic SQL Parameter Ordering
The dynamic SQL builder uses `param_index` as a counter for `$1`, `$2`, etc. When inserting a new field block, the `param_index += 1` must be inside the `if` block, not outside it. Wrong:

```python
if dob is not None:
    update_fields.append(f"dob = ${param_index}")
    update_params.append(dob)
    # ← MISSING: param_index += 1
param_index += 1  # ← WRONG: increments even when dob is None
```

### Pitfall 5: Validators Can Block New Fields
After adding a field to the model, check if there are `@field_validator` decorators that might apply. Some validators (like `validate_date_format`) might reject your field format. When adding the same field to the admin model as exists in signup, copy the validator too.

---

## Quick Reference

| Layer | File | What to Add |
|-------|------|-------------|
| Model | `app/models/admin.py` | `new_field: Optional[str] = Field(...)` |
| Router | `app/routers/admin_xxx.py` | `new_field=update_data.new_field` in service call |
| Service param | `app/services/xxx_service.py` | `new_field: Optional[str] = None` in method signature |
| Service SQL | `app/services/xxx_service.py` | `if new_field is not None:` block in query builder |

## Related Skills

- **systematic-debugging** — For tracing error cascades when a missing field blocks downstream features (KYC, card assign, payouts). Use Phase 1 step 8.
- **github-pr-workflow** — For creating a PR with the field propagation changes.
- **writing-plans** — For planning a multi-field propagation across multiple endpoints.
