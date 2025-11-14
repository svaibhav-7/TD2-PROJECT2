"""
Data processing module - handles data cleaning, analysis, and transformation
"""

import json
import logging
import csv
import io
from typing import Dict, Any, List, Union, Optional
import pandas as pd
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handle data processing tasks"""
    
    def __init__(self):
        """Initialize DataProcessor"""
        pass
    
    def process_csv(self, csv_data: Union[str, bytes]) -> pd.DataFrame:
        """Process CSV data"""
        try:
            if isinstance(csv_data, bytes):
                csv_data = csv_data.decode('utf-8')
            
            return pd.read_csv(io.StringIO(csv_data))
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            return None
    
    def process_json(self, json_data: Union[str, dict]) -> Union[Dict, List]:
        """Process JSON data"""
        try:
            if isinstance(json_data, str):
                return json.loads(json_data)
            return json_data
        except Exception as e:
            logger.error(f"Error processing JSON: {e}")
            return None
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting from PDF: {e}")
            return ""
    
    def aggregate_data(self, df: pd.DataFrame, agg_dict: Dict[str, str]) -> pd.DataFrame:
        """Aggregate data using groupby"""
        try:
            return df.groupby(agg_dict.get('groupby')).agg(agg_dict.get('agg', 'sum'))
        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            return None
    
    def sum_column(self, df: pd.DataFrame, column: str) -> float:
        """Sum a column"""
        try:
            return float(df[column].sum())
        except Exception as e:
            logger.error(f"Error summing column: {e}")
            return None
    
    def count_rows(self, df: pd.DataFrame, condition: Optional[Dict] = None) -> int:
        """Count rows matching condition"""
        try:
            if condition:
                for col, val in condition.items():
                    df = df[df[col] == val]
            return len(df)
        except Exception as e:
            logger.error(f"Error counting rows: {e}")
            return None
    
    def filter_data(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Filter dataframe"""
        try:
            result = df
            for col, condition in filters.items():
                if isinstance(condition, dict):
                    if 'min' in condition:
                        result = result[result[col] >= condition['min']]
                    if 'max' in condition:
                        result = result[result[col] <= condition['max']]
                else:
                    result = result[result[col] == condition]
            return result
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            return None
    
    def sort_data(self, df: pd.DataFrame, by: str, ascending: bool = True) -> pd.DataFrame:
        """Sort dataframe"""
        try:
            return df.sort_values(by=by, ascending=ascending)
        except Exception as e:
            logger.error(f"Error sorting data: {e}")
            return None
    
    def calculate_statistics(self, df: pd.DataFrame, column: str) -> Dict[str, float]:
        """Calculate basic statistics"""
        try:
            return {
                'mean': float(df[column].mean()),
                'median': float(df[column].median()),
                'std': float(df[column].std()),
                'min': float(df[column].min()),
                'max': float(df[column].max()),
                'sum': float(df[column].sum())
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def pivot_table(self, df: pd.DataFrame, index: str, columns: str, values: str, aggfunc: str = 'sum') -> pd.DataFrame:
        """Create pivot table"""
        try:
            return pd.pivot_table(df, index=index, columns=columns, values=values, aggfunc=aggfunc)
        except Exception as e:
            logger.error(f"Error creating pivot table: {e}")
            return None
    
    def merge_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame, on: str, how: str = 'inner') -> pd.DataFrame:
        """Merge two dataframes"""
        try:
            return pd.merge(df1, df2, on=on, how=how)
        except Exception as e:
            logger.error(f"Error merging dataframes: {e}")
            return None
    
    def generate_chart(self, df: pd.DataFrame, chart_type: str, x: str, y: str) -> str:
        """Generate chart as base64 image"""
        try:
            import matplotlib.pyplot as plt
            import base64
            from io import BytesIO
            
            fig, ax = plt.subplots()
            
            if chart_type == 'bar':
                df.plot(x=x, y=y, kind='bar', ax=ax)
            elif chart_type == 'line':
                df.plot(x=x, y=y, kind='line', ax=ax)
            elif chart_type == 'scatter':
                df.plot(x=x, y=y, kind='scatter', ax=ax)
            elif chart_type == 'pie':
                df.set_index(x)[y].plot(kind='pie', ax=ax)
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return f"data:image/png;base64,{img_base64}"
        
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean text data"""
        try:
            # Remove extra whitespace
            text = ' '.join(text.split())
            # Remove special characters
            import re
            text = re.sub(r'[^a-zA-Z0-9\s\-.]', '', text)
            return text
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text
    
    def extract_numbers(self, text: str) -> List[float]:
        """Extract numbers from text"""
        try:
            import re
            numbers = re.findall(r'-?\d+\.?\d*', text)
            return [float(n) for n in numbers]
        except Exception as e:
            logger.error(f"Error extracting numbers: {e}")
            return []
    
    def calculate_correlation(self, df: pd.DataFrame, col1: str, col2: str) -> float:
        """Calculate correlation between two columns"""
        try:
            return float(df[col1].corr(df[col2]))
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return None
    
    def apply_transformation(self, df: pd.DataFrame, column: str, transform: str) -> pd.DataFrame:
        """Apply transformation to column"""
        try:
            if transform == 'log':
                df[column] = np.log(df[column])
            elif transform == 'sqrt':
                df[column] = np.sqrt(df[column])
            elif transform == 'square':
                df[column] = df[column] ** 2
            elif transform == 'normalize':
                df[column] = (df[column] - df[column].mean()) / df[column].std()
            return df
        except Exception as e:
            logger.error(f"Error applying transformation: {e}")
            return None
