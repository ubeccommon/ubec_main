# UBEC Database Operations - Quick Reference Card

## 🚀 Quick Start

```bash
# Make scripts executable (one-time setup)
chmod +x scripts/*.sh

# Setup migration tracking (one-time setup)
./scripts/run_migration.sh database/migrations/000_create_migration_tracking.sql

# Check security model
sudo ./scripts/check_permissions.sh
```

---

## 📋 Common Commands

### Migrations

```bash
# Run a migration
./scripts/run_migration.sh YYYYMMDD_HHMM_description.sql
./scripts/run_migration.sh database/migrations/20251110_1500_fix_scheduler_job_functions.sql

# View migration history
./scripts/view_migrations.sh                    # Summary
./scripts/view_migrations.sh --all              # All migrations
./scripts/view_migrations.sh --recent 20        # Last 20
./scripts/view_migrations.sh --failed           # Failed only
./scripts/view_migrations.sh --detail <name>    # Specific migration

# Create new migration
TIMESTAMP=$(date +%Y%m%d_%H%M)
cp database/migrations/TEMPLATE_migration.sql \
   database/migrations/${TIMESTAMP}_your_description.sql
```

### Permissions

```bash
# Check permissions (requires sudo)
sudo ./scripts/check_permissions.sh

# Manual permission checks
psql -U ubec_admin -d ubec -c "SELECT tableowner FROM pg_tables WHERE schemaname='ubec_main';"
```

### Direct Database Access

```bash
# Connect as admin (for migrations)
psql -U ubec_admin -d ubec -h localhost

# Connect as app user (testing)
psql -U ubec_app -d ubec -h localhost

# Connect as postgres (emergency)
sudo -u postgres psql -d ubec
```

---

## 🔐 User Quick Reference

| User | Purpose | Can Do | Cannot Do |
|------|---------|--------|-----------|
| **ubec_admin** | Migrations | ALTER, CREATE, DROP tables | - |
| **ubec_app** | Runtime | SELECT, INSERT, UPDATE, DELETE | ALTER, DROP, CREATE |
| **ubec_monitor** | Monitoring | SELECT only | Any modifications |

---

## 🛠️ Common SQL Queries

### Check Table Ownership

```sql
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE schemaname = 'ubec_main'
ORDER BY tablename;
```

### Check Migration Status

```sql
SELECT migration_name, applied_at, status 
FROM ubec_main.schema_migrations 
ORDER BY applied_at DESC 
LIMIT 10;
```

### Check Constraints

```sql
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'ubec_main.scheduler_jobs'::regclass;
```

### Check User Permissions

```sql
SELECT 
    grantee,
    privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'ubec_main'
AND table_name = 'scheduler_jobs';
```

---

## 🚨 Emergency Procedures

### Fix Table Ownership

```bash
sudo -u postgres psql -d ubec <<EOF
ALTER TABLE ubec_main.scheduler_jobs OWNER TO ubec_admin;
ALTER TABLE ubec_main.schema_migrations OWNER TO ubec_admin;
EOF
```

### Reset User Password

```bash
sudo -u postgres psql -d ubec -c \
  "ALTER USER ubec_admin WITH PASSWORD 'new_secure_password';"
```

### Check Database Connection

```bash
psql -U ubec_admin -d ubec -h localhost -c "SELECT NOW();"
```

### View Active Connections

```bash
sudo -u postgres psql -c \
  "SELECT datname, usename, application_name, state 
   FROM pg_stat_activity 
   WHERE datname = 'ubec';"
```

---

## 📝 File Locations

```
UBEC/
├── database/
│   └── migrations/
│       ├── 000_create_migration_tracking.sql      # Setup
│       ├── TEMPLATE_migration.sql                 # Copy this
│       └── 20251110_1500_fix_scheduler_job_functions.sql
│
├── scripts/
│   ├── run_migration.sh           # Execute migrations
│   ├── view_migrations.sh         # View history
│   └── check_permissions.sh       # Verify security
│
├── docs/
│   └── DATABASE_SECURITY_AND_MIGRATIONS.md   # Full guide
│
└── .env                           # Database credentials
```

---

## 🔑 Environment Variables

```bash
# .env file (example)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ubec

# Application user (runtime)
DB_USER=ubec_app
DB_PASSWORD=<app-password>

# Admin user (migrations - keep secure!)
DB_ADMIN_USER=ubec_admin
DB_ADMIN_PASSWORD=<admin-password>

# Monitor user (read-only)
DB_READONLY_USER=ubec_monitor
DB_READONLY_PASSWORD=<monitor-password>
```

---

## ⚡ Quick Fixes

### Scheduler Job Format Issue

```bash
# Run the fix
./scripts/run_migration.sh 20251110_1500_fix_scheduler_job_functions.sql

# Verify
psql -U ubec_app -d ubec -c \
  "SELECT job_name, job_function FROM ubec_main.scheduler_jobs;"

# Restart server
python main.py serve
```

### Migration Failed

```bash
# View error
./scripts/view_migrations.sh --failed

# Check details
./scripts/view_migrations.sh --detail <migration_name>

# Fix issue and re-run
./scripts/run_migration.sh <migration_file>
```

### Can't Connect

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart if needed
sudo systemctl restart postgresql

# Test connection
psql -U ubec_admin -d ubec -h localhost -c "SELECT 1;"
```

---

## 📞 Getting Help

```bash
# Script help
./scripts/run_migration.sh --help
./scripts/view_migrations.sh --help

# Full documentation
cat docs/DATABASE_SECURITY_AND_MIGRATIONS.md

# System health check
python main.py health --detailed
```

---

## ✅ Pre-Production Checklist

Before deploying to production:

- [ ] All migrations tested on development database
- [ ] Migration history reviewed: `./scripts/view_migrations.sh`
- [ ] Security model verified: `sudo ./scripts/check_permissions.sh`
- [ ] Table ownership correct (ubec_admin owns tables)
- [ ] Application .env has ubec_app credentials only
- [ ] Admin credentials stored securely (not in application .env)
- [ ] Backups configured and tested
- [ ] Rollback procedures documented

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-10  
**For detailed documentation, see:** `docs/DATABASE_SECURITY_AND_MIGRATIONS.md`

---

*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.*
