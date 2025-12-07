"""
AI Explainer Utility
Uses Snowflake Cortex to generate plain-language explanations
"""

import streamlit as st
from typing import Dict, Any, List
import pandas as pd
from .snowflake_connector import get_connection

class AIExplainer:
    """Generates AI-powered explanations for query results"""
    
    def __init__(self):
        self.conn = get_connection()
        self.model = "mistral-large"
    
    def explain_query_results(
        self, 
        query: str, 
        results: pd.DataFrame,
        context: str = ""
    ) -> str:
        """
        Generates a plain-language explanation of query results
        
        Args:
            query: The SQL query that was executed
            results: DataFrame with query results
            context: Additional context about the query
            
        Returns:
            Plain language explanation
        """
        # Prepare results summary
        if results.empty:
            return "No patterns detected in the data."
        
        # Create a concise summary of results
        results_summary = self._summarize_results(results)
        
        prompt = f"""
You are analyzing privacy-safe, aggregated data from multiple financial organizations.

Context: {context}

Query Type: Cross-company fraud risk analysis

Results Summary:
{results_summary}

Provide a 2-3 sentence explanation that:
1. Describes the key pattern or insight found
2. Explains what this means for fraud detection or risk management
3. Suggests one concrete next action

Keep it professional and concise. Do not mention technical details like SQL or databases.
"""
        
        try:
            explanation = self.conn.execute_cortex_query(prompt)
            return explanation
        except Exception as e:
            return f"Unable to generate explanation. Key finding: {self._get_top_insight(results)}"
    
    def _summarize_results(self, df: pd.DataFrame, max_rows: int = 5) -> str:
        """Creates a text summary of DataFrame results"""
        summary_lines = []
        
        # Get top rows
        top_data = df.head(max_rows)
        
        for idx, row in top_data.iterrows():
            row_summary = ", ".join([f"{col}: {val}" for col, val in row.items()])
            summary_lines.append(f"- {row_summary}")
        
        return "\n".join(summary_lines)
    
    def _get_top_insight(self, df: pd.DataFrame) -> str:
        """Extracts the most important insight from results"""
        if df.empty:
            return "No significant patterns detected."
        
        # Heuristic: look for columns with "risk", "count", or "amount"
        risk_cols = [col for col in df.columns if 'risk' in col.lower()]
        count_cols = [col for col in df.columns if 'count' in col.lower()]
        
        if risk_cols:
            top_row = df.nlargest(1, risk_cols[0]).iloc[0]
            return f"Highest risk found in {top_row.to_dict()}"
        elif count_cols:
            top_row = df.nlargest(1, count_cols[0]).iloc[0]
            return f"Highest occurrence: {top_row.to_dict()}"
        else:
            return f"Top result: {df.iloc[0].to_dict()}"
    
    def generate_fraud_alert_description(
        self, 
        pattern_type: str, 
        affected_count: int,
        risk_score: int
    ) -> str:
        """
        Generates a description for a detected fraud pattern
        
        Args:
            pattern_type: Type of fraud pattern
            affected_count: Number of affected records (aggregated)
            risk_score: Risk score (0-100)
            
        Returns:
            Human-readable alert description
        """
        prompt = f"""
A fraud detection system has identified a pattern in cross-company data.

Pattern Type: {pattern_type}
Affected Profiles: {affected_count} (aggregated, anonymized)
Risk Score: {risk_score}/100

Write a 2-sentence alert that:
1. Explains what this pattern means in plain language
2. Recommends an immediate action for fraud investigators

Be specific but don't reveal any personal information.
"""
        
        try:
            description = self.conn.execute_cortex_query(prompt)
            return description
        except:
            return f"Pattern detected: {pattern_type}. Risk level: {risk_score}/100. Review affected segment for potential fraud."
    
    def suggest_next_queries(
        self, 
        current_query: str, 
        results: pd.DataFrame
    ) -> List[str]:
        """
        Suggests follow-up questions based on current results
        
        Args:
            current_query: The question that was just asked
            results: The results obtained
            
        Returns:
            List of suggested follow-up questions
        """
        results_summary = self._summarize_results(results, max_rows=2)
        
        prompt = f"""
A user asked: "{current_query}"

They received these results (summarized):
{results_summary}

Suggest 3 relevant follow-up questions they might want to ask to dig deeper into these findings.
Each question should be on a new line, starting with "- ".
Questions should be about fraud patterns, risk analysis, or demographic insights.
"""
        
        try:
            suggestions = self.conn.execute_cortex_query(prompt)
            # Parse into list
            questions = [q.strip('- ').strip() for q in suggestions.split('\n') if q.strip().startswith('-')]
            return questions[:3]  # Return top 3
        except:
            return [
                "What geographic areas show similar patterns?",
                "Which age groups are most affected?",
                "Has this pattern changed over time?"
            ]
    
    def translate_to_sql(self, natural_language_query: str) -> str:
        """
        Converts natural language question to SQL query
        
        Args:
            natural_language_query: User's question in plain English
            
        Returns:
            Generated SQL query (to be reviewed before execution)
        """
        prompt = f"""
You are a SQL expert for Snowflake specializing in privacy-safe analytics.

Available tables:
- CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK (age_group, risk_score, claim_amount, default_rate)
- CLEANROOM_DB.AGGREGATED_VIEWS.GEOGRAPHIC_RISK (zip_code_prefix, risk_score, customer_count)
- CLEANROOM_DB.FRAUD_DETECTION.DETECTED_PATTERNS (pattern_type, risk_level, affected_segments)

CRITICAL RULES:
1. NEVER select individual customer records
2. ALL results must be aggregated with COUNT(*) >= 50
3. Use HAVING COUNT(*) >= 50 to enforce minimum group size
4. Never expose PII (names, emails, SSN, etc.)

User question: {natural_language_query}

Generate a Snowflake SQL query that answers this question while following ALL privacy rules.
Return ONLY the SQL query, no explanations.
"""
        
        try:
            sql_query = self.conn.execute_cortex_query(prompt)
            # Clean up the response
            sql_query = sql_query.strip().strip('```sql').strip('```').strip()
            return sql_query
        except Exception as e:
            return f"-- Error generating query: {str(e)}"

# Singleton instance
_explainer = None

def get_explainer() -> AIExplainer:
    """Returns singleton AIExplainer instance"""
    global _explainer
    if _explainer is None:
        _explainer = AIExplainer()
    return _explainer
