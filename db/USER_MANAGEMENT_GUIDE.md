# UBEC Database - User Management Guide

**Database:** `ubec`  
**Schema:** `ubec_main`  
**Version:** 1.0  
**Date:** October 8, 2025

---

## Quick Start

### 1. Install User Permissions

```bash
# After creating the database schema, run the user script
psql -U postgres -d ubec -f ubec_users_permissions.sql
```

### 2. Verify Users Created

```sql
-- Connect as postgres
psql -U postgres -d ubec

-- Check created users
SELECT rolname, rolcanlogin, rolsuper, rolconnlimit 
FROM pg_roles 
WHERE rolname LIKE 'ubec_%'
ORDER BY rolname;

-- Or use the verification function
SELECT * FROM ubec_main.verify_user_setup();
```

---

## User Roles

### 1. ubec_admin (Administrator)

**Purpose:** Full administrative access to the database

**Capabilities:**
- ✅ Create/drop tables and schemas
- ✅ Manage other users and permissions
- ✅ Full read/write access to all data
- ✅ Execute all functions and procedures
- ✅ Backup and restore database

**Connection Limit:** Unlimited

**Use Cases:**
- Database maintenance
- Schema migrations
- User management
- Emergency operations

**Connection String:**
```
postgresql://ubec_admin:PASSWORD@localhost:5432/ubec
```

**Security Level:** 🔴 HIGHEST - Protect carefully!

---

### 2. ubec_app (Application User)

**Purpose:** Main application user for daily operations

**Capabilities:**
- ✅ Read data from all tables
- ✅ Insert new records
- ✅ Update existing records
- ✅ Delete records
- ✅ Execute all functions
- ❌ Cannot create/drop tables
- ❌ Cannot manage users

**Connection Limit:** 50 concurrent connections

**Use Cases:**
- Web application backend
- API services
- Main protocol operations
- Element protocol coordination

**Connection String:**
```
postgresql://ubec_app:PASSWORD@localhost:5432/ubec
```

**Security Level:** 🟡 MEDIUM - Used by applications

---

### 3. ubec_readonly (Read-Only User)

**Purpose:** Read-only access for reporting and analysis

**Capabilities:**
- ✅ Read data from all tables and views
- ✅ Execute read-only functions
- ❌ Cannot insert/update/delete data
- ❌ Cannot modify schema
- ❌ Cannot manage users

**Connection Limit:** 20 concurrent connections

**Use Cases:**
- Business intelligence tools
- Reporting dashboards
- Data analysis
- External integrations (read-only)
- Monitoring systems

**Connection String:**
```
postgresql://ubec_readonly:PASSWORD@localhost:5432/ubec
```

**Security Level:** 🟢 LOW - Safe for external access

---

### 4. ubec_sync (Synchronization User)

**Purpose:** Specialized user for blockchain data synchronization

**Capabilities:**
- ✅ Full access to blockchain data tables
- ✅ Full access to balance and distribution tables
- ✅ Update sync status
- ✅ Read-only access to holonic metrics and audit logs
- ❌ Cannot drop tables
- ❌ Cannot manage users

**Connection Limit:** 10 concurrent connections

**Use Cases:**
- Stellar blockchain synchronization
- Data ingestion services
- Automated sync processes
- Background workers

**Connection String:**
```
postgresql://ubec_sync:PASSWORD@localhost:5432/ubec
```

**Security Level:** 🟡 MEDIUM - Automated services only

---

## Password Management

### Initial Setup - CHANGE DEFAULT PASSWORDS IMMEDIATELY!

```sql
-- Connect as postgres
psql -U postgres -d ubec

-- Change all passwords
ALTER ROLE ubec_admin WITH PASSWORD 'your_secure_admin_password_2025!';
ALTER ROLE ubec_app WITH PASSWORD 'your_secure_app_password_2025!';
ALTER ROLE ubec_readonly WITH PASSWORD 'your_secure_readonly_password_2025!';
ALTER ROLE ubec_sync WITH PASSWORD 'your_secure_sync_password_2025!';
```

### Password Requirements

