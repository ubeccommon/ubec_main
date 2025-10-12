#!/usr/bin/env python3
"""
UBEC Protocol Suite - Comprehensive Multi-Schema Database Documentation Generator

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Generates comprehensive documentation across ALL schemas in the UBEC database:
- Auto-discovers all available schemas
- Documents ubec_main (Four-Element Protocol)
- Documents phenomenal (Quantum Gravity Analysis)
- Documents ubec_recipro (Legacy Reciprocity)
- Documents any custom schemas
- Cross-schema relationship tracking
- Complete database overview

Version: 4.0 - Multi-Schema Comprehensive Edition
Date: October 12, 2025
"""

import psycopg2
import psycopg2.extras
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
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

# UBEC Protocol Constants
ELEMENTS = {
    'air': {'symbol': '🜁', 'token': 'UBEC', 'principle': 'Diversity', 'role': 'Gateway & Universal Access'},
    'water': {'symbol': '🜄', 'token': 'UBECrc', 'principle': 'Reciprocity', 'role': 'Flow & Exchange'},
    'earth': {'symbol': '🜃', 'token': 'UBECgpi', 'principle': 'Mutualism', 'role': 'Stability & Value'},
    'fire': {'symbol': '🜂', 'token': 'UBECtt', 'principle': 'Regeneration', 'role': 'Transformation & Action'}
}

# Known schema descriptions
SCHEMA_DESCRIPTIONS = {
    'ubec_main': 'Four-Element Protocol - Primary operational schema for UBEC token management',
    'phenomenal': 'Phenomenological Quantum Gravity Schema - Advanced analytics and network topology',
    'topology': 'PostGIS Topology Schema - Spatial network topology and geometric relationships',
    'public': 'PostgreSQL default schema - PostGIS extensions and shared utilities'
}


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
        Path('/home/triag/UBEC/projects/UBEC') / '.env',
    ]
    
    for env_path in paths_to_check:
        if env_path.exists():
            logger.info(f"Loading .env from: {env_path}")
            load_dotenv(env_path)
            return True
    
    logger.warning("No .env file found")
    return False


