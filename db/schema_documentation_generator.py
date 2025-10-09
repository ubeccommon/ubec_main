#!/usr/bin/env python3
"""
Database Schema Documentation Generator for UBEC Environmental Monitoring System

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Generates comprehensive documentation of database schemas:
- Complete table structures with all columns
- Relationships between tables (foreign keys)
- Indexes for performance optimization
- Constraints ensuring data integrity
- Triggers and their purposes
- Functions and procedures
- Statistical insights

Version: 2.0 - Updated for UBEC Environmental Monitoring
"""

import psycopg2
import psycopg2.extras
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import argparse
from pathlib import Path

# Try to import python-dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_and_load_env_file():
    """Search for and load .env file from common locations."""
    if load_dotenv is None:
        logger.warning("python-dotenv not available, using system environment variables")
        return False
        
    current_path = Path.cwd()
    paths_to_check = [
        current_path / '.env',
        current_path.parent / '.env',
        current_path.parent.parent / '.env',
    ]
    
    # Check for api directory structure
    for parent in current_path.parents:
        if parent.name == 'api':
            paths_to_check.insert(0, parent / '.env')
            paths_to_check.insert(0, parent / 'app' / '.env')
            break
    
    for env_path in paths_to_check:
        if env_path.exists():
            logger.info(f"Loading .env from: {env_path}")
            load_dotenv(env_path)
            return True
    
    logger.warning("No .env file found")
    return False