**Strong Password Guidelines:**
- Minimum 16 characters
- Mix of uppercase and lowercase letters
- Include numbers
- Include special characters (!@#$%^&*)
- Avoid common words or patterns
- Different password for each user

**Example Strong Passwords:**
```
ubec_admin:    Ub3c@dM1n!Pr0t0c0l#2025$aIr
ubec_app:      W@t3rFl0w!UbEc$App#2025^sEcUr3
ubec_readonly: E@rthSt@b!R3ad#2025$0nLy^vI3w
ubec_sync:     F1r3Sync!Tr@nsF0rm#2025$dAtA^p1p3
```

### Password Rotation

Set up regular password rotation:

```sql
-- Set password expiration (optional)
ALTER ROLE ubec_admin VALID UNTIL '2026-01-01';
ALTER ROLE ubec_app VALID UNTIL '2026-01-01';
ALTER ROLE ubec_readonly VALID UNTIL '2026-01-01';
ALTER ROLE ubec_sync VALID UNTIL '2026-01-01';
```

---

## Configuration Files

### Environment Variables (.env)

Create a `.env` file for your application:

```bash
# Database Configuration
UBEC_DB_HOST=localhost
UBEC_DB_PORT=5432
UBEC_DB_NAME=ubec
UBEC_DB_SCHEMA=ubec_main

# Application User (for main protocol)
UBEC_DB_USER=ubec_app
UBEC_DB_PASSWORD=your_secure_app_password

# Read-Only User (for reporting)
UBEC_DB_READONLY_USER=ubec_readonly
UBEC_DB_READONLY_PASSWORD=your_secure_readonly_password

# Sync User (for blockchain sync)
UBEC_DB_SYNC_USER=ubec_sync
UBEC_DB_SYNC_PASSWORD=your_secure_sync_password

# Connection Pool Settings
UBEC_DB_POOL_MIN=2
UBEC_DB_POOL_MAX=20
UBEC_DB_POOL_TIMEOUT=30

# SSL Settings (recommended for production)
UBEC_DB_SSL_MODE=require
```

### Python Configuration (config.py)

```python
# config/database_config.py
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """Database configuration for UBEC protocol"""
    
    # Connection parameters
    HOST = os.getenv('UBEC_DB_HOST', 'localhost')
    PORT = int(os.getenv('UBEC_DB_PORT', '5432'))
    DATABASE = os.getenv('UBEC_DB_NAME', 'ubec')
    SCHEMA = os.getenv('UBEC_DB_SCHEMA', 'ubec_main')
    
    # Application user (main protocol)
    APP_USER = os.getenv('UBEC_DB_USER', 'ubec_app')
    APP_PASSWORD = os.getenv('UBEC_DB_PASSWORD')
    
    # Read-only user (reporting)
    READONLY_USER = os.getenv('UBEC_DB_READONLY_USER', 'ubec_readonly')
    READONLY_PASSWORD = os.getenv('UBEC_DB_READONLY_PASSWORD')
    
    # Sync user (blockchain sync)
    SYNC_USER = os.getenv('UBEC_DB_SYNC_USER', 'ubec_sync')
    SYNC_PASSWORD = os.getenv('UBEC_DB_SYNC_PASSWORD')
    
    # Connection pool
    POOL_MIN = int(os.getenv('UBEC_DB_POOL_MIN', '2'))
    POOL_MAX = int(os.getenv('UBEC_DB_POOL_MAX', '20'))
    POOL_TIMEOUT = int(os.getenv('UBEC_DB_POOL_TIMEOUT', '30'))
    
    # SSL settings
    SSL_MODE = os.getenv('UBEC_DB_SSL_MODE', 'prefer')
    
    @classmethod
    def get_connection_string(cls, user_type='app'):
        """Get connection string for specified user type"""
        
        user_map = {
            'app': (cls.APP_USER, cls.APP_PASSWORD),
            'readonly': (cls.READONLY_USER, cls.READONLY_PASSWORD),
            'sync': (cls.SYNC_USER, cls.SYNC_PASSWORD)
        }
        
        user, password = user_map.get(user_type, user_map['app'])
        
        return f"postgresql://{user}:{password}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"
    
    @classmethod
    def get_connection_params(cls, user_type='app'):
        """Get connection parameters dict"""
        
        user_map = {
            'app': (cls.APP_USER, cls.APP_PASSWORD),
            'readonly': (cls.READONLY_USER, cls.READONLY_PASSWORD),
            'sync': (cls.SYNC_USER, cls.SYNC_PASSWORD)
        }
        
        user, password = user_map.get(user_type, user_map['app'])
        
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'database': cls.DATABASE,
            'user': user,
            'password': password,
            'options': f'-c search_path={cls.SCHEMA},public'
        }
```

---

## Python Connection Examples

### Using psycopg2

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from config.database_config import DatabaseConfig

# Application connection
def get_app_connection():
    """Get connection using application user"""
    conn = psycopg2.connect(
        **DatabaseConfig.get_connection_params('app'),
        cursor_factory=RealDictCursor
    )
    return conn

# Read-only connection
def get_readonly_connection():
    """Get connection using read-only user"""
    conn = psycopg2.connect(
        **DatabaseConfig.get_connection_params('readonly'),
        cursor_factory=RealDictCursor
    )
    return conn

# Sync connection
def get_sync_connection():
    """Get connection using sync user"""
    conn = psycopg2.connect(
        **DatabaseConfig.get_connection_params('sync'),
        cursor_factory=RealDictCursor
    )
    return conn

# Usage example
def example_query():
    with get_app_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM view_air_gateway LIMIT 10")
            results = cur.fetchall()
            return results
```

### Using SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database_config import DatabaseConfig

# Create engines for different user types
app_engine = create_engine(
    DatabaseConfig.get_connection_string('app'),
    pool_size=DatabaseConfig.POOL_MIN,
    max_overflow=DatabaseConfig.POOL_MAX - DatabaseConfig.POOL_MIN,
    pool_timeout=DatabaseConfig.POOL_TIMEOUT,
    pool_pre_ping=True  # Verify connections before using
)

readonly_engine = create_engine(
    DatabaseConfig.get_connection_string('readonly'),
    pool_size=5,
    max_overflow=10
)

sync_engine = create_engine(
    DatabaseConfig.get_connection_string('sync'),
    pool_size=3,
    max_overflow=5
)

# Create session factories
AppSession = sessionmaker(bind=app_engine)
ReadOnlySession = sessionmaker(bind=readonly_engine)
SyncSession = sessionmaker(bind=sync_engine)

# Usage example
def get_account_balance(account_id):
    """Get account balance using app session"""
    session = AppSession()
    try:
        result = session.execute(
            """
            SELECT account_id, token_code, balance
            FROM ubec_balances
            WHERE account_id = :account_id
            """,
            {'account_id': account_id}
        )
        return result.fetchall()
    finally:
        session.close()
```

### Using Connection Pooling (psycopg2.pool)

```python
from psycopg2 import pool
from config.database_config import DatabaseConfig

# Create connection pools
app_pool = pool.ThreadedConnectionPool(
    minconn=DatabaseConfig.POOL_MIN,
    maxconn=DatabaseConfig.POOL_MAX,
    **DatabaseConfig.get_connection_params('app')
)

readonly_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    **DatabaseConfig.get_connection_params('readonly')
)

sync_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=5,
    **DatabaseConfig.get_connection_params('sync')
)

class DatabaseConnection:
    """Context manager for database connections"""
    
    def __init__(self, pool):
        self.pool = pool
        self.conn = None
    
    def __enter__(self):
        self.conn = self.pool.getconn()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.pool.putconn(self.conn)

# Usage
def sync_accounts():
    """Synchronize accounts using sync pool"""
    with DatabaseConnection(sync_pool) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE ubec_sync_status 
                SET status = 'syncing', updated_at = NOW()
                WHERE sync_type = 'accounts'
            """)
            conn.commit()
```

---

## Security Best Practices

### 1. Never Commit Passwords to Version Control

```bash
# .gitignore
.env
.env.local
.env.production
config/secrets.py
*.pem
*.key
```

### 2. Use Environment Variables

```python
import os

# ✅ Good - using environment variables
db_password = os.getenv('UBEC_DB_PASSWORD')

# ❌ Bad - hardcoded password
db_password = 'my_password_123'
```

### 3. Encrypt Connection Strings

For production, consider encrypting database credentials:

```python
from cryptography.fernet import Fernet

# Generate key (do this once, store securely)
key = Fernet.generate_key()

# Encrypt password
cipher = Fernet(key)
encrypted_password = cipher.encrypt(b"your_password")

# Decrypt when needed
password = cipher.decrypt(encrypted_password).decode()
```

### 4. Use SSL/TLS Connections

```python
import psycopg2

conn = psycopg2.connect(
    host="your-host",
    database="ubec",
    user="ubec_app",
    password="your_password",
    sslmode='require',  # Force SSL
    sslrootcert='/path/to/ca-cert.pem'
)
```

### 5. Implement Connection Timeouts

```python
import psycopg2

conn = psycopg2.connect(
    host="your-host",
    database="ubec",
    user="ubec_app",
    password="your_password",
    connect_timeout=10,  # 10 seconds
    options='-c statement_timeout=30000'  # 30 seconds for queries
)
```

### 6. Rotate Passwords Regularly

```bash
#!/bin/bash
# rotate_passwords.sh

# Generate new passwords
NEW_APP_PASSWORD=$(openssl rand -base64 32)
NEW_SYNC_PASSWORD=$(openssl rand -base64 32)
NEW_READONLY_PASSWORD=$(openssl rand -base64 32)

# Update database
psql -U postgres -d ubec <<EOF
ALTER ROLE ubec_app WITH PASSWORD '${NEW_APP_PASSWORD}';
ALTER ROLE ubec_sync WITH PASSWORD '${NEW_SYNC_PASSWORD}';
ALTER ROLE ubec_readonly WITH PASSWORD '${NEW_READONLY_PASSWORD}';
EOF

# Update .env file (use proper secret management in production)
echo "UBEC_DB_PASSWORD=${NEW_APP_PASSWORD}" > .env.new
echo "UBEC_DB_SYNC_PASSWORD=${NEW_SYNC_PASSWORD}" >> .env.new
echo "UBEC_DB_READONLY_PASSWORD=${NEW_READONLY_PASSWORD}" >> .env.new

# Backup old .env and replace
mv .env .env.backup.$(date +%Y%m%d)
mv .env.new .env

echo "Passwords rotated successfully"
```

---

## Monitoring and Auditing

### Check Active Connections

```sql
-- See who's connected
SELECT 
    usename,
    application_name,
    client_addr,
    state,
    COUNT(*) as connections
FROM pg_stat_activity
WHERE datname = 'ubec'
GROUP BY usename, application_name, client_addr, state
ORDER BY connections DESC;
```

### Monitor User Activity

```sql
-- Track queries by user
SELECT 
    usename,
    COUNT(*) as query_count,
    SUM(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active_queries
FROM pg_stat_activity
WHERE datname = 'ubec'
GROUP BY usename;
```

### Audit Failed Login Attempts

Enable PostgreSQL logging in `postgresql.conf`:
```
log_connections = on
log_disconnections = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

---

## Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
systemctl status postgresql

# Check if port is open
netstat -an | grep 5432

# Test connection
psql -U ubec_app -d ubec -h localhost
```

### Permission Denied

```sql
-- Check user privileges
SELECT * FROM ubec_main.view_user_permissions 
WHERE grantee = 'ubec_app';

-- Grant missing permissions
GRANT SELECT, INSERT, UPDATE ON TABLE ubec_main.stellar_accounts TO ubec_app;
```

### Too Many Connections

```sql
-- Check connection limit
SELECT rolname, rolconnlimit 
FROM pg_roles 
WHERE rolname = 'ubec_app';

-- Increase limit
ALTER ROLE ubec_app CONNECTION LIMIT 100;

-- Or check database-wide limit
SHOW max_connections;
```

### Authentication Failed

```bash
# Verify password
psql -U ubec_app -d ubec -h localhost -W

# If password is correct but still fails, check pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Should have line like:
# host    ubec    ubec_app    127.0.0.1/32    md5
```

---

## Quick Reference

### User Summary

| User | Purpose | Read | Write | Admin | Connections |
|------|---------|------|-------|-------|-------------|
| ubec_admin | Administration | ✅ | ✅ | ✅ | Unlimited |
| ubec_app | Application | ✅ | ✅ | ❌ | 50 |
| ubec_readonly | Reporting | ✅ | ❌ | ❌ | 20 |
| ubec_sync | Synchronization | ✅ | ✅* | ❌ | 10 |

*ubec_sync has write access only to specific tables

### Connection Strings

```bash
# Admin
postgresql://ubec_admin:PASSWORD@localhost:5432/ubec

# Application
postgresql://ubec_app:PASSWORD@localhost:5432/ubec

# Read-Only
postgresql://ubec_readonly:PASSWORD@localhost:5432/ubec

# Sync
postgresql://ubec_sync:PASSWORD@localhost:5432/ubec
```

---

## Next Steps

1. ✅ Change all default passwords
2. ✅ Create `.env` file with credentials
3. ✅ Test connections with each user
4. ✅ Set up connection pooling
5. ✅ Enable SSL in production
6. ✅ Set up password rotation schedule
7. ✅ Configure monitoring and alerting

---

**Security Status:** ⚠️ Change default passwords before use!

**Version:** 1.0

**Last Updated:** October 8, 2025
