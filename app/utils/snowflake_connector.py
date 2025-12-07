"""
Snowflake Connection Utility
Handles all database connections and queries
"""

import streamlit as st
import snowflake.connector
from snowflake.connector import DictCursor
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SnowflakeConnection:
    """Manages Snowflake database connections"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        """
        Establishes connection to Snowflake
        Returns True if successful, False otherwise
        """
        try:
            # Get credentials from environment or Streamlit secrets
            if hasattr(st, 'secrets') and 'snowflake' in st.secrets:
                config = st.secrets['snowflake']
            else:
                config = {
                    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
                    'user': os.getenv('SNOWFLAKE_USER'),
                    'password': os.getenv('SNOWFLAKE_PASSWORD'),
                    'token': os.getenv('SNOWFLAKE_TOKEN'),
                    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                    'role': os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN'),
                }
            
            # Use PAT if available, otherwise password
            if config.get('token'):
                self.connection = snowflake.connector.connect(
                    account=config['account'],
                    user=config['user'],
                    authenticator='oauth',
                    token=config['token'],
                    warehouse=config['warehouse'],
                    role=config['role'],
                )
            else:
                self.connection = snowflake.connector.connect(
                    account=config['account'],
                    user=config['user'],
                    password=config['password'],
                    warehouse=config['warehouse'],
                    role=config['role'],
                )
            
            self.cursor = self.connection.cursor(DictCursor)
            return True
            
        except Exception as e:
            st.error(f"Failed to connect to Snowflake: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Executes a SQL query and returns results as DataFrame
        
        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries
            
        Returns:
            DataFrame with query results
        """
        try:
            if not self.connection:
                self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            
            if results:
                return pd.DataFrame(results)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return pd.DataFrame()
    
    def execute_cortex_query(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Executes a Snowflake Cortex AI query
        
        Args:
            prompt: The prompt for the AI model
            context: Optional context for the query
            
        Returns:
            AI-generated response
        """
        try:
            model = os.getenv('CORTEX_MODEL', 'mistral-large')
            
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            else:
                full_prompt = prompt
            
            query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{model}',
                '{full_prompt}'
            ) as response
            """
            
            result = self.execute_query(query)
            
            if not result.empty:
                return result.iloc[0]['RESPONSE']
            else:
                return "No response generated"
                
        except Exception as e:
            st.error(f"Cortex AI query failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_aggregated_insights(
        self, 
        query_type: str, 
        parameters: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Executes privacy-safe aggregated queries
        
        Args:
            query_type: Type of analysis (e.g., 'fraud_risk', 'demographic')
            parameters: Query parameters
            
        Returns:
            DataFrame with aggregated results
        """
        # Load query template based on type
        query_templates = {
            'fraud_risk': """
                SELECT 
                    age_group,
                    COUNT(*) as total_cases,
                    AVG(risk_score) as avg_risk_score,
                    SUM(claim_amount) / COUNT(*) as avg_claim_amount
                FROM CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK
                WHERE COUNT(*) >= 50  -- Privacy: minimum aggregation
                GROUP BY age_group
                HAVING COUNT(*) >= 50
                ORDER BY avg_risk_score DESC
            """,
            'geographic': """
                SELECT 
                    zip_code_prefix,
                    COUNT(DISTINCT customer_id_hash) as customer_count,
                    AVG(risk_score) as avg_risk_score,
                    COUNT(CASE WHEN fraud_flag = 1 THEN 1 END) as fraud_cases
                FROM CLEANROOM_DB.AGGREGATED_VIEWS.GEOGRAPHIC_RISK
                GROUP BY zip_code_prefix
                HAVING COUNT(DISTINCT customer_id_hash) >= 50
                ORDER BY avg_risk_score DESC
                LIMIT 20
            """,
            'cross_org_pattern': """
                SELECT 
                    pattern_type,
                    organization_count,
                    affected_segments,
                    risk_level,
                    first_detected,
                    last_updated
                FROM CLEANROOM_DB.FRAUD_DETECTION.DETECTED_PATTERNS
                WHERE status = 'ACTIVE'
                ORDER BY risk_level DESC, last_updated DESC
            """
        }
        
        query = query_templates.get(query_type, "")
        
        if query:
            return self.execute_query(query)
        else:
            return pd.DataFrame()
    
    def log_audit_trail(
        self, 
        user: str, 
        query_type: str, 
        query: str, 
        result_count: int
    ):
        """
        Logs query execution for audit purposes
        
        Args:
            user: User who executed the query
            query_type: Type of query executed
            query: The actual query or description
            result_count: Number of results returned
        """
        try:
            audit_query = """
            INSERT INTO SECURE_INSIGHTS_DB.AUDIT.QUERY_LOG
            (timestamp, user_id, query_type, query_text, result_count)
            VALUES (CURRENT_TIMESTAMP(), ?, ?, ?, ?)
            """
            
            self.cursor.execute(audit_query, (user, query_type, query, result_count))
            self.connection.commit()
            
        except Exception as e:
            # Audit logging failure shouldn't break the app
            print(f"Audit logging failed: {str(e)}")
    
    def close(self):
        """Closes the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

# Singleton instance
_connection = None

def get_connection() -> SnowflakeConnection:
    """Returns a singleton Snowflake connection"""
    global _connection
    if _connection is None:
        _connection = SnowflakeConnection()
    return _connection

@st.cache_data(ttl=3600)
def get_cached_query(_conn: SnowflakeConnection, query: str) -> pd.DataFrame:
    """
    Cached query execution for frequently accessed data
    Note: _conn parameter starts with _ to prevent hashing
    """
    return _conn.execute_query(query)