def get_database_config():
    """Get database configuration from environment with fallbacks."""
    find_and_load_env_file()
    
    # First check for DATABASE_URL (common in many frameworks)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        logger.info(f"Found DATABASE_URL, parsing connection string")
        config = parse_database_url(database_url)
        logger.info(f"Parsed config: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
        return config
    
    # Fallback to individual environment variables
    config = {
        'host': os.environ.get('DB_HOST') or os.environ.get('POSTGRES_HOST') or 'localhost',
        'port': int(os.environ.get('DB_PORT') or os.environ.get('POSTGRES_PORT') or 5432),
        'database': os.environ.get('DB_NAME') or os.environ.get('POSTGRES_DB') or 'ubec_sensors',
        'user': os.environ.get('DB_USER') or os.environ.get('POSTGRES_USER') or 'postgres',
        'password': os.environ.get('DB_PASSWORD') or os.environ.get('POSTGRES_PASSWORD')
    }
    
    # Password is optional for peer authentication
    if not config['password']:
        logger.warning("No password found - attempting peer authentication")
    
    logger.info(f"Database config: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
    
    return config


def parse_database_url(url: str) -> Dict[str, Any]:
    """
    Parse DATABASE_URL connection string.
    
    Format: postgresql://user:password@host:port/database
    or: postgres://user:password@host:port/database
    """
    import re
    from urllib.parse import urlparse, parse_qs, unquote
    
    # Parse the URL
    parsed = urlparse(url)
    
    config = {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/') if parsed.path else 'ubec_sensors',
        'user': unquote(parsed.username) if parsed.username else 'postgres',
    }
    
    # Handle password (may contain special characters)
    if parsed.password:
        config['password'] = unquote(parsed.password)
    
    return config


class SchemaDocumenter:
    """Comprehensive database schema documentation generator."""
    
    def __init__(self, connection_params: Dict[str, Any], schema_name: str = 'public'):
        """
        Initialize documenter.
        
        Args:
            connection_params: Database connection parameters
            schema_name: PostgreSQL schema to document (default: 'public')
        """
        self.connection_params = connection_params
        self.schema_name = schema_name
        self.conn = None
        self.documentation = {
            'metadata': {},
            'tables': {},
            'relationships': [],
            'indexes': {},
            'triggers': {},
            'functions': {},
            'summary': {}
        }
        
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = True
            logger.info("Connected to database successfully")
        except psycopg2.OperationalError as e:
            if "password authentication failed" in str(e):
                logger.error("Password authentication failed. Check DB_PASSWORD in .env")
            elif "Connection refused" in str(e):
                logger.error("Connection refused. Is PostgreSQL running?")
            else:
                logger.error(f"Connection error: {e}")
            raise
            
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def generate_documentation(self) -> Dict[str, Any]:
        """Generate complete schema documentation."""
        logger.info(f"Documenting schema: '{self.schema_name}'")
        
        try:
            self._document_metadata()
            self._document_tables()
            self._document_relationships()
            self._document_indexes()
            self._document_triggers()
            self._document_functions()
            self._generate_summary()
            
            logger.info("Documentation generated successfully")
            
        except Exception as e:
            logger.error(f"Error during documentation: {e}")
            raise
            
        return self.documentation
        
    def _document_metadata(self):
        """Document database metadata."""
        cursor = self.conn.cursor()
        
        try:
            # PostgreSQL version
            cursor.execute("SELECT version()")
            pg_version = cursor.fetchone()[0]
            
            # Database size
            cursor.execute("""
                SELECT 
                    pg_database_size(current_database()) as size_bytes,
                    pg_size_pretty(pg_database_size(current_database())) as size_pretty
            """)
            db_size = cursor.fetchone()
            
            # Check if schema exists
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = %s
                )
            """, (self.schema_name,))
            schema_exists = cursor.fetchone()[0]
            
            if not schema_exists:
                logger.warning(f"Schema '{self.schema_name}' does not exist!")
                
            self.documentation['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'schema_name': self.schema_name,
                'schema_exists': schema_exists,
                'database_name': self.connection_params['database'],
                'database_version': pg_version.split(',')[0] if pg_version else 'Unknown',
                'database_size': {
                    'bytes': db_size[0] if db_size else 0,
                    'human_readable': db_size[1] if db_size else 'Unknown'
                },
                'documentation_version': '2.0',
                'generator': 'UBEC Schema Documenter'
            }
            
        finally:
            cursor.close()
            
        logger.info("Metadata documented")
        
    def _document_tables(self):
        """Document all tables in the schema."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            # Get all tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """, (self.schema_name,))
            
            tables = cursor.fetchall()
            logger.info(f"Found {len(tables)} tables in schema '{self.schema_name}'")
            
            if len(tables) == 0:
                logger.warning(f"No tables found in schema '{self.schema_name}'")
                return
            
            for (table_name,) in tables:
                logger.info(f"Documenting table: {table_name}")
                
                # Get columns
                cursor.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale,
                        is_nullable,
                        column_default,
                        COALESCE(is_identity, 'NO') as is_identity,
                        COALESCE(is_generated, 'NEVER') as is_generated
                    FROM information_schema.columns
                    WHERE table_schema = %s 
                    AND table_name = %s
                    ORDER BY ordinal_position
                """, (self.schema_name, table_name))
                
                columns = []
                for col in cursor.fetchall():
                    column_info = {
                        'name': col[0],
                        'data_type': self._format_data_type(col[1], col[2], col[3], col[4]),
                        'nullable': col[5] == 'YES',
                        'default': col[6],
                        'is_identity': col[7] == 'YES',
                        'is_generated': col[8] == 'ALWAYS'
                    }
                    columns.append(column_info)
                
                # Get constraints
                cursor.execute("""
                    SELECT 
                        con.conname as constraint_name,
                        con.contype as constraint_type,
                        pg_get_constraintdef(con.oid) as definition
                    FROM pg_constraint con
                    JOIN pg_namespace nsp ON nsp.oid = con.connamespace
                    JOIN pg_class cls ON cls.oid = con.conrelid
                    WHERE nsp.nspname = %s
                    AND cls.relname = %s
                    ORDER BY con.conname
                """, (self.schema_name, table_name))
                
                constraint_type_map = {
                    'p': 'PRIMARY KEY',
                    'u': 'UNIQUE',
                    'c': 'CHECK',
                    'f': 'FOREIGN KEY',
                    'x': 'EXCLUSION'
                }
                
                constraints = []
                for con in cursor.fetchall():
                    constraints.append({
                        'name': con[0],
                        'type': constraint_type_map.get(con[1], con[1]),
                        'definition': con[2]
                    })
                
                # Get table statistics
                try:
                    qualified_table = f'"{self.schema_name}"."{table_name}"'
                    cursor.execute(f"""
                        SELECT 
                            COUNT(*) as row_count,
                            pg_size_pretty(pg_total_relation_size('{qualified_table}'::regclass)) as total_size
                        FROM {qualified_table}
                    """)
                    stats = cursor.fetchone()
                except Exception as e:
                    logger.warning(f"Could not get stats for {table_name}: {e}")
                    stats = (0, 'Unknown')
                
                self.documentation['tables'][table_name] = {
                    'columns': columns,
                    'constraints': constraints,
                    'statistics': {
                        'row_count': stats[0],
                        'total_size': stats[1]
                    }
                }
                
        finally:
            cursor.close()
            
        logger.info(f"Documented {len(self.documentation['tables'])} tables")
        
    def _format_data_type(self, data_type: str, char_length: Optional[int],
                         numeric_precision: Optional[int], numeric_scale: Optional[int]) -> str:
        """Format data type with parameters."""
        if data_type == 'character varying' and char_length:
            return f"varchar({char_length})"
        elif data_type == 'character' and char_length:
            return f"char({char_length})"
        elif data_type == 'numeric' and numeric_precision:
            if numeric_scale and numeric_scale > 0:
                return f"numeric({numeric_precision},{numeric_scale})"
            return f"numeric({numeric_precision})"
        return data_type
            
    def _document_relationships(self):
        """Document foreign key relationships."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    tc.table_name as from_table,
                    kcu.column_name as from_column,
                    ccu.table_name as to_table,
                    ccu.column_name as to_column,
                    tc.constraint_name,
                    rc.update_rule,
                    rc.delete_rule
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu 
                    ON ccu.constraint_name = tc.constraint_name
                JOIN information_schema.referential_constraints rc
                    ON rc.constraint_name = tc.constraint_name
                WHERE tc.table_schema = %s
                AND tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_name, tc.constraint_name
            """, (self.schema_name,))
            
            relationships = []
            for row in cursor.fetchall():
                relationships.append({
                    'from_table': row[0],
                    'from_column': row[1],
                    'to_table': row[2],
                    'to_column': row[3],
                    'constraint_name': row[4],
                    'update_rule': row[5],
                    'delete_rule': row[6],
                    'relationship_type': 'many-to-one'  # Simplified
                })
                
            self.documentation['relationships'] = relationships
            logger.info(f"Documented {len(relationships)} relationships")
            
        finally:
            cursor.close()
            
    def _document_indexes(self):
        """Document indexes."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    indexname,
                    tablename,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = %s
                ORDER BY tablename, indexname
            """, (self.schema_name,))
            
            indexes_by_table = {}
            for row in cursor.fetchall():
                index_name, table_name, index_def = row
                
                if table_name not in indexes_by_table:
                    indexes_by_table[table_name] = []
                
                is_unique = 'UNIQUE' in index_def.upper()
                is_primary = index_name.endswith('_pkey')
                
                indexes_by_table[table_name].append({
                    'name': index_name,
                    'definition': index_def,
                    'is_unique': is_unique,
                    'is_primary': is_primary
                })
            
            self.documentation['indexes'] = indexes_by_table
            total = sum(len(idxs) for idxs in indexes_by_table.values())
            logger.info(f"Documented {total} indexes")
            
        finally:
            cursor.close()
            
    def _document_triggers(self):
        """Document triggers."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    trigger_name,
                    event_object_table,
                    event_manipulation,
                    action_timing,
                    action_orientation,
                    action_statement
                FROM information_schema.triggers
                WHERE trigger_schema = %s
                ORDER BY event_object_table, trigger_name
            """, (self.schema_name,))
            
            triggers_by_table = {}
            for row in cursor.fetchall():
                trigger_name, table_name, event, timing, orientation, action = row
                
                if table_name not in triggers_by_table:
                    triggers_by_table[table_name] = []
                    
                triggers_by_table[table_name].append({
                    'name': trigger_name,
                    'event': event,
                    'timing': timing,
                    'orientation': orientation,
                    'action': action
                })
                
            self.documentation['triggers'] = triggers_by_table
            total = sum(len(trgs) for trgs in triggers_by_table.values())
            logger.info(f"Documented {total} triggers")
            
        except Exception as e:
            logger.warning(f"Could not document triggers: {e}")
            self.documentation['triggers'] = {}
            
        finally:
            cursor.close()
            
    def _document_functions(self):
        """Document functions and procedures."""
        cursor = self.conn.cursor()
        
        try:
            # Try modern PostgreSQL (11+) query first
            try:
                cursor.execute("""
                    SELECT 
                        p.proname as function_name,
                        pg_get_function_result(p.oid) as return_type,
                        pg_get_function_arguments(p.oid) as arguments,
                        l.lanname as language
                    FROM pg_proc p
                    JOIN pg_namespace n ON n.oid = p.pronamespace
                    JOIN pg_language l ON l.oid = p.prolang
                    WHERE n.nspname = %s
                    AND p.prokind IN ('f', 'p')
                    ORDER BY p.proname
                """, (self.schema_name,))
            except psycopg2.ProgrammingError:
                # Fallback for older PostgreSQL versions
                self.conn.rollback()
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT 
                        p.proname as function_name,
                        pg_get_function_result(p.oid) as return_type,
                        pg_get_function_arguments(p.oid) as arguments,
                        l.lanname as language
                    FROM pg_proc p
                    JOIN pg_namespace n ON n.oid = p.pronamespace
                    JOIN pg_language l ON l.oid = p.prolang
                    WHERE n.nspname = %s
                    AND NOT p.proisagg
                    ORDER BY p.proname
                """, (self.schema_name,))
            
            functions = []
            for row in cursor.fetchall():
                functions.append({
                    'name': row[0],
                    'return_type': row[1],
                    'arguments': row[2],
                    'language': row[3]
                })
                
            self.documentation['functions'] = functions
            logger.info(f"Documented {len(functions)} functions")
            
        except Exception as e:
            logger.warning(f"Could not document functions: {e}")
            self.documentation['functions'] = []
            if self.conn:
                self.conn.rollback()
            
        finally:
            cursor.close()
            
    def _generate_summary(self):
        """Generate summary statistics."""
        summary = {
            'total_tables': len(self.documentation['tables']),
            'total_columns': sum(len(t['columns']) for t in self.documentation['tables'].values()),
            'total_relationships': len(self.documentation['relationships']),
            'total_indexes': sum(len(idxs) for idxs in self.documentation['indexes'].values()),
            'total_triggers': sum(len(trgs) for trgs in self.documentation['triggers'].values()),
            'total_functions': len(self.documentation['functions']),
            'tables_by_size': []
        }
        
        # Sort tables by row count
        for table_name, table_info in self.documentation['tables'].items():
            stats = table_info['statistics']
            summary['tables_by_size'].append({
                'table': table_name,
                'rows': stats['row_count'],
                'size': stats['total_size']
            })
        
        summary['tables_by_size'].sort(key=lambda x: x['rows'], reverse=True)
        
        self.documentation['summary'] = summary
        logger.info("Summary generated")
        
    def save_documentation(self, output_format: str = 'markdown', output_file: str = None):
        """Save documentation to file."""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"schema_doc_{self.schema_name}_{timestamp}"
            
        if output_format == 'markdown':
            self._save_as_markdown(f"{output_file}.md")
        elif output_format == 'json':
            self._save_as_json(f"{output_file}.json")
        else:
            raise ValueError(f"Unsupported format: {output_format}")
            
    def _save_as_markdown(self, filename: str):
        """Save as Markdown file."""
        with open(filename, 'w', encoding='utf-8') as f:
            meta = self.documentation['metadata']
            summary = self.documentation['summary']
            
            # Header
            f.write(f"# Database Schema Documentation\n\n")
            f.write(f"**Schema:** {meta['schema_name']}\n")
            f.write(f"**Database:** {meta['database_name']}\n")
            f.write(f"**Generated:** {meta['generated_at']}\n")
            f.write(f"**PostgreSQL Version:** {meta['database_version']}\n\n")
            
            if not meta['schema_exists']:
                f.write("⚠️ **WARNING: Schema does not exist!**\n\n")
                
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Tables:** {summary['total_tables']}\n")
            f.write(f"- **Total Columns:** {summary['total_columns']}\n")
            f.write(f"- **Total Relationships:** {summary['total_relationships']}\n")
            f.write(f"- **Total Indexes:** {summary['total_indexes']}\n")
            f.write(f"- **Database Size:** {meta['database_size']['human_readable']}\n\n")
            
            if summary['total_tables'] == 0:
                f.write("**No tables found in this schema.**\n\n")
                return
            
            # Tables
            f.write("## Tables\n\n")
            for table_name in sorted(self.documentation['tables'].keys()):
                table = self.documentation['tables'][table_name]
                f.write(f"### {table_name}\n\n")
                f.write(f"**Rows:** {table['statistics']['row_count']:,} | ")
                f.write(f"**Size:** {table['statistics']['total_size']}\n\n")
                
                # Columns
                f.write("| Column | Type | Nullable | Default |\n")
                f.write("|--------|------|----------|----------|\n")
                
                for col in table['columns']:
                    nullable = "✓" if col['nullable'] else "✗"
                    default = col['default'] or "-"
                    if len(str(default)) > 40:
                        default = str(default)[:37] + "..."
                    f.write(f"| {col['name']} | {col['data_type']} | {nullable} | {default} |\n")
                
                # Constraints
                if table['constraints']:
                    f.write("\n**Constraints:**\n\n")
                    for con in table['constraints']:
                        f.write(f"- `{con['name']}` ({con['type']})\n")
                
                # Indexes
                if table_name in self.documentation['indexes']:
                    f.write("\n**Indexes:**\n\n")
                    for idx in self.documentation['indexes'][table_name]:
                        flags = []
                        if idx['is_primary']:
                            flags.append("PRIMARY")
                        if idx['is_unique']:
                            flags.append("UNIQUE")
                        flag_str = f" ({', '.join(flags)})" if flags else ""
                        f.write(f"- `{idx['name']}`{flag_str}\n")
                
                f.write("\n---\n\n")
            
            # Relationships
            if self.documentation['relationships']:
                f.write("## Relationships\n\n")
                f.write("| From Table | Column | To Table | Column | On Delete |\n")
                f.write("|------------|--------|----------|--------|------------|\n")
                
                for rel in self.documentation['relationships']:
                    f.write(f"| {rel['from_table']} | {rel['from_column']} | ")
                    f.write(f"{rel['to_table']} | {rel['to_column']} | ")
                    f.write(f"{rel['delete_rule']} |\n")
                
                f.write("\n")
        
        print(f"\n✅ Documentation saved to: {filename}\n")
        logger.info(f"Saved to {filename}")
        
    def _save_as_json(self, filename: str):
        """Save as JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.documentation, f, indent=2, default=str)
        
        print(f"\n✅ Documentation saved to: {filename}\n")
        logger.info(f"Saved to {filename}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate database schema documentation for UBEC'
    )
    
    # Get default config
    try:
        env_config = get_database_config()
    except Exception as e:
        print(f"\n❌ Configuration Error: {e}\n")
        return 1
    
    # Arguments
    parser.add_argument('--host', default=env_config['host'])
    parser.add_argument('--port', type=int, default=env_config['port'])
    parser.add_argument('--database', default=env_config['database'])
    parser.add_argument('--user', default=env_config['user'])
    parser.add_argument('--password', default=env_config.get('password'))
    parser.add_argument('--schema', default='public',
                       help='Schema name to document (default: public)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--all-schemas', action='store_true',
                       help='Document all schemas (public, ubec_sensors, phenomenological)')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    conn_params = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user
    }
    
    if args.password:
        conn_params['password'] = args.password
    
    print(f"\n📊 UBEC Schema Documentation Generator")
    print(f"=" * 60)
    print(f"Database: {conn_params['database']}@{conn_params['host']}")
    
    schemas_to_document = []
    if args.all_schemas:
        schemas_to_document = ['public', 'ubec_sensors', 'phenomenological']
        print(f"Documenting all schemas: {', '.join(schemas_to_document)}")
    else:
        schemas_to_document = [args.schema]
        print(f"Schema: {args.schema}")
    
    print(f"=" * 60 + "\n")
    
    all_success = True
    
    for schema in schemas_to_document:
        print(f"📋 Documenting schema: {schema}")
        
        documenter = SchemaDocumenter(conn_params, schema)
        
        try:
            documenter.connect()
            documenter.generate_documentation()
            
            # Generate output filename for this schema
            if args.output and not args.all_schemas:
                output_file = args.output
            else:
                output_file = None  # Auto-generate
            
            documenter.save_documentation(args.format, output_file)
            
            # Print summary
            summary = documenter.documentation['summary']
            print(f"\n   Tables: {summary['total_tables']}")
            print(f"   Columns: {summary['total_columns']}")
            print(f"   Relationships: {summary['total_relationships']}")
            print(f"   Indexes: {summary['total_indexes']}\n")
            
        except Exception as e:
            logger.error(f"Error documenting {schema}: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            all_success = False
            
        finally:
            documenter.disconnect()
    
    if all_success:
        print("✅ Documentation complete!\n")
        return 0
    else:
        print("⚠️  Some schemas could not be documented\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
