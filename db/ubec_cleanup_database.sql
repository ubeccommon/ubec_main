-- ============================================================================
-- UBEC Database - Complete Cleanup Script
-- Purpose: Safely drop database and all users to start fresh
-- Version: 1.0
-- Date: October 8, 2025
-- 
-- WARNING: This will permanently delete the ubec database and all data!
-- ============================================================================

-- Connect to postgres database (not ubec, since we're dropping it)
\c postgres;

-- ============================================================================
-- STEP 1: TERMINATE ALL CONNECTIONS TO UBEC DATABASE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'UBEC Database Cleanup - Starting';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Step 1: Terminating all connections to ubec database...';
END $$;

-- Terminate all active connections to the ubec database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'ubec'
  AND pid <> pg_backend_pid();

DO $$
DECLARE
    v_conn_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_conn_count
    FROM pg_stat_activity
    WHERE datname = 'ubec';
    
    IF v_conn_count = 0 THEN
        RAISE NOTICE '✓ All connections terminated successfully';
    ELSE
        RAISE NOTICE '⚠ Warning: % connections still active', v_conn_count;
    END IF;
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- STEP 2: DROP DATABASE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Step 2: Dropping ubec database...';
END $$;

-- Check if database exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'ubec') THEN
        RAISE NOTICE '  Database "ubec" found - dropping...';
    ELSE
        RAISE NOTICE '  Database "ubec" does not exist - skipping';
    END IF;
END $$;

-- Drop the database if it exists
DROP DATABASE IF EXISTS ubec;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'ubec') THEN
        RAISE NOTICE '✓ Database "ubec" dropped successfully';
    ELSE
        RAISE NOTICE '✗ Failed to drop database "ubec"';
    END IF;
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- STEP 3: DROP ALL UBEC USERS/ROLES
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Step 3: Dropping all ubec users...';
END $$;

-- Drop ubec_admin
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ubec_admin') THEN
        RAISE NOTICE '  Dropping role: ubec_admin';
        DROP ROLE ubec_admin;
        RAISE NOTICE '  ✓ Role "ubec_admin" dropped';
    ELSE
        RAISE NOTICE '  Role "ubec_admin" does not exist - skipping';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '  ✗ Error dropping ubec_admin: %', SQLERRM;
END $$;

-- Drop ubec_app
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ubec_app') THEN
        RAISE NOTICE '  Dropping role: ubec_app';
        DROP ROLE ubec_app;
        RAISE NOTICE '  ✓ Role "ubec_app" dropped';
    ELSE
        RAISE NOTICE '  Role "ubec_app" does not exist - skipping';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '  ✗ Error dropping ubec_app: %', SQLERRM;
END $$;

-- Drop ubec_readonly
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ubec_readonly') THEN
        RAISE NOTICE '  Dropping role: ubec_readonly';
        DROP ROLE ubec_readonly;
        RAISE NOTICE '  ✓ Role "ubec_readonly" dropped';
    ELSE
        RAISE NOTICE '  Role "ubec_readonly" does not exist - skipping';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '  ✗ Error dropping ubec_readonly: %', SQLERRM;
END $$;

-- Drop ubec_sync
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ubec_sync') THEN
        RAISE NOTICE '  Dropping role: ubec_sync';
        DROP ROLE ubec_sync;
        RAISE NOTICE '  ✓ Role "ubec_sync" dropped';
    ELSE
        RAISE NOTICE '  Role "ubec_sync" does not exist - skipping';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '  ✗ Error dropping ubec_sync: %', SQLERRM;
END $$;

DO $$
BEGIN
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- STEP 4: VERIFY CLEANUP
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Step 4: Verifying cleanup...';
    RAISE NOTICE '';
END $$;

-- Check database
DO $$
DECLARE
    v_db_exists BOOLEAN;
BEGIN
    SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'ubec') INTO v_db_exists;
    
    IF v_db_exists THEN
        RAISE NOTICE '✗ Database "ubec" still exists!';
    ELSE
        RAISE NOTICE '✓ Database "ubec" confirmed removed';
    END IF;
END $$;

-- Check users
DO $$
DECLARE
    v_user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_user_count
    FROM pg_roles
    WHERE rolname IN ('ubec_admin', 'ubec_app', 'ubec_readonly', 'ubec_sync');
    
    IF v_user_count = 0 THEN
        RAISE NOTICE '✓ All ubec users confirmed removed';
    ELSE
        RAISE NOTICE '✗ Warning: % ubec users still exist', v_user_count;
        
        -- List remaining users
        RAISE NOTICE '  Remaining users:';
        FOR v_user IN 
            SELECT rolname FROM pg_roles 
            WHERE rolname IN ('ubec_admin', 'ubec_app', 'ubec_readonly', 'ubec_sync')
        LOOP
            RAISE NOTICE '    - %', v_user;
        END LOOP;
    END IF;
END $$;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'UBEC Database Cleanup - Complete';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Cleanup Summary:';
    RAISE NOTICE '  - Database "ubec" dropped';
    RAISE NOTICE '  - All connections terminated';
    RAISE NOTICE '  - All users removed (ubec_admin, ubec_app, ubec_readonly, ubec_sync)';
    RAISE NOTICE '';
    RAISE NOTICE 'You can now start fresh by running:';
    RAISE NOTICE '  1. psql -U postgres -f ubec_database_schema.sql';
    RAISE NOTICE '  2. psql -U postgres -d ubec -f ubec_users_permissions.sql';
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
END $$;
