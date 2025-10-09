-- ============================================================================
-- UBEC Database - User and Permission Management
-- Database: ubec
-- Schema: ubec_main
-- Version: 1.0
-- Date: October 8, 2025
-- 
-- Description:
-- Creates database users with appropriate roles and permissions
-- for the UBEC four-element protocol
-- 
-- User Types:
-- 1. ubec_admin     - Full administrative access
-- 2. ubec_app       - Application user (read/write)
-- 3. ubec_readonly  - Read-only access for reporting
-- 4. ubec_sync      - Synchronization service user
-- ============================================================================

-- Connect to the ubec database
\c ubec;

-- ============================================================================
-- SECTION 1: CREATE ROLES
-- ============================================================================

-- Drop existing roles if they exist (use with caution!)
DROP ROLE IF EXISTS ubec_admin;
DROP ROLE IF EXISTS ubec_app;
DROP ROLE IF EXISTS ubec_readonly;
DROP ROLE IF EXISTS ubec_sync;

-- Create admin role
CREATE ROLE ubec_admin WITH
    LOGIN
    SUPERUSER
    CREATEDB
    CREATEROLE
    INHERIT
    REPLICATION
    CONNECTION LIMIT -1
    PASSWORD 'Admin252010!@#';

COMMENT ON ROLE ubec_admin IS 'UBEC Protocol - Administrative user with full privileges';

-- Create application role
CREATE ROLE ubec_app WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    CONNECTION LIMIT 50
    PASSWORD 'App252010!@#';

COMMENT ON ROLE ubec_app IS 'UBEC Protocol - Main application user for read/write operations';

-- Create read-only role
CREATE ROLE ubec_readonly WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    CONNECTION LIMIT 20
    PASSWORD 'ReadOnly252010!@#';

COMMENT ON ROLE ubec_readonly IS 'UBEC Protocol - Read-only user for reporting and analysis';

-- Create synchronization service role
CREATE ROLE ubec_sync WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    CONNECTION LIMIT 10
    PASSWORD 'Sync252010!@#';

COMMENT ON ROLE ubec_sync IS 'UBEC Protocol - Synchronization service user for blockchain data ingestion';

-- ============================================================================
-- SECTION 2: ADMIN USER PERMISSIONS
-- ============================================================================

-- Grant all privileges to admin
GRANT ALL PRIVILEGES ON DATABASE ubec TO ubec_admin;
GRANT ALL PRIVILEGES ON SCHEMA ubec_main TO ubec_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ubec_main TO ubec_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ubec_main TO ubec_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA ubec_main TO ubec_admin;

-- Ensure admin can grant privileges to others
ALTER ROLE ubec_admin WITH ADMIN OPTION;

-- ============================================================================
-- SECTION 3: APPLICATION USER PERMISSIONS
-- ============================================================================

-- Grant database connection
GRANT CONNECT ON DATABASE ubec TO ubec_app;

-- Grant schema usage
GRANT USAGE ON SCHEMA ubec_main TO ubec_app;

-- Grant table permissions (SELECT, INSERT, UPDATE, DELETE)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ubec_main TO ubec_app;

-- Grant sequence usage for auto-increment columns
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ubec_main TO ubec_app;

-- Grant function execution
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ubec_main TO ubec_app;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main 
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ubec_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main 
    GRANT USAGE, SELECT ON SEQUENCES TO ubec_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main 
    GRANT EXECUTE ON FUNCTIONS TO ubec_app;

-- ============================================================================
-- SECTION 4: READ-ONLY USER PERMISSIONS
-- ============================================================================

-- Grant database connection
GRANT CONNECT ON DATABASE ubec TO ubec_readonly;

-- Grant schema usage
GRANT USAGE ON SCHEMA ubec_main TO ubec_readonly;

-- Grant SELECT only on all tables and views
GRANT SELECT ON ALL TABLES IN SCHEMA ubec_main TO ubec_readonly;

-- Grant SELECT on sequences (for monitoring)
GRANT SELECT ON ALL SEQUENCES IN SCHEMA ubec_main TO ubec_readonly;

-- Grant EXECUTE on read-only functions
GRANT EXECUTE ON FUNCTION ubec_main.get_element_for_token(token_code) TO ubec_readonly;
GRANT EXECUTE ON FUNCTION ubec_main.get_element_for_principle(ubuntu_principle) TO ubec_readonly;
GRANT EXECUTE ON FUNCTION ubec_main.check_distribution_compliance(token_code, DECIMAL) TO ubec_readonly;
GRANT EXECUTE ON FUNCTION ubec_main.get_latest_holonic_score(element_type, ubuntu_principle) TO ubec_readonly;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main 
    GRANT SELECT ON TABLES TO ubec_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main 
    GRANT SELECT ON SEQUENCES TO ubec_readonly;

