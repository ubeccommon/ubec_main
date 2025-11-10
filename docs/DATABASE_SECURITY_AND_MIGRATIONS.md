# UBEC Protocol Suite - Database Security & Migration Guide

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Author:** UBEC Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Security Model](#security-model)
3. [User Roles & Permissions](#user-roles--permissions)
4. [Migration Infrastructure](#migration-infrastructure)
5. [Common Tasks](#common-tasks)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Overview

This document describes the UBEC Protocol Suite's database security model and migration infrastructure. The system implements a **three-tier permission model** that follows the **Principle of Least Privilege** to ensure maximum security while maintaining operational efficiency.

### Design Principles Applied

- **Principle #4**: Database as single source of truth
- **Principle #6**: No sync fallbacks or backward compatibility layers
- **Principle #10**: Clear separation of concerns
- **Principle #11**: Comprehensive documentation

---

## Security Model

### Philosophy

**"Defense in Depth"** - Multiple layers of security prevent unauthorized access and accidental damage:

1. **Network Layer**: Firewall rules restrict database access
2. **Authentication Layer**: Strong passwords, connection limits
3. **Authorization Layer**: Role-based permissions (this document's focus)
4. **Application Layer**: Input validation, prepared statements
5. **Audit Layer**: All schema changes tracked

### Three-Tier Permission Model

```
┌─────────────────────────────────────────────────────────────┐
│                    PERMISSION HIERARCHY                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                          │
│  │   postgres   │  ← Superuser (emergency only)            │
│  └──────────────┘                                          │
│         │                                                   │
│         ├─────────────┐                                    │
│         │             │                                     │
│  ┌──────▼─────┐ ┌────▼──────┐ ┌──────────────┐           │
│  │ ubec_admin │ │ ubec_app  │ │ ubec_monitor │           │
│  │  (Admin)   │ │ (Runtime) │ │ (Read-Only)  │           │
│  └────────────┘ └───────────┘ └──────────────┘           │
│       │              │                │                     │
│   Schema Mgmt    Data Ops      Monitoring                  │
│   ALTER/DROP   INSERT/UPDATE    SELECT only                │
│   CREATE         DELETE                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## User Roles & Permissions

### 1. ubec_monitor (Read-Only)

**Purpose:** Monitoring, reporting, analytics, auditing  
**Use Cases:** Grafana, monitoring tools, data analysis, compliance reports

**Permissions:**
```sql
GRANT CONNECT ON DATABASE ubec TO ubec_monitor;
GRANT USAGE ON SCHEMA ubec_main TO ubec_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA ubec_main TO ubec_monitor;
```

**Can:**
- ✓ SELECT (read) data from all tables
- ✓ Execute read-only queries
- ✓ Generate reports

**Cannot:**
- ✗ INSERT, UPDATE, DELETE data
- ✗ ALTER, DROP, CREATE objects
- ✗ Modify any database structure

**Security Benefits:**
- Compromised monitoring tools cannot damage data
- Read-only access prevents accidental modifications
- Clear audit trail of who read what data

---

### 2. ubec_app (Application Runtime)

**Purpose:** Normal application operations  
**Use Cases:** Python application, API server, scheduled jobs

**Permissions:**
```sql
GRANT CONNECT ON DATABASE ubec TO ubec_app;
GRANT USAGE ON SCHEMA ubec_main TO ubec_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ubec_main TO ubec_app;
-- Note: NO ALTER, DROP, or CREATE permissions
```

**Can:**
- ✓ SELECT (read) data
- ✓ INSERT new records
- ✓ UPDATE existing records
- ✓ DELETE records
- ✓ Execute functions

**Cannot:**
- ✗ ALTER table structure
- ✗ DROP tables or columns
- ✗ CREATE new tables
- ✗ ADD/DROP constraints
- ✗ MODIFY triggers

**Security Benefits:**
- SQL injection attacks cannot modify schema
- Compromised application cannot drop tables
- Buggy code cannot accidentally alter structure
- Clear separation: data operations vs structure operations

**Critical Rule:** 
> **ubec_app must NOT own any tables.** If ubec_app owns a table, it can ALTER it, violating the security model.

---

### 3. ubec_admin (Schema Management)

**Purpose:** Database structure management, migrations  
**Use Cases:** Schema migrations, constraint modifications, table creation

**Permissions:**
```sql
GRANT ALL PRIVILEGES ON DATABASE ubec TO ubec_admin;
-- ubec_admin is the OWNER of all tables in ubec_main schema
```

**Can:**
- ✓ Everything ubec_app can do (SELECT, INSERT, UPDATE, DELETE)
- ✓ ALTER tables, columns, constraints
- ✓ CREATE and DROP tables
- ✓ MODIFY indexes, triggers, functions
- ✓ GRANT/REVOKE permissions

**Cannot:**
- ✗ Access other databases (unless explicitly granted)
- ✗ Modify postgres system tables (not a superuser)

**Security Benefits:**
- Schema changes are deliberate and tracked
- Clear ownership model (ubec_admin owns structure)
- Separate credentials reduce blast radius of compromise

**Critical Rule:**
> **ubec_admin credentials should NOT be in application .env file.** Only in secure admin environment.

---

## Migration Infrastructure

### Overview

All schema changes must go through the migration system. This ensures:

1. **Version Control**: Every schema change is tracked
2. **Auditability**: Who made what change when
3. **Repeatability**: Migrations can be applied to multiple environments
4. **Rollback Capability**: Each migration includes rollback instructions
5. **Verification**: Post-migration checks confirm success

### Components

```
database/
├── migrations/
│   ├── 000_create_migration_tracking.sql   # Creates tracking table
│   ├── TEMPLATE_migration.sql              # Template for new migrations
│   ├── 20251110_1500_fix_scheduler_job_functions.sql  # Example migration
│   └── [future migrations...]
scripts/
├── run_migration.sh          # Execute migrations safely
├── view_migrations.sh        # View migration history
└── check_permissions.sh      # Verify security model
```

### Files Created

#### 1. Migration Tracking Table
**File:** `database/migrations/000_create_migration_tracking.sql`

Creates the `ubec_main.schema_migrations` table that tracks all schema changes:

```sql
CREATE TABLE ubec_main.schema_migrations (
    migration_id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
    applied_by VARCHAR(100) NOT NULL,
    description TEXT,
    checksum VARCHAR(64),
    execution_time_ms INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    error_message TEXT,
    rollback_script TEXT
);
```

#### 2. Migration Runner Script
**File:** `scripts/run_migration.sh`

Safely executes migrations with proper user and error handling.

**Features:**
- Verifies database connection before running
- Checks if migration already applied
- Calculates checksum for integrity verification
- Records execution time
- Tracks failures with error messages
- Provides detailed output and confirmation

#### 3. Migration Template
**File:** `database/migrations/TEMPLATE_migration.sql`

Standard template for creating new migrations. Copy this file and fill in the placeholders.

#### 4. View Migrations Script
**File:** `scripts/view_migrations.sh`

View migration history and status.

#### 5. Check Permissions Script
**File:** `scripts/check_permissions.sh`

Verify database security model is correctly configured.

---

## Common Tasks

### Setup: First-Time Installation

#### Step 1: Make Scripts Executable

```bash
chmod +x scripts/run_migration.sh
chmod +x scripts/view_migrations.sh
chmod +x scripts/check_permissions.sh
```

#### Step 2: Create Migration Tracking Table

```bash
./scripts/run_migration.sh database/migrations/000_create_migration_tracking.sql
```

#### Step 3: Verify Security Model

```bash
sudo ./scripts/check_permissions.sh
```

Expected output should show:
- ✓ All three users exist (ubec_admin, ubec_app, ubec_monitor)
- ✓ ubec_admin owns tables
- ✓ ubec_app cannot ALTER tables

---

### Task 1: Create a New Migration

#### Step 1: Copy Template

```bash
# Create migration with current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M)
cp database/migrations/TEMPLATE_migration.sql \
   database/migrations/${TIMESTAMP}_your_description.sql
```

Example:
```bash
cp database/migrations/TEMPLATE_migration.sql \
   database/migrations/20251110_1600_add_audit_log_table.sql
```

#### Step 2: Edit Migration File

Open the file and:
1. Fill in all `[bracketed]` placeholders
2. Write your SQL between `BEGIN` and `COMMIT`
3. Add verification queries
4. Include rollback script in comments

#### Step 3: Test on Development Database

```bash
# Run on dev database first
./scripts/run_migration.sh 20251110_1600_add_audit_log_table.sql
```

#### Step 4: Review Migration History

```bash
./scripts/view_migrations.sh --recent 5
```

#### Step 5: Apply to Production

After testing succeeds:

```bash
# On production server
./scripts/run_migration.sh 20251110_1600_add_audit_log_table.sql
```

---

### Task 2: Fix the Scheduler Jobs Issue

This is the specific fix for the issue you encountered.

```bash
# Execute the fix migration
./scripts/run_migration.sh 20251110_1500_fix_scheduler_job_functions.sql

# Verify it worked
psql -U ubec_app -d ubec -h localhost -c \
  "SELECT job_name, job_function FROM ubec_main.scheduler_jobs;"

# Restart the UBEC server
python main.py serve
```

Expected result:
- ✓ All job_function values now in format: `service_name.method_name`
- ✓ Constraint prevents future invalid formats
- ✓ report_generation job executes successfully

---

### Task 3: View Migration History

#### View Summary (Default)

```bash
./scripts/view_migrations.sh
```

Shows:
- Total migrations
- Completed vs failed count
- Latest migration applied

#### View All Migrations

```bash
./scripts/view_migrations.sh --all
```

#### View Recent Migrations

```bash
# Last 10 (default)
./scripts/view_migrations.sh --recent

# Last 20
./scripts/view_migrations.sh --recent 20
```

#### View Specific Migration Details

```bash
./scripts/view_migrations.sh --detail 20251110_1500_fix_scheduler_job_functions
```

#### View Failed Migrations

```bash
./scripts/view_migrations.sh --failed
```

---

### Task 4: Check Database Permissions

```bash
# Requires sudo to access postgres user
sudo ./scripts/check_permissions.sh
```

Output shows:
- User existence and details
- Database and schema ownership
- Table permissions for each user
- Whether security model is correctly configured

---

### Task 5: Rollback a Migration

Migrations include rollback scripts in comments at the bottom of the file.

#### Step 1: Find Rollback Script

Open the migration file and locate the rollback section at the bottom:

```sql
-- ============================================================================
-- Rollback Script (Keep in comments for reference)
-- ============================================================================
-- BEGIN;
-- -- Rollback commands here
-- COMMIT;
```

#### Step 2: Execute Rollback

```bash
# Connect as ubec_admin
psql -U ubec_admin -d ubec -h localhost

# Copy and paste the rollback commands
BEGIN;
-- [rollback commands from migration file]
COMMIT;
```

#### Step 3: Mark as Rolled Back

```sql
UPDATE ubec_main.schema_migrations 
SET status = 'rolled_back', 
    error_message = 'Manual rollback executed'
WHERE migration_name = '20251110_XXXX_migration_name';
```

---

### Task 6: Grant Permissions to New User

If you need to create a new user with specific permissions:

```bash
# Connect as postgres
sudo -u postgres psql -d ubec
```

#### Read-Only User (Like ubec_monitor)

```sql
CREATE ROLE new_readonly_user WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE ubec TO new_readonly_user;
GRANT USAGE ON SCHEMA ubec_main TO new_readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA ubec_main TO new_readonly_user;

-- Make it apply to future tables too
ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main
    GRANT SELECT ON TABLES TO new_readonly_user;
```

#### Application User (Like ubec_app)

```sql
CREATE ROLE new_app_user WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE ubec TO new_app_user;
GRANT USAGE ON SCHEMA ubec_main TO new_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ubec_main TO new_app_user;

-- Make it apply to future tables too
ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO new_app_user;
```

---

## Troubleshooting

### Problem: "must be owner of table" Error

**Symptom:**
```
ERROR: must be owner of table scheduler_jobs
```

**Cause:** You're trying to ALTER a table with a user that doesn't own it.

**Solution:** Use ubec_admin for schema changes:

```bash
# Instead of:
psql -U ubec_app -d ubec -c "ALTER TABLE ..."

# Use:
psql -U ubec_admin -d ubec -c "ALTER TABLE ..."

# Or better, create a migration:
./scripts/run_migration.sh your_migration.sql
```

---

### Problem: Migration Already Applied

**Symptom:**
```
⚠ Migration already applied: 20251110_1500_fix_scheduler_job_functions
```

**Cause:** Migration was already executed.

**Solution:**

Check if migration actually succeeded:

```bash
./scripts/view_migrations.sh --detail 20251110_1500_fix_scheduler_job_functions
```

If status is 'completed', no action needed. If you want to re-run anyway:

```bash
./scripts/run_migration.sh 20251110_1500_fix_scheduler_job_functions.sql
# Answer "yes" when prompted
```

---

### Problem: Cannot Connect to Database

**Symptom:**
```
✗ Cannot connect to database as ubec_admin
```

**Solution:**

1. Check PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

2. Check credentials in `.env` file:
```bash
grep DB_ .env
```

3. Test connection manually:
```bash
psql -U ubec_admin -d ubec -h localhost -c "SELECT 1;"
```

4. If password wrong, update `.env`:
```bash
nano .env
# Update DB_ADMIN_USER and DB_ADMIN_PASSWORD
```

---

### Problem: Security Model Incorrect

**Symptom:**
```bash
sudo ./scripts/check_permissions.sh
# Shows:
⚠ ubec_app owns scheduler_jobs table - can ALTER (security concern)
```

**Cause:** Table ownership is incorrect.

**Solution:** Fix table ownership:

```bash
sudo -u postgres psql -d ubec <<EOF
-- Transfer ownership to ubec_admin
ALTER TABLE ubec_main.scheduler_jobs OWNER TO ubec_admin;
ALTER TABLE ubec_main.schema_migrations OWNER TO ubec_admin;
-- Repeat for other tables as needed
EOF
```

Verify:
```bash
sudo ./scripts/check_permissions.sh
```

---

## Best Practices

### DO ✓

1. **Always use migrations for schema changes**
   - Never ALTER tables directly in production
   - Use `run_migration.sh` script
   - Test on development first

2. **Use correct user for each task**
   - ubec_admin: Schema migrations only
   - ubec_app: Application runtime
   - ubec_monitor: Read-only operations

3. **Document all migrations**
   - Fill in description field
   - Include verification queries
   - Add rollback instructions

4. **Test migrations thoroughly**
   - Run on development database first
   - Verify with test queries
   - Check application still works

5. **Keep credentials secure**
   - ubec_admin password NOT in application `.env`
   - Store admin credentials in secure location
   - Rotate passwords quarterly

6. **Review migration history**
   - Use `view_migrations.sh` regularly
   - Check for failed migrations
   - Verify execution times

### DON'T ✗

1. **Don't grant ALTER to ubec_app**
   - Security risk
   - Violates principle of least privilege
   - Makes audit trail unclear

2. **Don't run migrations as postgres**
   - Use ubec_admin instead
   - Maintains clear ownership model
   - Easier to audit

3. **Don't skip verification**
   - Always include post-migration checks
   - Verify constraints exist
   - Check data integrity

4. **Don't make schema changes outside migrations**
   - No manual ALTER statements in production
   - No "quick fixes" bypassing migration system
   - All changes must be tracked

5. **Don't reuse migration names**
   - Each migration must have unique name
   - Use timestamp prefix (YYYYMMDD_HHMM)
   - Prevents conflicts

6. **Don't forget rollback scripts**
   - Every migration should have rollback
   - Test rollback on development
   - Document any manual steps needed

---

## Environment Variables

Update your `.env` file with both application and admin credentials:

```bash
# Application Database User (Runtime)
DB_USER=ubec_app
DB_PASSWORD=<app-secure-password>

# Admin Database User (Migrations Only)
# DO NOT use in application code
DB_ADMIN_USER=ubec_admin
DB_ADMIN_PASSWORD=<admin-secure-password>

# Monitor Database User (Read-Only)
DB_READONLY_USER=ubec_monitor
DB_READONLY_PASSWORD=<monitor-secure-password>

# Connection Details (Shared)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ubec
```

**Security Note:** Never commit `.env` file to version control!

---

## Summary

This infrastructure provides:

✓ **Security**: Three-tier permission model prevents unauthorized changes  
✓ **Auditability**: All schema changes tracked in database  
✓ **Repeatability**: Migrations work across environments  
✓ **Safety**: Verification and rollback for every migration  
✓ **Simplicity**: Helper scripts make operations easy  

Following these practices ensures your database remains secure, maintainable, and compliant with UBEC design principles.

---

**For questions or issues, refer to:**
- Design Principles: `README.md` (12 Project Design Principles)
- Database Schema: `ubec_comprehensive_doc_ubec_20251107_163408.md`
- System Admin Guide: `docs/User_Guides/SYSTEM_ADMINISTRATOR_ONBOARDING_GUIDE.md`

---

*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.*
