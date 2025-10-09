#!/usr/bin/env python3
"""
Database Schema Documentation Generator for UBEC Holon ETF System

This script creates a comprehensive documentation of your database schema,
serving as the single source of truth for your database structure.
Think of it as creating a detailed blueprint of your data architecture.

The documentation includes:
- Complete table structures with all columns and their properties
- Relationships between tables (foreign keys)
- Indexes for performance optimization
- Constraints that ensure data integrity
- Triggers and their purposes
- Visual relationship diagrams
- Best practices and usage notes

Author: Schema Documentation System
Version: 1.0
"""

import psycopg2
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import argparse
from pathlib import Path

# Try to import python-dotenv for loading .env files
try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv not installed. Trying to continue with environment variables.")
    print("To install: pip install python-dotenv")
    load_dotenv = None

# Set up logging to help track the documentation process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_and_load_env_file():
    """
    Search for and load the .env file from various possible locations.
    
    This function helps locate your project's .env file by checking common locations
    where it might be stored. It searches from the current directory upward through
    parent directories, looking for the .env file.
    """
    if load_dotenv is None:
        logger.warning("python-dotenv not available, skipping .env file loading")
        return False
        
    # List of possible locations to check for .env file
    current_path = Path.cwd()
    paths_to_check = [
        current_path / '.env',  # Current directory
        current_path.parent / '.env',  # Parent directory
        current_path.parent.parent / '.env',  # Grandparent directory
    ]
    
    # Also check for common project structure patterns
    # Looking for UBEC_Holon_ETF project root
    for parent in current_path.parents:
        if parent.name == 'UBEC_Holon_ETF':
            paths_to_check.insert(0, parent / '.env')
            break
    
    # Try to load .env from each possible location
    for env_path in paths_to_check:
        if env_path.exists():
            logger.info(f"Found .env file at: {env_path}")
            load_dotenv(env_path)
            return True
    
    # If no .env file found, log available paths for debugging
    logger.warning("No .env file found in common locations")
    logger.info(f"Searched in: {[str(p) for p in paths_to_check]}")
    return False


def get_database_config():
    """
    Get database configuration from environment variables with multiple fallbacks.
    
    This function understands that different projects might use different environment
    variable names for the same purpose. It checks multiple common patterns and
    provides helpful debugging information if connection details are missing.
    """
    # First, try to load the .env file
    env_loaded = find_and_load_env_file()
    
    # Define multiple possible environment variable names for each parameter
    # This handles variations like DB_HOST vs POSTGRES_HOST vs DATABASE_HOST
    config_mappings = {
        'host': ['DB_HOST', 'POSTGRES_HOST', 'DATABASE_HOST', 'PGHOST'],
        'port': ['DB_PORT', 'POSTGRES_PORT', 'DATABASE_PORT', 'PGPORT'],
        'database': ['DB_NAME', 'POSTGRES_DB', 'DATABASE_NAME', 'PGDATABASE'],
        'user': ['DB_USER', 'POSTGRES_USER', 'DATABASE_USER', 'PGUSER'],
        'password': ['DB_PASSWORD', 'POSTGRES_PASSWORD', 'DATABASE_PASSWORD', 'PGPASSWORD']
    }
    
    config = {}
    missing_configs = []
    
    # Try each possible environment variable name
    for param, possible_vars in config_mappings.items():
        value = None
        used_var = None
        
        for var_name in possible_vars:
            value = os.environ.get(var_name)
            if value:
                used_var = var_name
                break
        
        if value:
            config[param] = value
            logger.debug(f"Found {param} from {used_var}: {'***' if param == 'password' else value}")
        else:
            missing_configs.append(param)
    
    # Provide defaults for non-critical parameters
    defaults = {
        'host': 'localhost',
        'port': 5432,
        'database': 'ubec_holon_etf',
        'user': 'postgres'
    }
    
    for param, default_value in defaults.items():
        if param not in config:
            config[param] = default_value
            logger.warning(f"No {param} found in environment, using default: {default_value}")
    
    # Password is critical - we can't provide a default
    if 'password' not in config:
        logger.error("No database password found in environment variables!")
        logger.info("Please ensure your .env file contains one of: DB_PASSWORD, POSTGRES_PASSWORD, DATABASE_PASSWORD, or PGPASSWORD")
        if not env_loaded:
            logger.info("No .env file was found. Please create one in your project root.")
        
        # Try to help the user by showing what environment variables are available
        db_related_vars = [var for var in os.environ.keys() if 'DB' in var or 'POSTGRES' in var or 'DATABASE' in var]
        if db_related_vars:
            logger.info(f"Found these database-related environment variables: {', '.join(db_related_vars)}")
        
        raise ValueError("Database password not configured. Please check your .env file.")
    
    # Convert port to integer
    config['port'] = int(config['port'])
    
    return config