-- ============================================================================
-- SECTION 5: SYNC USER PERMISSIONS
-- ============================================================================

-- Grant database connection
GRANT CONNECT ON DATABASE ubec TO ubec_sync;

-- Grant schema usage
GRANT USAGE ON SCHEMA ubec_main TO ubec_sync;

-- Grant specific permissions for sync operations
-- Full access to blockchain data tables
GRANT SELECT, INSERT, UPDATE ON TABLE ubec_main.stellar_accounts TO ubec_sync;
GRANT SELECT, INSERT, UPDATE ON TABLE ubec_main.stellar_transactions TO ubec_sync;
GRANT SELECT, INSERT, UPDATE ON TABLE ubec_main.stellar_operations TO ubec_sync;
GRANT SELECT, INSERT, UPDATE ON TABLE ubec_main.stellar_effects TO ubec_sync;

-- Full access to UBEC-specific tables that need syncing
GRANT SELECT, INSERT, UPDATE ON TABLE ubec_main.ubec_balances TO ubec_sync;
GRANT SELECT, INSERT, UPDATE ON TABLE ubec_main.ubec_distributions TO ubec_sync;
GRANT SELECT, INSERT, UPDATE ON TABLE ubec_main.ubec_sync_status TO ubec_sync;

-- Read-only access to other tables
GRANT SELECT ON TABLE ubec_main.ubec_holonic_metrics TO ubec_sync;
GRANT SELECT ON TABLE ubec_main.ubec_audit_log TO ubec_sync;
GRANT SELECT ON TABLE ubec_main.ubec_reports TO ubec_sync;

-- Grant sequence usage
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ubec_main TO ubec_sync;

-- Grant execute on utility functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ubec_main TO ubec_sync;

-- ============================================================================
-- SECTION 6: ROW-LEVEL SECURITY (Optional but Recommended)
-- ============================================================================

-- Enable row-level security on sensitive tables
ALTER TABLE ubec_main.ubec_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE ubec_main.ubec_holonic_metrics ENABLE ROW LEVEL SECURITY;

-- Policy for admin: see everything
CREATE POLICY admin_all_policy ON ubec_main.ubec_balances
    FOR ALL
    TO ubec_admin
    USING (true)
    WITH CHECK (true);

CREATE POLICY admin_all_policy_metrics ON ubec_main.ubec_holonic_metrics
    FOR ALL
    TO ubec_admin
    USING (true)
    WITH CHECK (true);

-- Policy for app: full access
CREATE POLICY app_all_policy ON ubec_main.ubec_balances
    FOR ALL
    TO ubec_app
    USING (true)
    WITH CHECK (true);

CREATE POLICY app_all_policy_metrics ON ubec_main.ubec_holonic_metrics
    FOR ALL
    TO ubec_app
    USING (true)
    WITH CHECK (true);

-- Policy for readonly: select only
CREATE POLICY readonly_select_policy ON ubec_main.ubec_balances
    FOR SELECT
    TO ubec_readonly
    USING (true);

CREATE POLICY readonly_select_policy_metrics ON ubec_main.ubec_holonic_metrics
    FOR SELECT
    TO ubec_readonly
    USING (true);

-- Policy for sync: full access
CREATE POLICY sync_all_policy ON ubec_main.ubec_balances
    FOR ALL
    TO ubec_sync
    USING (true)
    WITH CHECK (true);

CREATE POLICY sync_all_policy_metrics ON ubec_main.ubec_holonic_metrics
    FOR SELECT
    TO ubec_sync
    USING (true);

-- ============================================================================
-- SECTION 7: CREATE ADDITIONAL SECURITY VIEWS
-- ============================================================================

-- Create a view that shows current user permissions
CREATE OR REPLACE VIEW ubec_main.view_user_permissions AS
SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'ubec_main'
ORDER BY grantee, table_name, privilege_type;

COMMENT ON VIEW ubec_main.view_user_permissions IS 'Shows current user permissions on ubec_main schema';

-- Grant access to permission view
GRANT SELECT ON ubec_main.view_user_permissions TO ubec_admin;
GRANT SELECT ON ubec_main.view_user_permissions TO ubec_readonly;

-- ============================================================================
-- SECTION 8: PASSWORD POLICIES AND SECURITY
-- ============================================================================

-- Set password lifetime (optional - adjust as needed)
-- ALTER ROLE ubec_admin VALID UNTIL '2026-10-08';
-- ALTER ROLE ubec_app VALID UNTIL '2026-10-08';
-- ALTER ROLE ubec_readonly VALID UNTIL '2026-10-08';
-- ALTER ROLE ubec_sync VALID UNTIL '2026-10-08';

