#!/usr/bin/env python3
"""
UBEC Protocol Suite - Database Schema Documentation Generator

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Generates comprehensive documentation of the UBEC four-element protocol database:
- Complete table structures with all columns
- Element-specific tables (Air, Water, Earth, Fire)
- Relationships between tables (foreign keys)
- Indexes for performance optimization
- Constraints ensuring data integrity
- Triggers and their purposes
- Functions and procedures
- Ubuntu principle mappings
- Statistical insights

Version: 3.0 - UBEC Four-Element Protocol Edition
Date: October 9, 2025
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

# UBEC Protocol Constants
ELEMENTS = {
    'air': {'symbol': '🜁', 'token': 'UBEC', 'principle': 'Diversity', 'role': 'Gateway & Universal Access'},
    'water': {'symbol': '🜄', 'token': 'UBECrc', 'principle': 'Reciprocity', 'role': 'Flow & Exchange'},
    'earth': {'symbol': '🜃', 'token': 'UBECgpi', 'principle': 'Mutualism', 'role': 'Stability & Value'},
    'fire': {'symbol': '🜂', 'token': 'UBECtt', 'principle': 'Regeneration', 'role': 'Transformation & Action'}
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
        Path('/home/triag/UBEC/projects/UBEC') / '.env',  # UBEC project path
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
    
    # First check for DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        logger.info(f"Found DATABASE_URL, parsing connection string")
        config = parse_database_url(database_url)
        logger.info(f"Parsed config: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
        return config
    
    # UBEC-specific environment variables with fallbacks
    config = {
        'host': os.environ.get('UBEC_DB_HOST') or os.environ.get('DB_HOST') or 'localhost',
        'port': int(os.environ.get('UBEC_DB_PORT') or os.environ.get('DB_PORT') or 5432),
        'database': os.environ.get('UBEC_DB_NAME') or os.environ.get('DB_NAME') or 'ubec',
        'user': os.environ.get('UBEC_DB_USER') or os.environ.get('DB_USER') or 'ubec_app',
        'password': os.environ.get('UBEC_DB_PASSWORD') or os.environ.get('DB_PASSWORD')
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
    """
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


