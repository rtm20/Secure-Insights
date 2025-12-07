"""
Query Builder Utility
Constructs safe, privacy-compliant SQL queries
"""

from typing import Dict, List, Optional, Any
import streamlit as st

class QueryBuilder:
    """Builds privacy-safe SQL queries for cross-company analytics"""
    
    def __init__(self, min_aggregation_size: int = 50):
        self.min_agg_size = min_aggregation_size
        self.cleanroom_db = "CLEANROOM_DB"
    
    def build_fraud_risk_query(
        self,
        group_by_column: str = "age_group",
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Builds a query to analyze fraud risk by demographic groups
        
        Args:
            group_by_column: Column to group by (age_group, zip_code, etc.)
            filters: Optional filters to apply
            
        Returns:
            SQL query string
        """
        query = f"""
        SELECT 
            {group_by_column},
            COUNT(*) as record_count,
            ROUND(AVG(risk_score), 2) as avg_risk_score,
            ROUND(AVG(claim_amount), 2) as avg_claim_amount,
            ROUND(AVG(default_rate) * 100, 2) as default_rate_pct,
            MIN(first_seen_date) as earliest_date,
            MAX(last_seen_date) as latest_date
        FROM {self.cleanroom_db}.AGGREGATED_VIEWS.CROSS_ORG_RISK
        WHERE 1=1
        """
        
        # Add filters if provided
        if filters:
            for key, value in filters.items():
                if isinstance(value, str):
                    query += f"\n  AND {key} = '{value}'"
                else:
                    query += f"\n  AND {key} = {value}"
        
        query += f"""
        GROUP BY {group_by_column}
        HAVING COUNT(*) >= {self.min_agg_size}
        ORDER BY avg_risk_score DESC
        """
        
        return query
    
    def build_geographic_analysis_query(
        self,
        top_n: int = 20,
        min_risk_score: Optional[float] = None
    ) -> str:
        """
        Builds a query for geographic risk analysis
        
        Args:
            top_n: Number of top risk areas to return
            min_risk_score: Minimum risk score threshold
            
        Returns:
            SQL query string
        """
        query = f"""
        SELECT 
            zip_code_prefix,
            COUNT(DISTINCT customer_id_hash) as unique_customers,
            ROUND(AVG(risk_score), 2) as avg_risk_score,
            SUM(CASE WHEN fraud_flag = 1 THEN 1 ELSE 0 END) as fraud_cases,
            ROUND(SUM(CASE WHEN fraud_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as fraud_rate_pct
        FROM {self.cleanroom_db}.AGGREGATED_VIEWS.GEOGRAPHIC_RISK
        WHERE 1=1
        """
        
        if min_risk_score:
            query += f"\n  AND risk_score >= {min_risk_score}"
        
        query += f"""
        GROUP BY zip_code_prefix
        HAVING COUNT(DISTINCT customer_id_hash) >= {self.min_agg_size}
        ORDER BY avg_risk_score DESC
        LIMIT {top_n}
        """
        
        return query
    
    def build_cross_org_pattern_query(
        self,
        status: str = "ACTIVE",
        min_risk_level: int = 60
    ) -> str:
        """
        Builds a query to find cross-organization fraud patterns
        
        Args:
            status: Pattern status (ACTIVE, RESOLVED, etc.)
            min_risk_level: Minimum risk level (0-100)
            
        Returns:
            SQL query string
        """
        query = f"""
        SELECT 
            pattern_id,
            pattern_type,
            pattern_description,
            organization_count,
            affected_segment_count,
            risk_level,
            confidence_score,
            first_detected,
            last_updated,
            status
        FROM {self.cleanroom_db}.FRAUD_DETECTION.DETECTED_PATTERNS
        WHERE status = '{status}'
          AND risk_level >= {min_risk_level}
          AND affected_segment_count >= {self.min_agg_size}
        ORDER BY risk_level DESC, last_updated DESC
        """
        
        return query
    
    def build_time_series_query(
        self,
        metric: str = "fraud_cases",
        group_by: str = "month",
        lookback_months: int = 12
    ) -> str:
        """
        Builds a time-series query for trend analysis
        
        Args:
            metric: Metric to track (fraud_cases, risk_score, etc.)
            group_by: Time grouping (day, week, month)
            lookback_months: Number of months to look back
            
        Returns:
            SQL query string
        """
        date_trunc_map = {
            'day': 'DAY',
            'week': 'WEEK',
            'month': 'MONTH'
        }
        
        date_part = date_trunc_map.get(group_by, 'MONTH')
        
        query = f"""
        SELECT 
            DATE_TRUNC('{date_part}', event_date) as time_period,
            COUNT(*) as total_events,
            SUM(CASE WHEN fraud_flag = 1 THEN 1 ELSE 0 END) as fraud_cases,
            ROUND(AVG(risk_score), 2) as avg_risk_score,
            COUNT(DISTINCT organization_id) as participating_orgs
        FROM {self.cleanroom_db}.AGGREGATED_VIEWS.TIME_SERIES_RISK
        WHERE event_date >= DATEADD(MONTH, -{lookback_months}, CURRENT_DATE())
        GROUP BY DATE_TRUNC('{date_part}', event_date)
        HAVING COUNT(*) >= {self.min_agg_size}
        ORDER BY time_period DESC
        """
        
        return query
    
    def build_segment_comparison_query(
        self,
        segment_column: str,
        segments_to_compare: List[str]
    ) -> str:
        """
        Builds a query to compare different customer segments
        
        Args:
            segment_column: Column defining segments (age_group, income_bracket, etc.)
            segments_to_compare: List of segment values to compare
            
        Returns:
            SQL query string
        """
        segments_str = "', '".join(segments_to_compare)
        
        query = f"""
        SELECT 
            {segment_column},
            COUNT(*) as segment_size,
            ROUND(AVG(risk_score), 2) as avg_risk_score,
            ROUND(AVG(claim_count), 2) as avg_claims,
            ROUND(AVG(transaction_velocity), 2) as avg_transaction_velocity,
            SUM(CASE WHEN high_risk_flag = 1 THEN 1 ELSE 0 END) as high_risk_count,
            ROUND(SUM(CASE WHEN high_risk_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as high_risk_pct
        FROM {self.cleanroom_db}.AGGREGATED_VIEWS.SEGMENT_ANALYSIS
        WHERE {segment_column} IN ('{segments_str}')
        GROUP BY {segment_column}
        HAVING COUNT(*) >= {self.min_agg_size}
        ORDER BY avg_risk_score DESC
        """
        
        return query
    
    def validate_query(self, query: str) -> tuple[bool, str]:
        """
        Validates that a query follows privacy rules
        
        Args:
            query: SQL query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        query_upper = query.upper()
        
        # Check for forbidden patterns
        forbidden_patterns = [
            ('SSN', 'Query cannot access SSN'),
            ('EMAIL', 'Query cannot access email addresses'),
            ('PHONE', 'Query cannot access phone numbers'),
            ('CREDIT_CARD', 'Query cannot access credit card numbers'),
            ('ACCOUNT_NUMBER', 'Query cannot access account numbers'),
            ('FULL_NAME', 'Query cannot access full names'),
        ]
        
        for pattern, error in forbidden_patterns:
            if pattern in query_upper:
                return False, error
        
        # Check for aggregation
        if 'GROUP BY' not in query_upper:
            return False, "Query must include GROUP BY for aggregation"
        
        # Check for minimum size constraint
        if f'HAVING COUNT(*) >= {self.min_agg_size}' not in query_upper.replace(' ', ''):
            return False, f"Query must include HAVING COUNT(*) >= {self.min_agg_size}"
        
        return True, "Query is valid"

# Singleton instance
_builder = None

def get_query_builder() -> QueryBuilder:
    """Returns singleton QueryBuilder instance"""
    global _builder
    if _builder is None:
        _builder = QueryBuilder()
    return _builder