def get_database_config():
    """Get database configuration from environment with UBEC-specific fallbacks."""
    find_and_load_env_file()
    
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        logger.info(f"Found DATABASE_URL, parsing connection string")
        config = parse_database_url(database_url)
        logger.info(f"Parsed config: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
        return config
    
    config = {
        'host': os.environ.get('UBEC_DB_HOST') or os.environ.get('DB_HOST') or 'localhost',
        'port': int(os.environ.get('UBEC_DB_PORT') or os.environ.get('DB_PORT') or 5432),
        'database': os.environ.get('UBEC_DB_NAME') or os.environ.get('DB_NAME') or 'ubec',
        'user': os.environ.get('UBEC_DB_USER') or os.environ.get('DB_USER') or 'ubec_app',
        'password': os.environ.get('UBEC_DB_PASSWORD') or os.environ.get('DB_PASSWORD')
    }
    
    if not config['password']:
        logger.warning("No password found - attempting peer authentication")
    
    logger.info(f"Database config: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
    
    return config


def parse_database_url(url: str) -> Dict[str, Any]:
    """Parse DATABASE_URL connection string."""
    from urllib.parse import urlparse, unquote
    
    parsed = urlparse(url)
    
    config = {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/') if parsed.path else 'ubec',
        'user': unquote(parsed.username) if parsed.username else 'ubec_app',
    }
    
    if parsed.password:
        config['password'] = unquote(parsed.password)
    
    return config


class UBECComprehensiveDocumenter:
    """Comprehensive multi-schema database documentation generator."""
    
    def __init__(self, connection_params: Dict[str, Any], 
                 schemas: Optional[List[str]] = None,
                 exclude_system_schemas: bool = True):
        """
        Initialize comprehensive documenter.
        
        Args:
            connection_params: Database connection parameters
            schemas: Specific schemas to document (None = auto-discover all)
            exclude_system_schemas: Exclude pg_* and information_schema
        """
        self.connection_params = connection_params
        self.requested_schemas = schemas
        self.exclude_system_schemas = exclude_system_schemas
        self.conn = None
        self.discovered_schemas = []
        self.documentation = {
            'metadata': {},
            'database_overview': {},
            'schemas': {},
            'cross_schema_analysis': {
                'total_tables': 0,
                'total_relationships': 0,
                'schema_dependencies': []
            }
        }
        
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = True
            logger.info("Connected to UBEC database successfully")
        except psycopg2.OperationalError as e:
            if "password authentication failed" in str(e):
                logger.error("Password authentication failed. Check UBEC_DB_PASSWORD in .env")
            elif "Connection refused" in str(e):
                logger.error("Connection refused. Is PostgreSQL running?")
            elif "does not exist" in str(e):
                logger.error(f"Database '{self.connection_params['database']}' does not exist.")
            else:
                logger.error(f"Connection error: {e}")
            raise
            
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def discover_schemas(self) -> List[str]:
        """Discover all available schemas in the database."""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT schema_name, 
                       COUNT(table_name) as table_count
                FROM information_schema.schemata s
                LEFT JOIN information_schema.tables t 
                    ON s.schema_name = t.table_schema 
                    AND t.table_type = 'BASE TABLE'
                WHERE 1=1
            """
            
            if self.exclude_system_schemas:
                query += """
                    AND schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND schema_name NOT LIKE 'pg_%'
                """
            
            query += """
                GROUP BY schema_name
                ORDER BY table_count DESC, schema_name
            """
            
            cursor.execute(query)
            schemas_info = cursor.fetchall()
            
            schemas = []
            logger.info("Discovered schemas:")
            for schema_name, table_count in schemas_info:
                schemas.append(schema_name)
                table_desc = f"{table_count} tables" if table_count > 0 else "empty"
                logger.info(f"  - {schema_name}: {table_desc}")
            
            return schemas
            
        finally:
            cursor.close()
    
    def generate_documentation(self) -> Dict[str, Any]:
        """Generate comprehensive multi-schema documentation."""
        logger.info("Starting comprehensive database documentation...")
        
        try:
            # Document database metadata
            self._document_database_metadata()
            
            # Discover schemas
            if self.requested_schemas:
                self.discovered_schemas = self.requested_schemas
                logger.info(f"Using requested schemas: {self.requested_schemas}")
            else:
                self.discovered_schemas = self.discover_schemas()
                logger.info(f"Auto-discovered {len(self.discovered_schemas)} schemas")
            
            # Document each schema
            for schema_name in self.discovered_schemas:
                logger.info(f"\n{'='*70}")
                logger.info(f"Documenting schema: {schema_name}")
                logger.info(f"{'='*70}")
                
                schema_doc = self._document_schema(schema_name)
                self.documentation['schemas'][schema_name] = schema_doc
            
            # Cross-schema analysis
            self._analyze_cross_schema_relationships()
            
            # Generate overview
            self._generate_database_overview()
            
            logger.info("\n✅ Comprehensive documentation generated successfully")
            
        except Exception as e:
            logger.error(f"Error during documentation: {e}")
            raise
            
        return self.documentation
    
    def _document_database_metadata(self):
        """Document database-level metadata."""
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
            
            # Total schemas
            cursor.execute("""
                SELECT COUNT(DISTINCT schema_name)
                FROM information_schema.schemata
                WHERE schema_name NOT LIKE 'pg_%'
                AND schema_name != 'information_schema'
            """)
            total_schemas = cursor.fetchone()[0]
            
            # Total tables
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema NOT LIKE 'pg_%'
                AND table_schema != 'information_schema'
                AND table_type = 'BASE TABLE'
            """)
            total_tables = cursor.fetchone()[0]
            
            self.documentation['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'database_name': self.connection_params['database'],
                'database_host': self.connection_params['host'],
                'database_version': pg_version.split(',')[0] if pg_version else 'Unknown',
                'database_size': {
                    'bytes': db_size[0] if db_size else 0,
                    'human_readable': db_size[1] if db_size else 'Unknown'
                },
                'total_schemas': total_schemas,
                'total_tables': total_tables,
                'documentation_version': '4.0 - Multi-Schema',
                'generator': 'UBEC Comprehensive Schema Documenter'
            }
            
        finally:
            cursor.close()
            
        logger.info("Database metadata documented")
    
    def _document_schema(self, schema_name: str) -> Dict[str, Any]:
        """Document a single schema comprehensively."""
        schema_doc = {
            'schema_name': schema_name,
            'description': SCHEMA_DESCRIPTIONS.get(schema_name, 'Custom schema'),
            'tables': {},
            'views': {},
            'functions': {},
            'triggers': {},
            'indexes': {},
            'relationships': [],
            'custom_types': {},
            'statistics': {}
        }
        
        # Get schema-specific info
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            # Schema comment
            cursor.execute("""
                SELECT obj_description(oid, 'pg_namespace') as description
                FROM pg_namespace
                WHERE nspname = %s
            """, (schema_name,))
            result = cursor.fetchone()
            if result and result['description']:
                schema_doc['description'] = result['description']
            
            # Tables
            schema_doc['tables'] = self._document_tables(schema_name)
            
            # Views
            schema_doc['views'] = self._document_views(schema_name)
            
            # Custom types
            schema_doc['custom_types'] = self._document_custom_types(schema_name)
            
            # Relationships
            schema_doc['relationships'] = self._document_relationships(schema_name)
            
            # Indexes
            schema_doc['indexes'] = self._document_indexes(schema_name)
            
            # Triggers
            schema_doc['triggers'] = self._document_triggers(schema_name)
            
            # Functions
            schema_doc['functions'] = self._document_functions(schema_name)
            
            # Statistics
            schema_doc['statistics'] = self._generate_schema_statistics(schema_doc)
            
        finally:
            cursor.close()
        
        return schema_doc
    
    def _document_tables(self, schema_name: str) -> Dict[str, Any]:
        """Document all tables in a schema."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        tables = {}
        
        try:
            # Get all tables
            cursor.execute("""
                SELECT 
                    t.table_name,
                    obj_description((quote_ident(t.table_schema)||'.'||quote_ident(t.table_name))::regclass, 'pg_class') as table_comment
                FROM information_schema.tables t
                WHERE t.table_schema = %s 
                AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name
            """, (schema_name,))
            
            table_list = cursor.fetchall()
            
            for row in table_list:
                table_name = row['table_name']
                table_comment = row['table_comment']
                
                # Get columns
                cursor.execute("""
                    SELECT 
                        c.column_name,
                        c.data_type,
                        c.character_maximum_length,
                        c.numeric_precision,
                        c.numeric_scale,
                        c.is_nullable,
                        c.column_default,
                        COALESCE(c.is_identity, 'NO') as is_identity,
                        COALESCE(c.is_generated, 'NEVER') as is_generated,
                        col_description((quote_ident(%s)||'.'||quote_ident(%s))::regclass, c.ordinal_position) as column_comment
                    FROM information_schema.columns c
                    WHERE c.table_schema = %s 
                    AND c.table_name = %s
                    ORDER BY c.ordinal_position
                """, (schema_name, table_name, schema_name, table_name))
                
                columns = []
                for col in cursor.fetchall():
                    column_info = {
                        'name': col['column_name'],
                        'data_type': self._format_data_type(
                            col['data_type'], 
                            col['character_maximum_length'],
                            col['numeric_precision'], 
                            col['numeric_scale']
                        ),
                        'nullable': col['is_nullable'] == 'YES',
                        'default': col['column_default'],
                        'is_identity': col['is_identity'] == 'YES',
                        'is_generated': col['is_generated'] == 'ALWAYS',
                        'comment': col['column_comment']
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
                """, (schema_name, table_name))
                
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
                        'name': con['constraint_name'],
                        'type': constraint_type_map.get(con['constraint_type'], con['constraint_type']),
                        'definition': con['definition']
                    })
                
                # Get table statistics
                try:
                    qualified_table = f'"{schema_name}"."{table_name}"'
                    cursor.execute(f"""
                        SELECT 
                            COUNT(*) as row_count,
                            pg_size_pretty(pg_total_relation_size('{qualified_table}'::regclass)) as total_size,
                            pg_size_pretty(pg_table_size('{qualified_table}'::regclass)) as table_size,
                            pg_size_pretty(pg_indexes_size('{qualified_table}'::regclass)) as index_size
                        FROM {qualified_table}
                    """)
                    stats_result = cursor.fetchone()
                    if stats_result:
                        stats = {
                            'row_count': stats_result['row_count'] or 0,
                            'total_size': stats_result['total_size'] or 'Unknown',
                            'table_size': stats_result['table_size'] or 'Unknown',
                            'index_size': stats_result['index_size'] or 'Unknown'
                        }
                    else:
                        stats = {'row_count': 0, 'total_size': 'Unknown', 'table_size': 'Unknown', 'index_size': 'Unknown'}
                except Exception as e:
                    logger.debug(f"Could not get stats for {schema_name}.{table_name}: {e}")
                    stats = {'row_count': 0, 'total_size': 'Unknown', 'table_size': 'Unknown', 'index_size': 'Unknown'}
                
                tables[table_name] = {
                    'comment': table_comment,
                    'columns': columns,
                    'constraints': constraints,
                    'statistics': stats
                }
                
        finally:
            cursor.close()
        
        return tables
    
    def _document_views(self, schema_name: str) -> Dict[str, Any]:
        """Document views in a schema."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        views = {}
        
        try:
            cursor.execute("""
                SELECT 
                    table_name,
                    view_definition
                FROM information_schema.views
                WHERE table_schema = %s
                ORDER BY table_name
            """, (schema_name,))
            
            for row in cursor.fetchall():
                views[row['table_name']] = {
                    'definition': row['view_definition']
                }
                
        finally:
            cursor.close()
        
        return views
    
    def _document_custom_types(self, schema_name: str) -> Dict[str, Any]:
        """Document custom types in a schema."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        custom_types = {}
        
        try:
            # Get custom enum types
            cursor.execute("""
                SELECT 
                    t.typname as type_name,
                    array_agg(e.enumlabel ORDER BY e.enumsortorder) as enum_values
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE n.nspname = %s
                GROUP BY t.typname
                ORDER BY t.typname
            """, (schema_name,))
            
            for row in cursor.fetchall():
                type_name = row['type_name']
                enum_values = row['enum_values']
                
                custom_types[type_name] = {
                    'type': 'enum',
                    'values': enum_values
                }
                
        finally:
            cursor.close()
        
        return custom_types
    
    def _document_relationships(self, schema_name: str) -> List[Dict[str, Any]]:
        """Document foreign key relationships in a schema."""
        cursor = self.conn.cursor()
        relationships = []
        
        try:
            cursor.execute("""
                SELECT 
                    tc.table_schema as from_schema,
                    tc.table_name as from_table,
                    kcu.column_name as from_column,
                    ccu.table_schema as to_schema,
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
            """, (schema_name,))
            
            for row in cursor.fetchall():
                relationships.append({
                    'from_schema': row[0],
                    'from_table': row[1],
                    'from_column': row[2],
                    'to_schema': row[3],
                    'to_table': row[4],
                    'to_column': row[5],
                    'constraint_name': row[6],
                    'update_rule': row[7],
                    'delete_rule': row[8],
                    'is_cross_schema': row[0] != row[3]
                })
                
        finally:
            cursor.close()
        
        return relationships
    
    def _document_indexes(self, schema_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Document indexes in a schema."""
        cursor = self.conn.cursor()
        indexes_by_table = {}
        
        try:
            cursor.execute("""
                SELECT 
                    indexname,
                    tablename,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = %s
                ORDER BY tablename, indexname
            """, (schema_name,))
            
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
                
        finally:
            cursor.close()
        
        return indexes_by_table
    
    def _document_triggers(self, schema_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Document triggers in a schema."""
        cursor = self.conn.cursor()
        triggers_by_table = {}
        
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
            """, (schema_name,))
            
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
                
        except Exception as e:
            logger.debug(f"Could not document triggers for {schema_name}: {e}")
            
        finally:
            cursor.close()
        
        return triggers_by_table
    
    def _document_functions(self, schema_name: str) -> List[Dict[str, Any]]:
        """Document functions in a schema."""
        cursor = self.conn.cursor()
        functions = []
        
        try:
            try:
                cursor.execute("""
                    SELECT 
                        p.proname as function_name,
                        pg_get_function_result(p.oid) as return_type,
                        pg_get_function_arguments(p.oid) as arguments,
                        l.lanname as language,
                        obj_description(p.oid, 'pg_proc') as description
                    FROM pg_proc p
                    JOIN pg_namespace n ON n.oid = p.pronamespace
                    JOIN pg_language l ON l.oid = p.prolang
                    WHERE n.nspname = %s
                    AND p.prokind IN ('f', 'p')
                    ORDER BY p.proname
                """, (schema_name,))
            except psycopg2.ProgrammingError:
                self.conn.rollback()
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT 
                        p.proname as function_name,
                        pg_get_function_result(p.oid) as return_type,
                        pg_get_function_arguments(p.oid) as arguments,
                        l.lanname as language,
                        obj_description(p.oid, 'pg_proc') as description
                    FROM pg_proc p
                    JOIN pg_namespace n ON n.oid = p.pronamespace
                    JOIN pg_language l ON l.oid = p.prolang
                    WHERE n.nspname = %s
                    AND NOT p.proisagg
                    ORDER BY p.proname
                """, (schema_name,))
            
            for row in cursor.fetchall():
                functions.append({
                    'name': row[0],
                    'return_type': row[1],
                    'arguments': row[2],
                    'language': row[3],
                    'description': row[4]
                })
                
        except Exception as e:
            logger.debug(f"Could not document functions for {schema_name}: {e}")
            if self.conn:
                self.conn.rollback()
            
        finally:
            cursor.close()
        
        return functions
    
    def _generate_schema_statistics(self, schema_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistics for a schema."""
        stats = {
            'total_tables': len(schema_doc['tables']),
            'total_columns': sum(len(t['columns']) for t in schema_doc['tables'].values()),
            'total_views': len(schema_doc['views']),
            'total_relationships': len(schema_doc['relationships']),
            'total_indexes': sum(len(idxs) for idxs in schema_doc['indexes'].values()),
            'total_triggers': sum(len(trgs) for trgs in schema_doc['triggers'].values()),
            'total_functions': len(schema_doc['functions']),
            'total_custom_types': len(schema_doc['custom_types']),
            'total_rows': 0,
            'tables_by_size': []
        }
        
        # Calculate total rows and sort tables by size
        for table_name, table_info in schema_doc['tables'].items():
            row_count = table_info.get('statistics', {}).get('row_count', 0)
            stats['total_rows'] += row_count
            
            stats['tables_by_size'].append({
                'table': table_name,
                'rows': row_count,
                'size': table_info.get('statistics', {}).get('total_size', 'Unknown')
            })
        
        stats['tables_by_size'].sort(key=lambda x: x['rows'], reverse=True)
        
        return stats
    
    def _analyze_cross_schema_relationships(self):
        """Analyze relationships that cross schema boundaries."""
        cross_schema_rels = []
        
        for schema_name, schema_doc in self.documentation['schemas'].items():
            for rel in schema_doc['relationships']:
                if rel.get('is_cross_schema'):
                    cross_schema_rels.append({
                        'from': f"{rel['from_schema']}.{rel['from_table']}.{rel['from_column']}",
                        'to': f"{rel['to_schema']}.{rel['to_table']}.{rel['to_column']}",
                        'constraint': rel['constraint_name']
                    })
        
        self.documentation['cross_schema_analysis']['cross_schema_relationships'] = cross_schema_rels
        self.documentation['cross_schema_analysis']['total_cross_schema_relationships'] = len(cross_schema_rels)
        
        # Calculate dependencies between schemas
        schema_deps = {}
        for rel in cross_schema_rels:
            from_schema = rel['from'].split('.')[0]
            to_schema = rel['to'].split('.')[0]
            
            if from_schema not in schema_deps:
                schema_deps[from_schema] = set()
            schema_deps[from_schema].add(to_schema)
        
        # Convert sets to lists for JSON serialization
        self.documentation['cross_schema_analysis']['schema_dependencies'] = {
            k: list(v) for k, v in schema_deps.items()
        }
    
    def _generate_database_overview(self):
        """Generate overall database overview."""
        overview = {
            'schemas': {},
            'totals': {
                'tables': 0,
                'columns': 0,
                'views': 0,
                'relationships': 0,
                'indexes': 0,
                'triggers': 0,
                'functions': 0,
                'custom_types': 0,
                'rows': 0
            }
        }
        
        for schema_name, schema_doc in self.documentation['schemas'].items():
            stats = schema_doc['statistics']
            
            overview['schemas'][schema_name] = {
                'description': schema_doc['description'],
                'tables': stats['total_tables'],
                'rows': stats['total_rows'],
                'views': stats['total_views'],
                'functions': stats['total_functions']
            }
            
            # Add to totals
            overview['totals']['tables'] += stats['total_tables']
            overview['totals']['columns'] += stats['total_columns']
            overview['totals']['views'] += stats['total_views']
            overview['totals']['relationships'] += stats['total_relationships']
            overview['totals']['indexes'] += stats['total_indexes']
            overview['totals']['triggers'] += stats['total_triggers']
            overview['totals']['functions'] += stats['total_functions']
            overview['totals']['custom_types'] += stats['total_custom_types']
            overview['totals']['rows'] += stats['total_rows']
        
        self.documentation['database_overview'] = overview
    
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
        elif data_type == 'USER-DEFINED':
            return 'enum'
        return data_type
    
    def save_documentation(self, output_format: str = 'markdown', output_file: str = None):
        """Save comprehensive documentation to file."""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            db_name = self.connection_params['database']
            output_file = f"ubec_comprehensive_doc_{db_name}_{timestamp}"
            
        if output_format == 'markdown':
            self._save_as_markdown(f"{output_file}.md")
        elif output_format == 'json':
            self._save_as_json(f"{output_file}.json")
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _save_as_markdown(self, filename: str):
        """Save as comprehensive Markdown file with robust error handling."""
        logger.info(f"Starting markdown generation: {filename}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                meta = self.documentation.get('metadata', {})
                overview = self.documentation.get('database_overview', {})
                
                # Header
                f.write(f"# UBEC Protocol Suite - Comprehensive Database Documentation\n\n")
                f.write(f"## 🜁 🜄 🜃 🜂 Complete Multi-Schema Analysis\n\n")
                f.write(f"**Database:** `{meta['database_name']}`  \n")
                f.write(f"**Host:** `{meta['database_host']}`  \n")
                f.write(f"**Generated:** {meta['generated_at']}  \n")
                f.write(f"**PostgreSQL Version:** {meta['database_version']}  \n")
                f.write(f"**Documentation Version:** {meta['documentation_version']}  \n")
                f.write(f"**Database Size:** {meta['database_size']['human_readable']}  \n\n")
                
                # Database Overview
                f.write("## 📊 Database Overview\n\n")
                f.write(f"**Total Schemas:** {meta.get('total_schemas', 0)}  \n")
                
                totals = overview.get('totals', {})
                f.write(f"**Total Tables:** {totals.get('tables', 0)}  \n")
                f.write(f"**Total Rows:** {totals.get('rows', 0):,}  \n")
                f.write(f"**Total Columns:** {totals.get('columns', 0):,}  \n")
                f.write(f"**Total Views:** {totals.get('views', 0)}  \n")
                f.write(f"**Total Functions:** {totals.get('functions', 0)}  \n")
                f.write(f"**Total Relationships:** {totals.get('relationships', 0)}  \n")
                f.write(f"**Total Indexes:** {totals.get('indexes', 0)}  \n\n")
                
                # Schema Summary
                schemas_info = overview.get('schemas', {})
                if schemas_info:
                    f.write("### Schemas in Database\n\n")
                    f.write("| Schema | Description | Tables | Rows | Views | Functions |\n")
                    f.write("|--------|-------------|--------|------|-------|------------|\n")
                    
                    for schema_name, schema_info in schemas_info.items():
                        desc = schema_info.get('description', 'No description')[:40]
                        f.write(f"| {schema_name} | {desc}... | ")
                        f.write(f"{schema_info.get('tables', 0)} | {schema_info.get('rows', 0):,} | ")
                        f.write(f"{schema_info.get('views', 0)} | {schema_info.get('functions', 0)} |\n")
                    f.write("\n")
                
                # Cross-Schema Analysis
                cross = self.documentation.get('cross_schema_analysis', {})
                cross_rels = cross.get('cross_schema_relationships', [])
                if cross_rels:
                    f.write("### Cross-Schema Relationships\n\n")
                    f.write(f"**Total Cross-Schema Foreign Keys:** {cross.get('total_cross_schema_relationships', 0)}\n\n")
                    
                    schema_deps = cross.get('schema_dependencies', {})
                    if schema_deps:
                        f.write("**Schema Dependencies:**\n\n")
                        for from_schema, to_schemas in schema_deps.items():
                            f.write(f"- `{from_schema}` → {', '.join(f'`{s}`' for s in to_schemas)}\n")
                        f.write("\n")
                
                f.write("---\n\n")
                
                # Detailed Schema Documentation
                for schema_name in sorted(self.documentation['schemas'].keys()):
                    try:
                        logger.info(f"Writing documentation for schema: {schema_name}")
                        schema_doc = self.documentation['schemas'][schema_name]
                        stats = schema_doc['statistics']
                        
                        f.write(f"## Schema: `{schema_name}`\n\n")
                        f.write(f"**Description:** {schema_doc['description']}\n\n")
                        
                        # Schema Statistics
                        f.write("### Schema Statistics\n\n")
                        f.write(f"- **Tables:** {stats['total_tables']}\n")
                        f.write(f"- **Total Rows:** {stats['total_rows']:,}\n")
                        f.write(f"- **Columns:** {stats['total_columns']}\n")
                        f.write(f"- **Views:** {stats['total_views']}\n")
                        f.write(f"- **Relationships:** {stats['total_relationships']}\n")
                        f.write(f"- **Indexes:** {stats['total_indexes']}\n")
                        f.write(f"- **Triggers:** {stats['total_triggers']}\n")
                        f.write(f"- **Functions:** {stats['total_functions']}\n")
                        f.write(f"- **Custom Types:** {stats['total_custom_types']}\n\n")
                        
                        # Custom Types
                        if schema_doc['custom_types']:
                            try:
                                logger.info(f"  Writing custom types for {schema_name}")
                                f.write("### Custom Types\n\n")
                                for type_name, type_info in schema_doc['custom_types'].items():
                                    f.write(f"#### {type_name}\n\n")
                                    f.write(f"**Values:** {', '.join(f'`{v}`' for v in type_info['values'])}\n\n")
                            except Exception as e:
                                logger.error(f"Error writing custom types for {schema_name}: {e}")
                                f.write(f"\n*Error documenting custom types: {e}*\n\n")
                        
                        # Tables
                        if schema_doc['tables']:
                            try:
                                logger.info(f"  Writing {len(schema_doc['tables'])} tables for {schema_name}")
                                f.write("### Tables\n\n")
                                
                                # Table summary
                                f.write("| Table | Rows | Columns | Size |\n")
                                f.write("|-------|------|---------|------|\n")
                                for table_info in stats['tables_by_size'][:20]:  # Top 20
                                    table_name = table_info['table']
                                    if table_name in schema_doc['tables']:
                                        table = schema_doc['tables'][table_name]
                                        f.write(f"| {table_name} | {table_info['rows']:,} | ")
                                        f.write(f"{len(table['columns'])} | {table_info['size']} |\n")
                                f.write("\n")
                                
                                # Detailed table documentation
                                for table_name in sorted(schema_doc['tables'].keys()):
                                    try:
                                        table = schema_doc['tables'][table_name]
                                        
                                        f.write(f"#### {schema_name}.{table_name}\n\n")
                                        
                                        if table.get('comment'):
                                            f.write(f"*{table['comment']}*\n\n")
                                        
                                        # Columns
                                        f.write("| Column | Type | Nullable | Default | Description |\n")
                                        f.write("|--------|------|----------|---------|-------------|\n")
                                        
                                        for col in table['columns']:
                                            nullable = "✓" if col['nullable'] else "✗"
                                            default = col['default'] or "-"
                                            if len(str(default)) > 30:
                                                default = str(default)[:27] + "..."
                                            comment = col['comment'] or "-"
                                            if len(str(comment)) > 40:
                                                comment = str(comment)[:37] + "..."
                                            
                                            col_type = col['data_type']
                                            if col['is_generated']:
                                                col_type += " (gen)"
                                            if col['is_identity']:
                                                col_type += " (id)"
                                                
                                            f.write(f"| {col['name']} | {col_type} | {nullable} | {default} | {comment} |\n")
                                        
                                        f.write("\n")
                                        
                                        # Constraints
                                        if table['constraints']:
                                            f.write("**Constraints:**\n")
                                            for con in table['constraints']:
                                                f.write(f"- `{con['name']}` ({con['type']})\n")
                                            f.write("\n")
                                            
                                    except Exception as e:
                                        logger.error(f"Error writing table {schema_name}.{table_name}: {e}")
                                        f.write(f"\n*Error documenting table {table_name}: {e}*\n\n")
                                        
                            except Exception as e:
                                logger.error(f"Error writing tables section for {schema_name}: {e}")
                                f.write(f"\n*Error documenting tables: {e}*\n\n")
                        
                        # Views
                        if schema_doc['views']:
                            try:
                                logger.info(f"  Writing {len(schema_doc['views'])} views for {schema_name}")
                                f.write("### Views\n\n")
                                for view_name in sorted(schema_doc['views'].keys()):
                                    try:
                                        f.write(f"#### {view_name}\n\n")
                                        f.write("```sql\n")
                                        view_def = schema_doc['views'][view_name]['definition']
                                        # Sanitize view definition to avoid encoding issues
                                        if view_def:
                                            safe_def = view_def.encode('utf-8', errors='replace').decode('utf-8')
                                            f.write(safe_def[:500])
                                            if len(safe_def) > 500:
                                                f.write("\n...\n")
                                        f.write("\n```\n\n")
                                    except Exception as e:
                                        logger.error(f"Error writing view {view_name}: {e}")
                                        f.write(f"\n*Error documenting view {view_name}: {e}*\n\n")
                            except Exception as e:
                                logger.error(f"Error writing views section for {schema_name}: {e}")
                                f.write(f"\n*Error documenting views: {e}*\n\n")
                        
                        # Functions
                        if schema_doc['functions']:
                            try:
                                logger.info(f"  Writing {len(schema_doc['functions'])} functions for {schema_name}")
                                f.write("### Functions\n\n")
                                for func in schema_doc['functions']:
                                    try:
                                        f.write(f"#### {func['name']}({func['arguments']})\n\n")
                                        f.write(f"- **Returns:** {func['return_type']}\n")
                                        f.write(f"- **Language:** {func['language']}\n")
                                        if func.get('description'):
                                            f.write(f"- **Description:** {func['description']}\n")
                                        f.write("\n")
                                    except Exception as e:
                                        logger.error(f"Error writing function {func.get('name', 'unknown')}: {e}")
                                        f.write(f"\n*Error documenting function: {e}*\n\n")
                            except Exception as e:
                                logger.error(f"Error writing functions section for {schema_name}: {e}")
                                f.write(f"\n*Error documenting functions: {e}*\n\n")
                        
                        f.write("---\n\n")
                        logger.info(f"Completed documentation for schema: {schema_name}")
                        
                    except Exception as e:
                        logger.error(f"Error documenting schema {schema_name}: {e}")
                        f.write(f"\n## ERROR: Could not complete documentation for schema `{schema_name}`\n\n")
                        f.write(f"Error: {e}\n\n")
                        f.write("---\n\n")
            
            print(f"\n✅ Comprehensive documentation saved to: {filename}\n")
            logger.info(f"Successfully saved to {filename}")
            
        except Exception as e:
            logger.error(f"Fatal error saving markdown: {e}")
            print(f"\n❌ Error saving documentation: {e}\n")
            raise

    def _save_as_json(self, filename: str):
        """Save as JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.documentation, f, indent=2, default=str)
        
        print(f"\n✅ Comprehensive documentation saved to: {filename}\n")
        logger.info(f"Saved to {filename}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive multi-schema UBEC database documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Document ALL schemas (auto-discover)
  python ubec_comprehensive_schema_documenter.py
  
  # Document specific schemas
  python ubec_comprehensive_schema_documenter.py --schemas ubec_main phenomenal
  
  # Include system schemas
  python ubec_comprehensive_schema_documenter.py --include-system
  
  # Generate JSON format
  python ubec_comprehensive_schema_documenter.py --format json
  
  # Custom output file
  python ubec_comprehensive_schema_documenter.py --output complete_ubec_docs
        """
    )
    
    # Get default config
    try:
        env_config = get_database_config()
    except Exception as e:
        print(f"\n❌ Configuration Error: {e}\n")
        return 1
    
    # Arguments
    parser.add_argument('--host', default=env_config['host'],
                       help='Database host')
    parser.add_argument('--port', type=int, default=env_config['port'],
                       help='Database port')
    parser.add_argument('--database', default=env_config['database'],
                       help='Database name')
    parser.add_argument('--user', default=env_config['user'],
                       help='Database user')
    parser.add_argument('--password', default=env_config.get('password'),
                       help='Database password')
    parser.add_argument('--schemas', nargs='+',
                       help='Specific schemas to document (default: auto-discover all)')
    parser.add_argument('--include-system', action='store_true',
                       help='Include system schemas (pg_*, information_schema)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                       help='Output format')
    parser.add_argument('--output', help='Output filename (without extension)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
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
    
    print(f"\n🜁 🜄 🜃 🜂 UBEC Comprehensive Multi-Schema Documentation Generator")
    print(f"=" * 70)
    print(f"Database: {conn_params['database']}@{conn_params['host']}:{conn_params['port']}")
    print(f"User: {conn_params['user']}")
    if args.schemas:
        print(f"Schemas: {', '.join(args.schemas)}")
    else:
        print(f"Schemas: Auto-discover all")
    print(f"=" * 70 + "\n")
    
    documenter = UBECComprehensiveDocumenter(
        conn_params, 
        schemas=args.schemas,
        exclude_system_schemas=not args.include_system
    )
    
    try:
        documenter.connect()
        documenter.generate_documentation()
        documenter.save_documentation(args.format, args.output)
        
        # Print summary
        overview = documenter.documentation['database_overview']
        print(f"\n📊 Documentation Summary:")
        print(f"   Schemas: {len(overview['schemas'])}")
        print(f"   Tables: {overview['totals']['tables']}")
        print(f"   Rows: {overview['totals']['rows']:,}")
        print(f"   Columns: {overview['totals']['columns']:,}")
        print(f"   Views: {overview['totals']['views']}")
        print(f"   Functions: {overview['totals']['functions']}")
        print(f"   Relationships: {overview['totals']['relationships']}\n")
        
        # Schema breakdown
        print(f"📋 Schemas Documented:")
        for schema_name, schema_info in overview['schemas'].items():
            print(f"   • {schema_name}: {schema_info['tables']} tables, {schema_info['rows']:,} rows")
        
        print(f"\n✅ Comprehensive documentation complete!\n")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
        
    finally:
        documenter.disconnect()


if __name__ == "__main__":
    sys.exit(main())