class UBECSchemaDocumenter:
    """UBEC Protocol Suite database schema documentation generator."""
    
    def __init__(self, connection_params: Dict[str, Any], schema_name: str = 'ubec_main'):
        """
        Initialize UBEC schema documenter.
        
        Args:
            connection_params: Database connection parameters
            schema_name: PostgreSQL schema to document (default: 'ubec_main')
        """
        self.connection_params = connection_params
        self.schema_name = schema_name
        self.conn = None
        self.documentation = {
            'metadata': {},
            'ubec_protocol': {
                'elements': ELEMENTS,
                'element_tables': {},
                'custom_types': {},
                'ubuntu_principles': {}
            },
            'tables': {},
            'relationships': [],
            'indexes': {},
            'triggers': {},
            'functions': {},
            'views': {},
            'summary': {}
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
                logger.error(f"Database '{self.connection_params['database']}' does not exist. Run ubec_database_setup.sql first.")
            else:
                logger.error(f"Connection error: {e}")
            raise
            
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def generate_documentation(self) -> Dict[str, Any]:
        """Generate complete UBEC schema documentation."""
        logger.info(f"Documenting UBEC schema: '{self.schema_name}'")
        
        try:
            self._document_metadata()
            self._document_custom_types()
            self._document_tables()
            self._document_element_tables()
            self._document_views()
            self._document_relationships()
            self._document_indexes()
            self._document_triggers()
            self._document_functions()
            self._generate_summary()
            
            logger.info("UBEC documentation generated successfully")
            
        except Exception as e:
            logger.error(f"Error during documentation: {e}")
            raise
            
        return self.documentation
        
    def _document_metadata(self):
        """Document database metadata with UBEC protocol info."""
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
                'protocol_version': 'Four-Element Protocol v1.0',
                'documentation_version': '3.0',
                'generator': 'UBEC Protocol Schema Documenter'
            }
            
        finally:
            cursor.close()
            
        logger.info("Metadata documented")
    
    def _document_custom_types(self):
        """Document UBEC-specific custom types."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
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
            """, (self.schema_name,))
            
            custom_types = {}
            for row in cursor.fetchall():
                type_name = row['type_name']
                enum_values = row['enum_values']
                
                # Add descriptions for UBEC types
                description = self._get_type_description(type_name)
                
                custom_types[type_name] = {
                    'values': enum_values,
                    'description': description
                }
            
            self.documentation['ubec_protocol']['custom_types'] = custom_types
            logger.info(f"Documented {len(custom_types)} custom types")
            
        finally:
            cursor.close()
    
    def _get_type_description(self, type_name: str) -> str:
        """Get description for UBEC custom types."""
        descriptions = {
            'element_type': 'Four elements: air=UBEC (Gateway), water=UBECrc (Flow), earth=UBECgpi (Stability), fire=UBECtt (Transformation)',
            'token_code': 'Four UBEC protocol tokens',
            'ubuntu_principle': 'Five Ubuntu principles: diversity, reciprocity, mutualism, regeneration, holism',
            'distribution_category': 'Token distribution categories: 75% general, 20% stewardship, 5% administration',
            'health_status': 'System health indicators',
            'transaction_type': 'Stellar transaction operation types'
        }
        return descriptions.get(type_name, 'Custom type')
        
    def _document_tables(self):
        """Document all tables in the UBEC schema."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
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
            """, (self.schema_name,))
            
            tables = cursor.fetchall()
            logger.info(f"Found {len(tables)} tables in schema '{self.schema_name}'")
            
            if len(tables) == 0:
                logger.warning(f"No tables found in schema '{self.schema_name}'")
                return
            
            for row in tables:
                table_name = row['table_name']
                table_comment = row['table_comment']
                logger.info(f"Documenting table: {table_name}")
                
                # Get columns with descriptions
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
                """, (self.schema_name, table_name, self.schema_name, table_name))
                
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
                        'name': con['constraint_name'],
                        'type': constraint_type_map.get(con['constraint_type'], con['constraint_type']),
                        'definition': con['definition']
                    })
                
                # Get table statistics
                try:
                    qualified_table = f'"{self.schema_name}"."{table_name}"'
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
                    logger.warning(f"Could not get stats for {table_name}: {e}")
                    stats = {'row_count': 0, 'total_size': 'Unknown', 'table_size': 'Unknown', 'index_size': 'Unknown'}
                
                self.documentation['tables'][table_name] = {
                    'comment': table_comment,
                    'columns': columns,
                    'constraints': constraints,
                    'statistics': {
                        'row_count': stats['row_count'],
                        'total_size': stats['total_size'],
                        'table_size': stats['table_size'],
                        'index_size': stats['index_size']
                    }
                }
                
        finally:
            cursor.close()
            
        logger.info(f"Documented {len(self.documentation['tables'])} tables")
    
    def _document_element_tables(self):
        """Document element-specific tables and their relationships."""
        element_tables = {
            'air': [],
            'water': [],
            'earth': [],
            'fire': [],
            'core': []
        }
        
        # Classify tables by element
        for table_name in self.documentation['tables'].keys():
            if 'air' in table_name.lower() or table_name.lower().startswith('ubec_') and 'rc' not in table_name.lower():
                element_tables['air'].append(table_name)
            elif 'water' in table_name.lower() or 'rc' in table_name.lower() or 'flow' in table_name.lower():
                element_tables['water'].append(table_name)
            elif 'earth' in table_name.lower() or 'gpi' in table_name.lower() or 'stability' in table_name.lower() or 'distribution' in table_name.lower():
                element_tables['earth'].append(table_name)
            elif 'fire' in table_name.lower() or 'tt' in table_name.lower() or 'transformation' in table_name.lower() or 'audit' in table_name.lower():
                element_tables['fire'].append(table_name)
            elif 'stellar' in table_name.lower() or 'holonic' in table_name.lower() or 'balance' in table_name.lower():
                element_tables['core'].append(table_name)
        
        self.documentation['ubec_protocol']['element_tables'] = element_tables
        logger.info("Documented element-specific tables")
    
    def _document_views(self):
        """Document database views."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute("""
                SELECT 
                    table_name,
                    view_definition
                FROM information_schema.views
                WHERE table_schema = %s
                ORDER BY table_name
            """, (self.schema_name,))
            
            views = {}
            for row in cursor.fetchall():
                views[row['table_name']] = {
                    'definition': row['view_definition']
                }
            
            self.documentation['views'] = views
            logger.info(f"Documented {len(views)} views")
            
        finally:
            cursor.close()
        
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
                    'relationship_type': 'many-to-one'
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
                """, (self.schema_name,))
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
                """, (self.schema_name,))
            
            functions = []
            for row in cursor.fetchall():
                functions.append({
                    'name': row[0],
                    'return_type': row[1],
                    'arguments': row[2],
                    'language': row[3],
                    'description': row[4]
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
            'total_views': len(self.documentation['views']),
            'total_custom_types': len(self.documentation['ubec_protocol']['custom_types']),
            'tables_by_size': [],
            'tables_by_element': {}
        }
        
        # Sort tables by row count
        for table_name, table_info in self.documentation['tables'].items():
            stats = table_info.get('statistics', {})
            row_count = stats.get('row_count', 0)
            total_size = stats.get('total_size', 'Unknown')
            
            summary['tables_by_size'].append({
                'table': table_name,
                'rows': row_count if row_count is not None else 0,
                'size': total_size if total_size is not None else 'Unknown'
            })
        
        summary['tables_by_size'].sort(key=lambda x: x['rows'], reverse=True)
        
        # Count tables by element
        element_tables = self.documentation['ubec_protocol']['element_tables']
        for element, tables in element_tables.items():
            summary['tables_by_element'][element] = len(tables)
        
        self.documentation['summary'] = summary
        logger.info("Summary generated")
        
    def save_documentation(self, output_format: str = 'markdown', output_file: str = None):
        """Save documentation to file."""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"ubec_schema_doc_{self.schema_name}_{timestamp}"
            
        if output_format == 'markdown':
            self._save_as_markdown(f"{output_file}.md")
        elif output_format == 'json':
            self._save_as_json(f"{output_file}.json")
        else:
            raise ValueError(f"Unsupported format: {output_format}")
            
    def _save_as_markdown(self, filename: str):
        """Save as Markdown file with UBEC protocol formatting."""
        with open(filename, 'w', encoding='utf-8') as f:
            meta = self.documentation['metadata']
            summary = self.documentation['summary']
            protocol = self.documentation['ubec_protocol']
            
            # Header with UBEC branding
            f.write(f"# UBEC Protocol Suite - Database Schema Documentation\n\n")
            f.write(f"## 🜁 🜄 🜃 🜂 Four-Element Protocol\n\n")
            f.write(f"**Schema:** `{meta['schema_name']}`  \n")
            f.write(f"**Database:** `{meta['database_name']}`  \n")
            f.write(f"**Generated:** {meta['generated_at']}  \n")
            f.write(f"**PostgreSQL Version:** {meta['database_version']}  \n")
            f.write(f"**Protocol Version:** {meta['protocol_version']}  \n\n")
            
            if not meta['schema_exists']:
                f.write("⚠️ **WARNING: Schema does not exist!**\n\n")
                f.write("Please run `ubec_database_setup.sql` to create the schema.\n\n")
                return
            
            # Four Elements Overview
            f.write("## The Four Elements\n\n")
            for element, info in ELEMENTS.items():
                f.write(f"### {info['symbol']} {element.title()} - {info['token']}\n\n")
                f.write(f"- **Ubuntu Principle:** {info['principle']}\n")
                f.write(f"- **Role:** {info['role']}\n")
                tables = protocol['element_tables'].get(element, [])
                if tables:
                    f.write(f"- **Tables:** {', '.join(f'`{t}`' for t in tables)}\n")
                f.write("\n")
            
            # Core Infrastructure
            core_tables = protocol['element_tables'].get('core', [])
            if core_tables:
                f.write(f"### Core Infrastructure Tables\n\n")
                f.write(f"Shared tables used across all elements:\n\n")
                for table in core_tables:
                    f.write(f"- `{table}`\n")
                f.write("\n")
            
            # Custom Types
            if protocol['custom_types']:
                f.write("## Custom Types\n\n")
                for type_name, type_info in protocol['custom_types'].items():
                    f.write(f"### {type_name}\n\n")
                    f.write(f"{type_info['description']}\n\n")
                    f.write(f"**Values:** {', '.join(f'`{v}`' for v in type_info['values'])}\n\n")
            
            # Summary
            f.write("## Database Summary\n\n")
            f.write(f"- **Total Tables:** {summary['total_tables']}\n")
            f.write(f"- **Total Columns:** {summary['total_columns']}\n")
            f.write(f"- **Total Relationships:** {summary['total_relationships']}\n")
            f.write(f"- **Total Indexes:** {summary['total_indexes']}\n")
            f.write(f"- **Total Views:** {summary['total_views']}\n")
            f.write(f"- **Total Functions:** {summary['total_functions']}\n")
            f.write(f"- **Total Custom Types:** {summary['total_custom_types']}\n")
            f.write(f"- **Database Size:** {meta['database_size']['human_readable']}\n\n")
            
            # Tables by Element
            f.write("### Tables by Element\n\n")
            for element, count in summary['tables_by_element'].items():
                symbol = ELEMENTS.get(element, {}).get('symbol', '📊')
                f.write(f"- {symbol} **{element.title()}:** {count} tables\n")
            f.write("\n")
            
            if summary['total_tables'] == 0:
                f.write("**No tables found in this schema.**\n\n")
                return
            
            # Tables by Size
            f.write("### Largest Tables\n\n")
            f.write("| Table | Rows | Size |\n")
            f.write("|-------|------|------|\n")
            for table_info in summary['tables_by_size'][:10]:
                rows = table_info.get('rows', 0)
                size = table_info.get('size', 'Unknown')
                f.write(f"| {table_info['table']} | {rows:,} | {size} |\n")
            f.write("\n---\n\n")
            
            # Detailed Tables
            f.write("## Detailed Table Documentation\n\n")
            
            # Group tables by element
            for element in ['core', 'air', 'water', 'earth', 'fire']:
                tables = protocol['element_tables'].get(element, [])
                if not tables:
                    continue
                
                if element == 'core':
                    f.write(f"### Core Infrastructure Tables\n\n")
                else:
                    info = ELEMENTS[element]
                    f.write(f"### {info['symbol']} {element.title()} Element ({info['token']})\n\n")
                
                for table_name in sorted(tables):
                    if table_name not in self.documentation['tables']:
                        continue
                    
                    table = self.documentation['tables'][table_name]
                    f.write(f"#### {table_name}\n\n")
                    
                    if table.get('comment'):
                        f.write(f"*{table['comment']}*\n\n")
                    
                    stats = table.get('statistics', {})
                    row_count = stats.get('row_count', 0)
                    table_size = stats.get('table_size', 'Unknown')
                    index_size = stats.get('index_size', 'Unknown')
                    total_size = stats.get('total_size', 'Unknown')
                    
                    f.write(f"**Statistics:** {row_count:,} rows | ")
                    f.write(f"Table: {table_size} | ")
                    f.write(f"Indexes: {index_size} | ")
                    f.write(f"Total: {total_size}\n\n")
                    
                    # Columns
                    f.write("| Column | Type | Nullable | Default | Description |\n")
                    f.write("|--------|------|----------|---------|-------------|\n")
                    
                    for col in table['columns']:
                        nullable = "✓" if col['nullable'] else "✗"
                        default = col['default'] or "-"
                        if len(str(default)) > 40:
                            default = str(default)[:37] + "..."
                        comment = col['comment'] or "-"
                        if len(str(comment)) > 50:
                            comment = str(comment)[:47] + "..."
                        
                        col_type = col['data_type']
                        if col['is_generated']:
                            col_type += " (generated)"
                        if col['is_identity']:
                            col_type += " (identity)"
                            
                        f.write(f"| {col['name']} | {col_type} | {nullable} | {default} | {comment} |\n")
                    
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
                    
                    f.write("\n")
                
                f.write("---\n\n")
            
            # Views
            if self.documentation['views']:
                f.write("## Views\n\n")
                for view_name in sorted(self.documentation['views'].keys()):
                    f.write(f"### {view_name}\n\n")
                    f.write("```sql\n")
                    f.write(self.documentation['views'][view_name]['definition'][:500])
                    if len(self.documentation['views'][view_name]['definition']) > 500:
                        f.write("...\n")
                    f.write("\n```\n\n")
            
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
            
            # Functions
            if self.documentation['functions']:
                f.write("## Functions\n\n")
                for func in self.documentation['functions']:
                    f.write(f"### {func['name']}({func['arguments']})\n\n")
                    f.write(f"- **Returns:** {func['return_type']}\n")
                    f.write(f"- **Language:** {func['language']}\n")
                    if func.get('description'):
                        f.write(f"- **Description:** {func['description']}\n")
                    f.write("\n")
        
        print(f"\n✅ UBEC Protocol documentation saved to: {filename}\n")
        logger.info(f"Saved to {filename}")
        
    def _save_as_json(self, filename: str):
        """Save as JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.documentation, f, indent=2, default=str)
        
        print(f"\n✅ UBEC Protocol documentation saved to: {filename}\n")
        logger.info(f"Saved to {filename}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate UBEC Protocol Suite database schema documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Document default UBEC schema
  python ubec_schema_documenter.py
  
  # Document with custom output
  python ubec_schema_documenter.py --output ubec_docs
  
  # Generate JSON format
  python ubec_schema_documenter.py --format json
  
  # Document different schema
  python ubec_schema_documenter.py --schema public
  
  # Use custom database
  python ubec_schema_documenter.py --database ubec_test --user postgres
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
                       help='Database host (default: from .env or localhost)')
    parser.add_argument('--port', type=int, default=env_config['port'],
                       help='Database port (default: from .env or 5432)')
    parser.add_argument('--database', default=env_config['database'],
                       help='Database name (default: from .env or ubec)')
    parser.add_argument('--user', default=env_config['user'],
                       help='Database user (default: from .env or ubec_app)')
    parser.add_argument('--password', default=env_config.get('password'),
                       help='Database password (default: from .env)')
    parser.add_argument('--schema', default='ubec_main',
                       help='Schema name to document (default: ubec_main)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                       help='Output format (default: markdown)')
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
    
    print(f"\n🜁 🜄 🜃 🜂 UBEC Protocol Schema Documentation Generator")
    print(f"=" * 70)
    print(f"Database: {conn_params['database']}@{conn_params['host']}:{conn_params['port']}")
    print(f"Schema: {args.schema}")
    print(f"User: {conn_params['user']}")
    print(f"=" * 70 + "\n")
    
    documenter = UBECSchemaDocumenter(conn_params, args.schema)
    
    try:
        documenter.connect()
        documenter.generate_documentation()
        documenter.save_documentation(args.format, args.output)
        
        # Print summary
        summary = documenter.documentation['summary']
        print(f"📊 Documentation Summary:")
        print(f"   Tables: {summary['total_tables']}")
        print(f"   Columns: {summary['total_columns']}")
        print(f"   Relationships: {summary['total_relationships']}")
        print(f"   Indexes: {summary['total_indexes']}")
        print(f"   Views: {summary['total_views']}")
        print(f"   Functions: {summary['total_functions']}")
        print(f"   Custom Types: {summary['total_custom_types']}\n")
        
        # Element breakdown
        print(f"📋 Tables by Element:")
        for element, count in summary['tables_by_element'].items():
            symbol = ELEMENTS.get(element, {}).get('symbol', '📊')
            print(f"   {symbol} {element.title()}: {count}")
        
        print(f"\n✅ Documentation complete!\n")
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