class SchemaDocumenter:
    """
    A comprehensive schema documentation generator that examines your database
    structure and creates detailed documentation.
    
    Think of this class as a detective that investigates every corner of your
    database to understand how all the pieces fit together.
    """
    
    def __init__(self, connection_params: Dict[str, Any], schema_name: str = 'ubec_holon_etf'):
        """
        Initialize the documenter with database connection parameters.
        
        Parameters:
        -----------
        connection_params : dict
            Database connection parameters (host, port, database, user, password)
        schema_name : str
            The schema to document (default: 'ubec_holon_etf')
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
        """Establish connection to the database."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            # Set autocommit to True to avoid transaction issues
            self.conn.autocommit = True
            logger.info("Successfully connected to database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
            
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def generate_documentation(self) -> Dict[str, Any]:
        """
        Generate complete schema documentation.
        
        This is the main orchestrator method that calls all the specific
        documentation methods in the right order.
        """
        logger.info(f"Starting schema documentation for '{self.schema_name}'")
        
        # Track progress for better debugging
        steps_completed = []
        
        try:
            # First, gather metadata about the documentation process itself
            logger.info("Step 1: Documenting metadata...")
            self._document_metadata()
            steps_completed.append('metadata')
            
            # Document all tables and their structures
            logger.info("Step 2: Documenting tables...")
            self._document_tables()
            steps_completed.append('tables')
            
            # Document relationships between tables (foreign keys)
            logger.info("Step 3: Documenting relationships...")
            self._document_relationships()
            steps_completed.append('relationships')
            
            # Document indexes for understanding performance optimization
            logger.info("Step 4: Documenting indexes...")
            self._document_indexes()
            steps_completed.append('indexes')
            
            # Document triggers that automate certain behaviors
            logger.info("Step 5: Documenting triggers...")
            self._document_triggers()
            steps_completed.append('triggers')
            
            # Document any custom functions or procedures
            logger.info("Step 6: Documenting functions...")
            self._document_functions()
            steps_completed.append('functions')
            
            # Generate a summary with insights and statistics
            logger.info("Step 7: Generating summary...")
            self._generate_summary()
            steps_completed.append('summary')
            
            logger.info("Schema documentation completed successfully")
            logger.info(f"Steps completed: {', '.join(steps_completed)}")
            
        except Exception as e:
            logger.error(f"Error during documentation generation: {e}")
            logger.error(f"Steps completed before error: {', '.join(steps_completed)}")
            # Re-raise the exception with more context
            raise Exception(f"Documentation failed after completing: {', '.join(steps_completed)}. Error: {str(e)}")
            
        return self.documentation
        
    def _document_metadata(self):
        """
        Document metadata about the database and documentation process.
        
        This helps track when documentation was generated and what version
        of the database it represents.
        """
        cursor = self.conn.cursor()
        
        # Get PostgreSQL version
        cursor.execute("SELECT version()")
        pg_version = cursor.fetchone()[0]
        
        # Get database size
        cursor.execute("""
            SELECT pg_database_size(current_database()) as size_bytes,
                   pg_size_pretty(pg_database_size(current_database())) as size_pretty
        """)
        db_size = cursor.fetchone()
        
        # Note: PostgreSQL doesn't store table creation dates in a standard way
        # We'll skip this rather than fail the entire documentation process
        
        self.documentation['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'schema_name': self.schema_name,
            'database_version': pg_version,
            'database_size': {
                'bytes': db_size[0],
                'human_readable': db_size[1]
            },
            'documentation_version': '1.0',
            'generator': 'UBEC Holon ETF Schema Documenter'
        }
        
        cursor.close()
        logger.info("Metadata documentation completed")
        
    def _document_tables(self):
        """
        Document all tables in the schema with complete details.
        
        This is like creating a detailed inventory of every table,
        including all its columns and their properties.
        """
        cursor = self.conn.cursor()
        
        # First, get all tables in the schema
        cursor.execute(f"""
            SELECT 
                t.table_name,
                obj_description(c.oid) as table_comment
            FROM information_schema.tables t
            JOIN pg_class c ON c.relname = t.table_name
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE t.table_schema = %s 
            AND t.table_type = 'BASE TABLE'
            AND n.nspname = %s
            ORDER BY t.table_name
        """, (self.schema_name, self.schema_name))
        
        tables = cursor.fetchall()
        logger.info(f"Found {len(tables)} tables to document")
        
        for table_name, table_comment in tables:
            logger.info(f"Documenting table: {table_name}")
            
            # Get detailed column information for each table
            cursor.execute(f"""
                SELECT 
                    c.column_name,
                    c.data_type,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale,
                    c.is_nullable,
                    c.column_default,
                    c.is_identity,
                    c.is_generated,
                    c.generation_expression,
                    pgd.description as column_comment
                FROM information_schema.columns c
                LEFT JOIN pg_catalog.pg_description pgd ON 
                    pgd.objoid = (
                        SELECT oid FROM pg_class 
                        WHERE relname = c.table_name 
                        AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = c.table_schema)
                    )
                    AND pgd.objsubid = c.ordinal_position
                WHERE c.table_schema = %s 
                AND c.table_name = %s
                ORDER BY c.ordinal_position
            """, (self.schema_name, table_name))
            
            columns = []
            for col in cursor.fetchall():
                # Build a comprehensive column definition
                column_info = {
                    'name': col[0],
                    'data_type': self._format_data_type(col[1], col[2], col[3], col[4]),
                    'nullable': col[5] == 'YES',
                    'default': col[6],
                    'is_identity': col[7] == 'YES',
                    'is_generated': col[8] == 'ALWAYS',
                    'generation_expression': col[9],
                    'comment': col[10]
                }
                columns.append(column_info)
            
            # Get table constraints (primary keys, unique constraints, check constraints)
            cursor.execute(f"""
                SELECT 
                    con.conname as constraint_name,
                    con.contype as constraint_type,
                    pg_get_constraintdef(con.oid) as definition
                FROM pg_constraint con
                JOIN pg_namespace nsp ON nsp.oid = con.connamespace
                WHERE nsp.nspname = %s
                AND con.conrelid = (
                    SELECT oid FROM pg_class 
                    WHERE relname = %s 
                    AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
                )
                ORDER BY con.conname
            """, (self.schema_name, table_name, self.schema_name))
            
            constraints = []
            for con in cursor.fetchall():
                constraint_type_map = {
                    'p': 'PRIMARY KEY',
                    'u': 'UNIQUE',
                    'c': 'CHECK',
                    'f': 'FOREIGN KEY',
                    'x': 'EXCLUSION'
                }
                constraints.append({
                    'name': con[0],
                    'type': constraint_type_map.get(con[1], con[1]),
                    'definition': con[2]
                })
            
            # Get row count and table size for context
            try:
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as row_count,
                        pg_size_pretty(pg_total_relation_size(quote_ident(%s) || '.' || quote_ident(%s))) as total_size
                    FROM {self.schema_name}.{table_name}
                """, (self.schema_name, table_name))
                
                stats = cursor.fetchone()
            except Exception as e:
                logger.warning(f"Could not get stats for table {table_name}: {e}")
                stats = (0, 'Unknown')
                
                stats = cursor.fetchone()
            except Exception as e:
                logger.warning(f"Could not get stats for table {table_name}: {e}")
                stats = (0, 'Unknown')
            
            # Store all table information
            self.documentation['tables'][table_name] = {
                'comment': table_comment,
                'columns': columns,
                'constraints': constraints,
                'statistics': {
                    'row_count': stats[0],
                    'total_size': stats[1]
                }
            }
        
        cursor.close()
        logger.info("Table documentation completed")
        
    def _format_data_type(self, data_type: str, char_length: Optional[int], 
                         numeric_precision: Optional[int], numeric_scale: Optional[int]) -> str:
        """
        Format data type information into a readable string.
        
        This method translates database-specific type information into
        a human-readable format that's consistent and clear.
        """
        if data_type == 'character varying' and char_length:
            return f"varchar({char_length})"
        elif data_type == 'numeric' and numeric_precision:
            if numeric_scale:
                return f"numeric({numeric_precision},{numeric_scale})"
            else:
                return f"numeric({numeric_precision})"
        else:
            return data_type
            
    def _document_relationships(self):
        """
        Document all foreign key relationships between tables.
        
        Understanding relationships is crucial for grasping how data flows
        through your system. This method maps out all the connections.
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(f"""
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
                    AND ccu.table_schema = tc.table_schema
                JOIN information_schema.referential_constraints rc
                    ON rc.constraint_name = tc.constraint_name
                    AND rc.constraint_schema = tc.table_schema
                WHERE tc.table_schema = %s
                AND tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_name, tc.constraint_name
            """, (self.schema_name,))
            
            relationships = []
            results = cursor.fetchall()
            
            logger.debug(f"Found {len(results)} relationship rows to process")
            
            for i, row in enumerate(results):
                # Debug logging for troubleshooting
                logger.debug(f"Processing relationship row {i}: length={len(row)}")
                
                # Safely unpack with validation
                if len(row) < 7:
                    logger.error(f"Relationship row has insufficient columns: {row}")
                    continue
                
                try:
                    from_table = row[0]
                    from_column = row[1]
                    to_table = row[2]
                    to_column = row[3]
                    constraint_name = row[4]
                    update_rule = row[5]
                    delete_rule = row[6]
                    
                    relationship = {
                        'from_table': from_table,
                        'from_column': from_column,
                        'to_table': to_table,
                        'to_column': to_column,
                        'constraint_name': constraint_name,
                        'update_rule': update_rule,
                        'delete_rule': delete_rule,
                        'relationship_type': self._infer_relationship_type(from_table, from_column, to_table)
                    }
                    relationships.append(relationship)
                    
                except IndexError as e:
                    logger.error(f"Error unpacking relationship row {i}: {e}")
                    logger.error(f"Row data: {row}")
                    continue
                    
            self.documentation['relationships'] = relationships
            logger.info(f"Documented {len(relationships)} relationships")
            
        except Exception as e:
            logger.error(f"Error in relationship documentation: {e}")
            self.documentation['relationships'] = []
            raise
            
        finally:
            cursor.close()
        
    def _infer_relationship_type(self, from_table: str, from_column: str, to_table: str) -> str:
        """
        Infer the type of relationship based on table and column names.
        
        This helps understand whether relationships are one-to-many,
        many-to-many, or one-to-one.
        """
        # Simple heuristics for relationship types
        if from_column.endswith('_id'):
            if from_table.endswith('s') and to_table.endswith('s'):
                # Both tables are plural, might be many-to-many
                return "many-to-one (possible many-to-many via junction)"
            else:
                return "many-to-one"
        else:
            return "one-to-one"
            
    def _document_indexes(self):
        """
        Document all indexes in the schema.
        
        Indexes are crucial for query performance. Understanding which columns
        are indexed helps explain why certain queries are fast or slow.
        """
        cursor = self.conn.cursor()
        
        try:
            # First, let's check what columns are available in pg_indexes
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pg_indexes'
                LIMIT 10
            """)
            available_columns = [row[0] for row in cursor.fetchall()]
            logger.debug(f"Available pg_indexes columns: {available_columns}")
            
            # Use a simpler query that's more compatible across PostgreSQL versions
            cursor.execute(f"""
                SELECT 
                    indexname,
                    tablename,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = %s
                ORDER BY tablename, indexname
            """, (self.schema_name,))
            
            indexes_by_table = {}
            all_results = cursor.fetchall()
            
            logger.debug(f"Retrieved {len(all_results)} index records")
            
            for row in all_results:
                # More defensive unpacking
                if len(row) < 3:
                    logger.warning(f"Skipping malformed index row: {row}")
                    continue
                
                index_name = row[0]
                table_name = row[1]
                index_def = row[2]
                
                # Derive index properties from the definition
                is_unique = 'UNIQUE' in index_def.upper()
                is_primary = index_name.endswith('_pkey')
                
                if table_name not in indexes_by_table:
                    indexes_by_table[table_name] = []
                
                indexes_by_table[table_name].append({
                    'name': index_name,
                    'definition': index_def,
                    'is_unique': is_unique,
                    'is_primary': is_primary,
                    'columns': self._extract_index_columns(index_def)
                })
            
            self.documentation['indexes'] = indexes_by_table
            
            total_indexes = sum(len(idxs) for idxs in indexes_by_table.values())
            logger.info(f"Documented {total_indexes} indexes across {len(indexes_by_table)} tables")
            
        except Exception as e:
            logger.error(f"Error in index documentation: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            # Don't let index documentation failure kill the entire process
            self.documentation['indexes'] = {}
            logger.warning("Continuing without index documentation")
            
        finally:
            cursor.close()
        
    def _extract_index_columns(self, index_def: str) -> List[str]:
        """
        Extract column names from an index definition.
        
        This parsing helps understand which columns are covered by each index.
        """
        if not index_def:
            return []
            
        # Simple extraction - might need enhancement for complex cases
        import re
        
        try:
            # Look for column names between parentheses
            match = re.search(r'\((.*?)\)', index_def)
            if match:
                columns_str = match.group(1)
                # Split by comma and clean up
                columns = []
                for col in columns_str.split(','):
                    # Extract just the column name, removing any additional syntax
                    col_clean = col.strip().split()[0]
                    # Remove any quotes
                    col_clean = col_clean.strip('"').strip("'")
                    if col_clean:
                        columns.append(col_clean)
                return columns
        except Exception as e:
            logger.warning(f"Error extracting columns from index definition: {e}")
            
        return []
        
    def _document_triggers(self):
        """
        Document all triggers in the schema.
        
        Triggers are automated responses to data changes. Understanding them
        is crucial for knowing what side effects data modifications might have.
        """
        # Use a new connection to avoid transaction issues
        cursor = self.conn.cursor()
        
        try:
            # Note: tgtype is not available in information_schema.triggers
            # We'll use a simpler query that works across PostgreSQL versions
            cursor.execute(f"""
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
            results = cursor.fetchall()
            
            for row in results:
                # Safely handle the row data
                if len(row) < 6:
                    logger.warning(f"Unexpected trigger row format: {row}")
                    continue
                    
                trigger_name = row[0]
                table_name = row[1]
                event = row[2]
                timing = row[3]
                orientation = row[4]
                function = row[5]
                
                if table_name not in triggers_by_table:
                    triggers_by_table[table_name] = []
                    
                triggers_by_table[table_name].append({
                    'name': trigger_name,
                    'event': event,  # INSERT, UPDATE, DELETE
                    'timing': timing,  # BEFORE, AFTER
                    'orientation': orientation,  # ROW, STATEMENT
                    'function': function
                })
                
            self.documentation['triggers'] = triggers_by_table
            
            total_triggers = sum(len(trgs) for trgs in triggers_by_table.values())
            logger.info(f"Documented {total_triggers} triggers across {len(triggers_by_table)} tables")
            
        except Exception as e:
            logger.error(f"Error documenting triggers: {e}")
            self.documentation['triggers'] = {}
            # Rollback the transaction to allow subsequent operations
            self.conn.rollback()
            logger.warning("Continuing without trigger documentation")
            
        finally:
            cursor.close()
        
    def _document_functions(self):
        """
        Document custom functions and procedures in the schema.
        
        Functions contain business logic that operates on your data.
        Understanding them helps grasp the computational aspects of your system.
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(f"""
                SELECT 
                    p.proname as function_name,
                    pg_get_function_result(p.oid) as return_type,
                    pg_get_function_arguments(p.oid) as arguments,
                    p.prosrc as source_code,
                    obj_description(p.oid) as comment,
                    l.lanname as language
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                JOIN pg_language l ON l.oid = p.prolang
                WHERE n.nspname = %s
                AND p.prokind IN ('f', 'p')  -- functions and procedures
                ORDER BY p.proname
            """, (self.schema_name,))
            
            functions = []
            for func in cursor.fetchall():
                functions.append({
                    'name': func[0],
                    'return_type': func[1],
                    'arguments': func[2],
                    'source_code': func[3],
                    'comment': func[4],
                    'language': func[5]
                })
                
            self.documentation['functions'] = functions
            logger.info(f"Documented {len(functions)} functions/procedures")
            
        except Exception as e:
            logger.error(f"Error documenting functions: {e}")
            # Check if it's due to prokind not existing (older PostgreSQL versions)
            if "column" in str(e) and "prokind" in str(e):
                logger.info("Retrying with compatibility query for older PostgreSQL version")
                try:
                    # Rollback the failed transaction
                    self.conn.rollback()
                    cursor = self.conn.cursor()
                    
                    # Use proisagg instead of prokind for older versions
                    cursor.execute(f"""
                        SELECT 
                            p.proname as function_name,
                            pg_get_function_result(p.oid) as return_type,
                            pg_get_function_arguments(p.oid) as arguments,
                            p.prosrc as source_code,
                            obj_description(p.oid) as comment,
                            l.lanname as language
                        FROM pg_proc p
                        JOIN pg_namespace n ON n.oid = p.pronamespace
                        JOIN pg_language l ON l.oid = p.prolang
                        WHERE n.nspname = %s
                        AND NOT p.proisagg  -- not an aggregate function
                        ORDER BY p.proname
                    """, (self.schema_name,))
                    
                    functions = []
                    for func in cursor.fetchall():
                        functions.append({
                            'name': func[0],
                            'return_type': func[1],
                            'arguments': func[2],
                            'source_code': func[3],
                            'comment': func[4],
                            'language': func[5]
                        })
                        
                    self.documentation['functions'] = functions
                    logger.info(f"Documented {len(functions)} functions/procedures (compatibility mode)")
                    
                except Exception as e2:
                    logger.error(f"Error in compatibility mode: {e2}")
                    self.documentation['functions'] = []
                    self.conn.rollback()
                    
            else:
                self.documentation['functions'] = []
                # Rollback to allow subsequent operations
                try:
                    self.conn.rollback()
                except:
                    pass
                    
        finally:
            cursor.close()
        
    def _generate_summary(self):
        """
        Generate insightful summary statistics about the schema.
        
        This provides a bird's-eye view of your database structure,
        helping identify patterns and potential areas for optimization.
        """
        summary = {
            'total_tables': len(self.documentation['tables']),
            'total_columns': sum(len(t['columns']) for t in self.documentation['tables'].values()),
            'total_relationships': len(self.documentation['relationships']),
            'total_indexes': sum(len(idxs) for idxs in self.documentation['indexes'].values()),
            'total_triggers': sum(len(trgs) for trgs in self.documentation['triggers'].values()),
            'total_functions': len(self.documentation['functions']),
            'tables_by_size': [],
            'tables_by_rows': [],
            'most_referenced_tables': {},
            'orphan_tables': []
        }
        
        # Analyze table sizes and row counts
        for table_name, table_info in self.documentation['tables'].items():
            stats = table_info['statistics']
            summary['tables_by_size'].append({
                'table': table_name,
                'size': stats['total_size'],
                'rows': stats['row_count']
            })
            summary['tables_by_rows'].append({
                'table': table_name,
                'rows': stats['row_count']
            })
            
        # Sort by size and rows
        summary['tables_by_size'].sort(key=lambda x: x['rows'], reverse=True)
        summary['tables_by_rows'].sort(key=lambda x: x['rows'], reverse=True)
        
        # Find most referenced tables (tables that others depend on)
        reference_count = {}
        for rel in self.documentation['relationships']:
            to_table = rel['to_table']
            reference_count[to_table] = reference_count.get(to_table, 0) + 1
            
        summary['most_referenced_tables'] = dict(sorted(
            reference_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        # Find orphan tables (tables with no relationships)
        all_tables = set(self.documentation['tables'].keys())
        tables_with_relationships = set()
        for rel in self.documentation['relationships']:
            tables_with_relationships.add(rel['from_table'])
            tables_with_relationships.add(rel['to_table'])
            
        summary['orphan_tables'] = list(all_tables - tables_with_relationships)
        
        self.documentation['summary'] = summary
        logger.info("Summary generation completed")
        
    def save_documentation(self, output_format: str = 'markdown', output_file: str = None):
        """
        Save the documentation in the specified format.
        
        Parameters:
        -----------
        output_format : str
            Format for documentation ('markdown', 'json', 'html')
        output_file : str
            Output filename (auto-generated if not specified)
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"schema_documentation_{self.schema_name}_{timestamp}"
            
        if output_format == 'markdown':
            self._save_as_markdown(f"{output_file}.md")
        elif output_format == 'json':
            self._save_as_json(f"{output_file}.json")
        elif output_format == 'html':
            self._save_as_html(f"{output_file}.html")
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
    def _save_as_markdown(self, filename: str):
        """
        Save documentation as a well-formatted Markdown file.
        
        Markdown is ideal for documentation because it's human-readable,
        version-control friendly, and can be converted to other formats.
        """
        with open(filename, 'w') as f:
            # Write header
            f.write(f"# Database Schema Documentation: {self.schema_name}\n\n")
            f.write(f"Generated on: {self.documentation['metadata']['generated_at']}\n\n")
            
            # Write table of contents
            f.write("## Table of Contents\n\n")
            f.write("1. [Overview](#overview)\n")
            f.write("2. [Tables](#tables)\n")
            for table in sorted(self.documentation['tables'].keys()):
                f.write(f"   - [{table}](#{table.lower().replace('_', '-')})\n")
            f.write("3. [Relationships](#relationships)\n")
            f.write("4. [Indexes](#indexes)\n")
            f.write("5. [Triggers](#triggers)\n")
            f.write("6. [Functions](#functions)\n")
            f.write("7. [Summary Statistics](#summary-statistics)\n\n")
            
            # Write overview
            f.write("## Overview\n\n")
            f.write(f"This documentation provides a complete picture of the `{self.schema_name}` ")
            f.write("database schema. It serves as the single source of truth for understanding ")
            f.write("the data structure, relationships, and business logic implemented in the database.\n\n")
            
            meta = self.documentation['metadata']
            f.write(f"- **Database Size**: {meta['database_size']['human_readable']}\n")
            f.write(f"- **PostgreSQL Version**: {meta['database_version'].split(',')[0]}\n")
            f.write(f"- **Total Tables**: {self.documentation['summary']['total_tables']}\n")
            f.write(f"- **Total Relationships**: {self.documentation['summary']['total_relationships']}\n\n")
            
            # Write tables section
            f.write("## Tables\n\n")
            for table_name in sorted(self.documentation['tables'].keys()):
                table = self.documentation['tables'][table_name]
                f.write(f"### {table_name}\n\n")
                
                if table['comment']:
                    f.write(f"{table['comment']}\n\n")
                    
                f.write(f"**Statistics**: {table['statistics']['row_count']:,} rows, ")
                f.write(f"{table['statistics']['total_size']} total size\n\n")
                
                # Write columns table
                f.write("| Column | Type | Nullable | Default | Description |\n")
                f.write("|--------|------|----------|---------|-------------|\n")
                
                for col in table['columns']:
                    nullable = "Yes" if col['nullable'] else "No"
                    default = col['default'] if col['default'] else "-"
                    if len(default) > 50:
                        default = default[:47] + "..."
                    comment = col['comment'] if col['comment'] else "-"
                    
                    # Handle generated columns
                    if col['is_generated']:
                        col_type = f"{col['data_type']} (generated)"
                    else:
                        col_type = col['data_type']
                        
                    f.write(f"| {col['name']} | {col_type} | {nullable} | {default} | {comment} |\n")
                
                # Write constraints
                if table['constraints']:
                    f.write("\n**Constraints**:\n\n")
                    for con in table['constraints']:
                        f.write(f"- **{con['name']}** ({con['type']}): {con['definition']}\n")
                
                # Write indexes for this table
                if table_name in self.documentation['indexes']:
                    f.write("\n**Indexes**:\n\n")
                    for idx in self.documentation['indexes'][table_name]:
                        unique = " (UNIQUE)" if idx['is_unique'] else ""
                        primary = " (PRIMARY KEY)" if idx['is_primary'] else ""
                        f.write(f"- **{idx['name']}**: {', '.join(idx['columns'])}{unique}{primary}\n")
                
                # Write triggers for this table
                if table_name in self.documentation['triggers']:
                    f.write("\n**Triggers**:\n\n")
                    for trg in self.documentation['triggers'][table_name]:
                        f.write(f"- **{trg['name']}**: {trg['timing']} {trg['event']} ")
                        f.write(f"({trg['orientation']}) - Executes {trg['function']}\n")
                
                f.write("\n---\n\n")
            
            # Write relationships section
            f.write("## Relationships\n\n")
            f.write("This section documents how tables are connected through foreign key relationships. ")
            f.write("Understanding these connections is crucial for writing efficient queries and ")
            f.write("maintaining data integrity.\n\n")
            
            if self.documentation['relationships']:
                f.write("| From Table | From Column | To Table | To Column | Relationship Type | On Delete |\n")
                f.write("|------------|-------------|----------|-----------|-------------------|------------|\n")
                
                for rel in self.documentation['relationships']:
                    f.write(f"| {rel['from_table']} | {rel['from_column']} | ")
                    f.write(f"{rel['to_table']} | {rel['to_column']} | ")
                    f.write(f"{rel['relationship_type']} | {rel['delete_rule']} |\n")
            else:
                f.write("No foreign key relationships defined.\n")
            
            f.write("\n")
            
            # Write summary statistics
            f.write("## Summary Statistics\n\n")
            summary = self.documentation['summary']
            
            f.write("### Schema Overview\n\n")
            f.write(f"- **Total Tables**: {summary['total_tables']}\n")
            f.write(f"- **Total Columns**: {summary['total_columns']}\n")
            f.write(f"- **Total Relationships**: {summary['total_relationships']}\n")
            f.write(f"- **Total Indexes**: {summary['total_indexes']}\n")
            f.write(f"- **Total Triggers**: {summary['total_triggers']}\n")
            f.write(f"- **Total Functions**: {summary['total_functions']}\n\n")
            
            f.write("### Largest Tables by Row Count\n\n")
            for i, table in enumerate(summary['tables_by_rows'][:5]):
                f.write(f"{i+1}. **{table['table']}**: {table['rows']:,} rows\n")
            
            f.write("\n### Most Referenced Tables\n\n")
            f.write("These tables are referenced by foreign keys from other tables, ")
            f.write("indicating they are central to the data model:\n\n")
            
            for table, count in list(summary['most_referenced_tables'].items())[:5]:
                f.write(f"- **{table}**: Referenced by {count} foreign keys\n")
                
            if summary['orphan_tables']:
                f.write("\n### Orphan Tables\n\n")
                f.write("These tables have no foreign key relationships. They might be ")
                f.write("lookup tables, log tables, or candidates for review:\n\n")
                for table in summary['orphan_tables']:
                    f.write(f"- {table}\n")
        
        logger.info(f"Documentation saved to {filename}")
        print(f"\n✅ Schema documentation successfully saved to: {filename}")
        
    def _save_as_json(self, filename: str):
        """Save documentation as JSON for programmatic use."""
        with open(filename, 'w') as f:
            json.dump(self.documentation, f, indent=2, default=str)
        logger.info(f"Documentation saved to {filename}")
        
    def _save_as_html(self, filename: str):
        """
        Save documentation as an HTML file with styling.
        
        HTML format allows for interactive features and better visual presentation.
        """
        # This is a simplified version - you could enhance with better styling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Schema Documentation: {self.schema_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                h1, h2, h3 {{ color: #333; }}
                .metadata {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                .constraint {{ color: #d9534f; }}
                .index {{ color: #5cb85c; }}
            </style>
        </head>
        <body>
            <h1>Database Schema Documentation: {self.schema_name}</h1>
            <div class="metadata">
                <p>Generated on: {self.documentation['metadata']['generated_at']}</p>
                <p>Database Size: {self.documentation['metadata']['database_size']['human_readable']}</p>
            </div>
            <!-- Add more HTML content here -->
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html_content)
        logger.info(f"Documentation saved to {filename}")


def main():
    """
    Main function that orchestrates the schema documentation process.
    
    This is where we bring everything together and create your documentation.
    """
    parser = argparse.ArgumentParser(
        description='Generate comprehensive database schema documentation',
        epilog='This tool creates a single source of truth for your database structure.'
    )
    
    # First, try to get configuration from environment
    try:
        env_config = get_database_config()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nTo fix this, make sure you have a .env file with your database credentials.")
        print("Example .env file content:")
        print("  DB_HOST=your-host")
        print("  DB_PORT=5432")
        print("  DB_NAME=ubec_holon_etf")
        print("  DB_USER=your-username")
        print("  DB_PASSWORD=your-password")
        return 1
    
    # Database connection arguments (can override environment settings)
    parser.add_argument('--host', default=env_config['host'],
                       help='Database host (default: from environment)')
    parser.add_argument('--port', type=int, default=env_config['port'],
                       help='Database port (default: from environment)')
    parser.add_argument('--database', default=env_config['database'],
                       help='Database name (default: from environment)')
    parser.add_argument('--user', default=env_config['user'],
                       help='Database user (default: from environment)')
    parser.add_argument('--password', default=env_config.get('password'),
                       help='Database password (default: from environment)')
    
    # Schema and output arguments
    parser.add_argument('--schema', default='ubec_holon_etf',
                       help='Schema name to document')
    parser.add_argument('--format', choices=['markdown', 'json', 'html'], default='markdown',
                       help='Output format for documentation')
    parser.add_argument('--output', help='Output filename (auto-generated if not specified)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Prepare connection parameters
    conn_params = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password
    }
    
    # Show connection info (without password)
    print(f"\n🔗 Connecting to database:")
    print(f"   Host: {conn_params['host']}")
    print(f"   Port: {conn_params['port']}")
    print(f"   Database: {conn_params['database']}")
    print(f"   User: {conn_params['user']}")
    print(f"   Schema: {args.schema}\n")
    
    # Create documenter instance
    documenter = SchemaDocumenter(conn_params, args.schema)
    
    try:
        # Connect to database
        documenter.connect()
        
        # Generate documentation
        print(f"\n📚 Generating schema documentation for '{args.schema}'...")
        print("This process will examine every aspect of your database structure.\n")
        
        documenter.generate_documentation()
        
        # Save documentation
        documenter.save_documentation(args.format, args.output)
        
        # Print summary
        summary = documenter.documentation['summary']
        print(f"\n📊 Documentation Summary:")
        print(f"   - Documented {summary['total_tables']} tables")
        print(f"   - Found {summary['total_relationships']} relationships")
        print(f"   - Cataloged {summary['total_indexes']} indexes")
        print(f"   - Discovered {summary['total_triggers']} triggers")
        
        if summary['orphan_tables']:
            print(f"\n⚠️  Found {len(summary['orphan_tables'])} orphan tables that might need attention")
        
        print("\n✨ Your database schema documentation is ready!")
        print("   This documentation serves as your single source of truth.")
        print("   Share it with your team to ensure everyone understands the data model.\n")
        
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        print(f"\n❌ Error: {e}")
        print("   Please check your database connection parameters and try again.")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
        
    finally:
        documenter.disconnect()
    
    return 0


if __name__ == "__main__":
    exit(main())
