import pandas as pd
import re

class NLtoSQL:
    """
    Natural Language to SQL/Pandas query converter.
    Translates user questions into pandas operations on the dataframe.
    """
    
    def __init__(self, data):
        self.data = data
        self.available_columns = list(data.columns)
        
    def parse_and_execute(self, query):
        """
        Parse natural language query and execute on dataframe.
        
        Returns:
            dict with 'result' (data) and 'sql_equivalent' (string)
        """
        query_lower = query.lower()
        
        # Aggregation queries
        if "average" in query_lower or "mean" in query_lower:
            return self._handle_aggregation(query_lower, 'mean')
        elif "sum" in query_lower or "total" in query_lower:
            return self._handle_aggregation(query_lower, 'sum')
        elif "max" in query_lower or "maximum" in query_lower or "highest" in query_lower:
            return self._handle_aggregation(query_lower, 'max')
        elif "min" in query_lower or "minimum" in query_lower or "lowest" in query_lower:
            return self._handle_aggregation(query_lower, 'min')
        elif "count" in query_lower or "how many" in query_lower:
            return self._handle_count(query_lower)
        
        # Filtering queries
        elif "where" in query_lower or "when" in query_lower:
            return self._handle_filter(query_lower)
        
        # Grouping queries
        elif "by" in query_lower and ("group" in query_lower or "breakdown" in query_lower):
            return self._handle_groupby(query_lower)
        
        # Top N queries
        elif "top" in query_lower:
            return self._handle_top_n(query_lower)
        
        # Show all data
        elif "show" in query_lower or "display" in query_lower:
            return self._handle_show(query_lower)
        
        else:
            return {
                'result': None,
                'sql_equivalent': 'Query not understood',
                'error': 'Could not parse query'
            }
    
    def _handle_aggregation(self, query, agg_func):
        """Handle aggregation queries like 'average sales by category'."""
        # Try to find column name
        column = self._extract_column(query)
        
        if not column:
            return {'result': None, 'sql_equivalent': 'Column not found', 'error': 'Could not identify column'}
        
        # Check for grouping
        if " by " in query:
            group_col = self._extract_group_column(query)
            if group_col:
                result = self.data.groupby(group_col)[column].agg(agg_func).reset_index()
                sql = f"SELECT {group_col}, {agg_func.upper()}({column}) FROM data GROUP BY {group_col}"
                return {'result': result, 'sql_equivalent': sql}
        
        # Simple aggregation
        result = getattr(self.data[column], agg_func)()
        sql = f"SELECT {agg_func.upper()}({column}) FROM data"
        return {'result': result, 'sql_equivalent': sql}
    
    def _handle_count(self, query):
        """Handle count queries."""
        if " by " in query:
            group_col = self._extract_group_column(query)
            if group_col:
                result = self.data.groupby(group_col).size().reset_index(name='count')
                sql = f"SELECT {group_col}, COUNT(*) FROM data GROUP BY {group_col}"
                return {'result': result, 'sql_equivalent': sql}
        
        result = len(self.data)
        sql = "SELECT COUNT(*) FROM data"
        return {'result': result, 'sql_equivalent': sql}
    
    def _handle_filter(self, query):
        """Handle filtering queries."""
        # Simple implementation - can be extended
        result = self.data
        sql = "SELECT * FROM data WHERE <condition>"
        return {'result': result, 'sql_equivalent': sql}
    
    def _handle_groupby(self, query):
        """Handle group by queries."""
        group_col = self._extract_group_column(query)
        agg_col = self._extract_column(query)
        
        if group_col and agg_col:
            result = self.data.groupby(group_col)[agg_col].sum().reset_index()
            sql = f"SELECT {group_col}, SUM({agg_col}) FROM data GROUP BY {group_col}"
            return {'result': result, 'sql_equivalent': sql}
        
        return {'result': None, 'sql_equivalent': 'Could not parse group by', 'error': 'Missing columns'}
    
    def _handle_top_n(self, query):
        """Handle top N queries like 'top 5 sales'."""
        # Extract N
        n = 5  # default
        match = re.search(r'top (\d+)', query)
        if match:
            n = int(match.group(1))
        
        # Extract column to sort by
        column = self._extract_column(query)
        if not column:
            column = 'Total_Sales'  # default
        
        result = self.data.nlargest(n, column)
        sql = f"SELECT * FROM data ORDER BY {column} DESC LIMIT {n}"
        return {'result': result, 'sql_equivalent': sql}
    
    def _handle_show(self, query):
        """Handle show/display queries."""
        # Extract column if specified
        column = self._extract_column(query)
        
        if column:
            result = self.data[[column]].head(10)
            sql = f"SELECT {column} FROM data LIMIT 10"
        else:
            result = self.data.head(10)
            sql = "SELECT * FROM data LIMIT 10"
        
        return {'result': result, 'sql_equivalent': sql}
    
    def _extract_column(self, query):
        """Extract column name from query."""
        # Check for common column patterns
        for col in self.available_columns:
            if col.lower() in query or col.replace('_', ' ').lower() in query:
                return col
        
        # Check for semantic matches
        if 'sales' in query or 'revenue' in query:
            if 'Total_Sales' in self.available_columns:
                return 'Total_Sales'
        
        if 'spend' in query or 'investment' in query:
            for col in self.available_columns:
                if 'TV' in col or 'Digital' in col:
                    return col
        
        return None
    
    def _extract_group_column(self, query):
        """Extract grouping column from query."""
        # Look for "by <column>"
        match = re.search(r'by (\w+)', query)
        if match:
            potential_col = match.group(1)
            for col in self.available_columns:
                if col.lower() == potential_col or col.replace('_', ' ').lower() == potential_col:
                    return col
        
        # Check for common grouping columns
        if 'month' in query:
            return 'month'
        if 'date' in query:
            return 'Date'
        if 'category' in query:
            for col in self.available_columns:
                if 'category' in col.lower():
                    return col
        
        return None