-- Force SSL connections (recommended for production)
-- ALTER ROLE ubec_admin WITH NOSUPERUSER;
-- Uncomment and configure SSL in postgresql.conf

-- ============================================================================
-- SECTION 9: VERIFY SETUP
-- ============================================================================

-- Function to verify user setup
CREATE OR REPLACE FUNCTION ubec_main.verify_user_setup()
RETURNS TABLE(
    role_name TEXT,
    can_login BOOLEAN,
    is_superuser BOOLEAN,
    connection_limit INTEGER,
    table_privileges TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.rolname::TEXT,
        r.rolcanlogin,
        r.rolsuper,
        r.rolconnlimit,
        STRING_AGG(DISTINCT t.privilege_type, ', ')::TEXT
    FROM pg_roles r
    LEFT JOIN information_schema.role_table_grants t 
        ON r.rolname = t.grantee 
        AND t.table_schema = 'ubec_main'
    WHERE r.rolname IN ('ubec_admin', 'ubec_app', 'ubec_readonly', 'ubec_sync')
    GROUP BY r.rolname, r.rolcanlogin, r.rolsuper, r.rolconnlimit
    ORDER BY r.rolname;
END;
$$ LANGUAGE plpgsql;

-- Run verification
SELECT * FROM ubec_main.verify_user_setup();

-- ============================================================================
-- SECTION 10: CONNECTION STRING TEMPLATES
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '===========================================================';
    RAISE NOTICE 'UBEC Database Users Created Successfully!';
    RAISE NOTICE '===========================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Created Users:';
    RAISE NOTICE '  1. ubec_admin     - Full administrative access';
    RAISE NOTICE '  2. ubec_app       - Application user (read/write)';
    RAISE NOTICE '  3. ubec_readonly  - Read-only access';
    RAISE NOTICE '  4. ubec_sync      - Synchronization service';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  IMPORTANT: CHANGE ALL DEFAULT PASSWORDS!';
    RAISE NOTICE '';
    RAISE NOTICE 'To change passwords:';
    RAISE NOTICE '  ALTER ROLE ubec_admin WITH PASSWORD ''your_secure_password'';';
    RAISE NOTICE '  ALTER ROLE ubec_app WITH PASSWORD ''your_secure_password'';';
    RAISE NOTICE '  ALTER ROLE ubec_readonly WITH PASSWORD ''your_secure_password'';';
    RAISE NOTICE '  ALTER ROLE ubec_sync WITH PASSWORD ''your_secure_password'';';
    RAISE NOTICE '';
    RAISE NOTICE 'Connection String Templates:';
    RAISE NOTICE '';
    RAISE NOTICE 'Admin:';
    RAISE NOTICE '  postgresql://ubec_admin:password@localhost:5432/ubec';
    RAISE NOTICE '';
    RAISE NOTICE 'Application:';
    RAISE NOTICE '  postgresql://ubec_app:password@localhost:5432/ubec';
    RAISE NOTICE '';
    RAISE NOTICE 'Read-Only:';
    RAISE NOTICE '  postgresql://ubec_readonly:password@localhost:5432/ubec';
    RAISE NOTICE '';
    RAISE NOTICE 'Synchronization:';
    RAISE NOTICE '  postgresql://ubec_sync:password@localhost:5432/ubec';
    RAISE NOTICE '';
    RAISE NOTICE 'Python Example:';
    RAISE NOTICE '  import psycopg2';
    RAISE NOTICE '  conn = psycopg2.connect(';
    RAISE NOTICE '      host="localhost",';
    RAISE NOTICE '      database="ubec",';
    RAISE NOTICE '      user="ubec_app",';
    RAISE NOTICE '      password="your_password"';
    RAISE NOTICE '  )';
    RAISE NOTICE '';
    RAISE NOTICE 'Environment Variables:';
    RAISE NOTICE '  export UBEC_DB_HOST=localhost';
    RAISE NOTICE '  export UBEC_DB_PORT=5432';
    RAISE NOTICE '  export UBEC_DB_NAME=ubec';
    RAISE NOTICE '  export UBEC_DB_USER=ubec_app';
    RAISE NOTICE '  export UBEC_DB_PASSWORD=your_password';
    RAISE NOTICE '';
    RAISE NOTICE 'Verify setup:';
    RAISE NOTICE '  SELECT * FROM ubec_main.verify_user_setup();';
    RAISE NOTICE '===========================================================';
    RAISE NOTICE '';
END $$;
