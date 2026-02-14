# src/reporting/data_fetcher.py
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Union
from supabase import create_client, Client


class DataFetcher:
    """
    Fetches and aggregates quality control data from Supabase database
    with support for time-based filtering.
    
    Note: This class expects the database 'logs' table to have:
    - 'created_at' field: ISO 8601 timestamp (e.g., '2026-02-14T01:14:48.850995+00:00')
    - 'prediction' field: Classification result ('Fresh' or 'Dry')
    """

    def __init__(self, debug: bool = False):
        db_url = os.environ.get("DB_API")
        db_key = os.environ.get("DB_SERVICE_ROLE_KEY")
        
        if not db_url or not db_key:
            raise ValueError("DB_API and DB_SERVICE_ROLE_KEY must be set in environment")
        
        self.supabase: Client = create_client(db_url, db_key)
        self.debug = debug

    def fetch_all_data(self) -> Dict[str, Union[int, str]]:
        """
        Fetch all records and return aggregated statistics.
        
        Returns:
            Dict with keys: total, fresh, dry, time_period
        """
        try:
            response = self.supabase.table("logs").select("*").execute()
            data = response.data or []
            return self._aggregate_data(data, "All time")
        except Exception as e:
            print(f"Error fetching all data: {e}")
            return {"total": 0, "fresh": 0, "dry": 0, "time_period": "Error"}

    def fetch_by_hours(self, hours: int) -> Dict[str, Union[int, str]]:
        """
        Fetch records from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dict with keys: total, fresh, dry, time_period
        """
        start_time = datetime.now() - timedelta(hours=hours)
        start_time_str = start_time.isoformat()
        
        if self.debug:
            print(f"[DEBUG] Fetching last {hours} hours")
            print(f"[DEBUG] Start time: {start_time_str}")
            print(f"[DEBUG] Query: created_at >= '{start_time_str}'")
        
        try:
            response = (
                self.supabase.table("logs")
                .select("*")
                .gte("created_at", start_time_str)
                .execute()
            )
            data = response.data or []
            
            if self.debug:
                print(f"[DEBUG] Retrieved {len(data)} records")
            
            time_period = f"Last {hours} hour{'s' if hours > 1 else ''}"
            return self._aggregate_data(data, time_period)
        except Exception as e:
            print(f"Error fetching data for last {hours} hours: {e}")
            return {"total": 0, "fresh": 0, "dry": 0, "time_period": f"Last {hours} hours (Error)"}

    def fetch_by_date_range(self, start_date: datetime, end_date: datetime) -> Dict[str, Union[int, str]]:
        """
        Fetch records within a specific date range.
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            
        Returns:
            Dict with keys: total, fresh, dry, time_period
        """
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        try:
            response = (
                self.supabase.table("logs")
                .select("*")
                .gte("created_at", start_str)
                .lte("created_at", end_str)
                .execute()
            )
            data = response.data or []
            time_period = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            return self._aggregate_data(data, time_period)
        except Exception as e:
            print(f"Error fetching data for date range: {e}")
            return {"total": 0, "fresh": 0, "dry": 0, "time_period": "Date range (Error)"}

    def fetch_by_days(self, days: int) -> Dict[str, Union[int, str]]:
        """
        Fetch records from the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict with keys: total, fresh, dry, time_period
        """
        start_date = datetime.now() - timedelta(days=days)
        start_date_str = start_date.isoformat()
        
        try:
            response = (
                self.supabase.table("logs")
                .select("*")
                .gte("created_at", start_date_str)
                .execute()
            )
            data = response.data or []
            time_period = f"Last {days} day{'s' if days > 1 else ''}"
            return self._aggregate_data(data, time_period)
        except Exception as e:
            print(f"Error fetching data for last {days} days: {e}")
            return {"total": 0, "fresh": 0, "dry": 0, "time_period": f"Last {days} days (Error)"}

    def _aggregate_data(self, data: list, time_period: str) -> Dict[str, Union[int, str]]:
        """
        Aggregate raw data into statistics.
        
        Args:
            data: List of log records
            time_period: Description of the time period
            
        Returns:
            Dict with keys: total, fresh, dry, time_period
        """
        total = len(data)
        fresh = sum(1 for record in data if record.get("prediction", "").lower() == "fresh")
        dry = sum(1 for record in data if record.get("prediction", "").lower() == "dry")
        
        return {
            "total": total,
            "fresh": fresh,
            "dry": dry,
            "time_period": time_period
        }

    def get_time_series_data(self, hours: int = 24) -> list:
        """
        Get time-series data for visualization (hourly aggregation).
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of dicts with created_at, fresh_count, dry_count
        """
        start_time = datetime.now() - timedelta(hours=hours)
        start_time_str = start_time.isoformat()
        
        try:
            response = (
                self.supabase.table("logs")
                .select("*")
                .gte("created_at", start_time_str)
                .order("created_at")
                .execute()
            )
            return response.data or []
        except Exception as e:
            print(f"Error fetching time series data: {e}")
            return []
