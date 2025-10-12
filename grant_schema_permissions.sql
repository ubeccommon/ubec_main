-- UBEC Schema Permissions Fix
-- 
-- This project uses the services of Claude and Anthropic PBC to inform our 
-- decisions and recommendations. This project was made possible with the 
-- assistance of Claude and Anthropic PBC.
--
-- Run this as the postgres superuser to grant proper permissions
-- Usage: sudo -u postgres psql -d ubec -f grant_schema_permissions.sql

\echo '================================'
\echo 'UBEC Schema Permissions Setup'
\echo '================================'
\echo ''

-- Set the application user (change if different)
\set app_user ubec_app

\echo 'Granting permissions to user:' :app_user
\echo ''

-- Grant USAGE on all UBEC schemas
\echo 'Granting USAGE on schemas...'
GRANT USAGE ON SCHEMA ubec_main TO :app_user;
GRANT USAGE ON SCHEMA phenomenal TO :app_user;
GRANT USAGE ON SCHEMA topology TO :app_user;
GRANT USAGE ON SCHEMA public TO :app_user;

-- Grant SELECT on all existing tables in each schema
\echo 'Granting SELECT on all tables...'
GRANT SELECT ON ALL TABLES IN SCHEMA ubec_main TO :app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA phenomenal TO :app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA topology TO :app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO :app_user;

-- Grant SELECT on all existing sequences
\echo 'Granting SELECT on all sequences...'
GRANT SELECT ON ALL SEQUENCES IN SCHEMA ubec_main TO :app_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA phenomenal TO :app_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA topology TO :app_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO :app_user;

-- Grant EXECUTE on all functions (needed for some PostGIS operations)
\echo 'Granting EXECUTE on all functions...'
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ubec_main TO :app_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA phenomenal TO :app_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA topology TO :app_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO :app_user;

-- Set default privileges for future objects
\echo 'Setting default privileges for future objects...'
ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main GRANT SELECT ON TABLES TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA phenomenal GRANT SELECT ON TABLES TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA topology GRANT SELECT ON TABLES TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO :app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main GRANT SELECT ON SEQUENCES TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA phenomenal GRANT SELECT ON SEQUENCES TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA topology GRANT SELECT ON SEQUENCES TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO :app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA ubec_main GRANT EXECUTE ON FUNCTIONS TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA phenomenal GRANT EXECUTE ON FUNCTIONS TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA topology GRANT EXECUTE ON FUNCTIONS TO :app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO :app_user;

\echo ''
\echo '✅ Permissions granted successfully!'
\echo ''
\echo 'Verification:'
\echo '============='

-- Verify permissions
SELECT 
    n.nspname as schema_name,
    has_schema_privilege(:'app_user', n.nspname, 'USAGE') as has_usage
FROM pg_namespace n
WHERE n.nspname IN ('ubec_main', 'phenomenal', 'topology', 'public')
ORDER BY n.nspname;

\echo ''
\echo 'Done! Now run the documenter again.'
