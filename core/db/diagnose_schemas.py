#!/usr/bin/env python3
"""
UBEC Schema Visibility Diagnostic Tool

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Diagnoses why schemas might not be visible to the application user.
"""

import psycopg2
import sys
from pathlib import Path

# Add parent directory to path to import from ubec_schema_documenter
sys.path.insert(0, str(Path(__file__).parent))

# Import configuration functions from the documenter
try:
    from ubec_schema_documenter import get_database_config
except ImportError:
    print("Error: Cannot import from ubec_schema_documenter.py")
    print("Make sure the file is in the same directory.")
    sys.exit(1)


def diagnose_schema_visibility():
    """Diagnose schema visibility issues."""
    
    print("\n" + "=" * 70)
    print("UBEC Schema Visibility Diagnostic")
    print("=" * 70 + "\n")
    
    # Get connection config
    try:
        config = get_database_config()
    except Exception as e:
        print(f"❌ Error getting database config: {e}")
        return 1
    
    print(f"Connection Details:")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  Database: {config['database']}")
    print(f"  User: {config['user']}")
    print(f"  Password: {'Set' if config.get('password') else 'Not set'}\n")
    
    # Connect
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        print("✅ Connection successful!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}\n")
        return 1
    
    try:
        # Check current user
        cursor.execute("SELECT current_user, session_user")
        current_user, session_user = cursor.fetchone()
        print(f"Connected as:")
        print(f"  Current user: {current_user}")
        print(f"  Session user: {session_user}\n")
        
        # Check if user is superuser
        cursor.execute("""
            SELECT rolsuper, rolcreatedb, rolcreaterole 
            FROM pg_roles 
            WHERE rolname = current_user
        """)
        is_super, can_createdb, can_createrole = cursor.fetchone()
        print(f"User privileges:")
        print(f"  Superuser: {is_super}")
        print(f"  Can create databases: {can_createdb}")
        print(f"  Can create roles: {can_createrole}\n")
        
        # List all schemas in database
        print("Schemas visible to postgres superuser:")
        print("  (from system catalog)")
        cursor.execute("""
            SELECT nspname, nspowner::regrole
            FROM pg_namespace
            WHERE nspname NOT LIKE 'pg_toast%'
            AND nspname NOT LIKE 'pg_temp%'
            ORDER BY nspname
        """)
        all_schemas = cursor.fetchall()
        for schema_name, owner in all_schemas:
            print(f"  • {schema_name} (owner: {owner})")
        print()
        
        # List schemas visible through information_schema
        print("Schemas visible through information_schema:")
        print("  (what the documenter sees)")
        cursor.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            AND schema_name NOT LIKE 'pg_%'
            ORDER BY schema_name
        """)
        visible_schemas = cursor.fetchall()
        for (schema_name,) in visible_schemas:
            print(f"  • {schema_name}")
        print()
        
        # Check which schemas have USAGE privilege
        print("Schemas with USAGE privilege for current user:")
        cursor.execute("""
            SELECT nspname
            FROM pg_namespace
            WHERE has_schema_privilege(current_user, nspname, 'USAGE')
            AND nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            AND nspname NOT LIKE 'pg_%'
            ORDER BY nspname
        """)
        usable_schemas = cursor.fetchall()
        for (schema_name,) in usable_schemas:
            print(f"  • {schema_name}")
        print()
        
        # Check each specific schema
        expected_schemas = ['ubec_main', 'phenomenal', 'topology', 'public']
        print("Detailed permission check for expected schemas:")
        for schema in expected_schemas:
            cursor.execute("""
                SELECT 
                    nspname,
                    nspowner::regrole as owner,
                    has_schema_privilege(current_user, nspname, 'USAGE') as has_usage,
                    has_schema_privilege(current_user, nspname, 'CREATE') as has_create
                FROM pg_namespace
                WHERE nspname = %s
            """, (schema,))
            
            result = cursor.fetchone()
            if result:
                name, owner, has_usage, has_create = result
                status = "✅" if has_usage else "❌"
                print(f"  {status} {name}:")
                print(f"      Owner: {owner}")
                print(f"      USAGE: {has_usage}")
                print(f"      CREATE: {has_create}")
                
                # Check table count
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    AND table_type = 'BASE TABLE'
                """, (schema,))
                table_count = cursor.fetchone()[0]
                print(f"      Tables visible: {table_count}")
            else:
                print(f"  ❌ {schema}: NOT FOUND in pg_namespace")
            print()
        
        # Recommendations
        print("=" * 70)
        print("DIAGNOSIS & RECOMMENDATIONS:")
        print("=" * 70 + "\n")
        
        missing_schemas = []
        for schema in expected_schemas:
            cursor.execute("""
                SELECT has_schema_privilege(current_user, %s, 'USAGE')
            """, (schema,))
            result = cursor.fetchone()
            if not result or not result[0]:
                missing_schemas.append(schema)
        
        if missing_schemas:
            print(f"⚠️  User '{current_user}' lacks USAGE privilege on:")
            for schema in missing_schemas:
                print(f"   • {schema}")
            print()
            print("To fix, run as postgres user:")
            print()
            for schema in missing_schemas:
                print(f"  GRANT USAGE ON SCHEMA {schema} TO {current_user};")
            print()
            print("To also allow reading tables:")
            print()
            for schema in missing_schemas:
                print(f"  GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {current_user};")
                print(f"  GRANT SELECT ON ALL SEQUENCES IN SCHEMA {schema} TO {current_user};")
                print(f"  ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} GRANT SELECT ON TABLES TO {current_user};")
            print()
        else:
            print("✅ All expected schemas are accessible!")
            print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(diagnose_schema_visibility())
