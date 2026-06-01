import pyodbc
import pandas as pd
import streamlit as st

@st.cache_resource
def get_connection():
    """Establishes and caches the connection to SQL Server."""
    try:
        return pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost;"
            "Database=MockCorpDB;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

def execute_query(query, conn):
    """Executes a SQL query and returns a Pandas DataFrame."""
    return pd.read_sql(query, conn)

def get_schema():
    """Returns the database schema so the AI knows what tables/columns exist."""
    return """
    Tables:
    1. Departments (DepartmentID INT, DepartmentName NVARCHAR, AnnualBudget DECIMAL)
    2. Transactions (TransactionID INT, DepartmentID INT, Amount DECIMAL, TransactionDate DATE, VendorName NVARCHAR)
    """