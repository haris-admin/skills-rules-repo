# AML Hive Production RDS Schema (July 2026)

**Endpoint:** `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`
**User:** `amlhive`  
**Database:** `amlhive` (NOT `amlhive_prod`)
**SSL:** Required (`PGSSLMODE=require`)
**Password:** Secrets Manager `amlhive/prod/rds`

## Key Tables and Their Columns

### agencies
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| name | text | |
| abn | text | |
| subscription_tier | text | |
| is_active | boolean | ✅ Exists |
| lifecycle_status | text | Values: `active`, `trial`, `onboarding`, `cancelled` |
| created_at | timestamptz | |
| updated_at | timestamptz | |

### users
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| agency_id | uuid | FK |
| email | text | |
| role | text | |
| is_active | boolean | |
| is_approved | boolean | |
| created_at | timestamptz | |
| activated_at | timestamptz | |

### employee_screening_records
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| screen_type | text | |
| total_hits | integer | |
| **outcome** | text | ⚠️ Values: `CLEAN`, `HIT` (UPPERCASE) |
| **decision** | text | Values: `FALSE_POSITIVE` or NULL |
| performed_at | timestamptz | ⚠️ NOT `created_at` |

### kyc_identities
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| verification_provider | text | |
| **verification_status** | text | ⚠️ Values: `VERIFIED`, `PENDING`, `EXPIRED`, `FAILED`, `REFER` (UPPERCASE) |
| confidence_score | double | |
| verified_at | timestamptz | |
| created_at | timestamptz | |

### kyb_records
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| entity_name | text | |
| abn | text | |
| acn | text | |
| entity_type | text | |
| **status** | text | ⚠️ NOT `verification_status`. Values: `Active` (mixed case) |
| verified_at | timestamptz | |
| created_at | timestamptz | |
| gst_registered | text | |

### matters
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| status | text | Values: `open`, `active`, `closed` |
| property_address | text | |
| matter_ref | text | |
| created_at | timestamptz | |

### clients
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| **is_archived** | boolean | ⚠️ NOT `is_active`. For active clients: `WHERE is_archived=false OR is_archived IS NULL` |
| client_type | text | |
| created_at | timestamptz | |

### cdd_checklists
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| **status** | text | ⚠️ Values: `IN_PROGRESS`, `SIGNED_OFF` (UPPERCASE) |
| cdd_type | text | |
| risk_tier | text | |
| created_at | timestamptz | (actually doesn't exist — uses a different column, verify before use) |

### audit_entries
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| action_type | text | |
| performed_at | timestamptz | ⚠️ NOT `created_at` |
| outcome | text | |

### platform_audit_log
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| **platform_user_id** | uuid | ⚠️ NOT `user_id` |
| action | text | |
| performed_at | timestamptz | ⚠️ NOT `created_at` |

## Troubleshooting Checklist

If the daily report fails with table/column errors:

1. **Check table exists:** `SELECT table_name FROM information_schema.tables WHERE table_schema='public'`
2. **Check columns:** `SELECT column_name FROM information_schema.columns WHERE table_name='<table>' ORDER BY ordinal_position`
3. **Check UPPERCASE values:** `SELECT status, COUNT(*) FROM <table> GROUP BY status`
4. **Install psql if new instance:** `sudo yum install -y postgresql15` on the backend EC2
5. **Verify backend EC2 ID:** `aws ec2 describe-instances --filters "Name=tag:Name,Values=amlhive-prod" --query "Reservations[].Instances[].InstanceId"`

## Schema Change History

| Date | Change |
|------|--------|
| Pre-Jul 2026 | Old RDS: `c9aso80ocbn0`, DB `amlhive_prod`, tables `screenings`, `kyc`, `kyb`, `cdd`, `user_sessions` |
| ~Jul 16 2026 | New RDS: `ch4ykiy82n3q`, DB `amlhive`. Tables renamed: `employee_screening_records`, `kyc_identities`, `kyb_records`, `cdd_checklists`, `platform_audit_log`. Status values now UPPERCASE. |
