import os
import csv
import requests
import datetime
from flask import current_app

class MarketStackService:
    def __init__(self, api_key, api_endpoint="http://api.marketstack.com/v1/eod"):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.cache_file = "stock_data.csv"
        # Mega 7 companies
        self.symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"]

    def get_stock_data(self):
        """
        Retrieves stock data for the Mega 7 companies.
        First checks if valid cache exists. If not, fetches from API and updates cache.
        """
        if self._is_cache_valid():
            return self._read_cache()
        else:
            return self._fetch_from_api()

    def _is_cache_valid(self):
        """
        Checks if the cache file exists and was modified today.
        """
        if not os.path.exists(self.cache_file):
            return False
        
        file_time = os.path.getmtime(self.cache_file)
        file_date = datetime.date.fromtimestamp(file_time)
        today = datetime.date.today()
        
        # Simple daily cache: valid if file was created/modified today
        return file_date == today

    def _read_cache(self):
        """
        Reads data from the CSV cache file.
        """
        data = []
        try:
            with open(self.cache_file, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
        except Exception as e:
            print(f"Error reading cache: {e}")
            return []

    def _fetch_from_api(self):
        """
        Fetches data from MarketStack API and saves to cache.
        """
        params = {
            'access_key': self.api_key,
            'symbols': ','.join(self.symbols),
            'limit': 14  # 7 companies * 2 days = 14 records roughly needed
        }
        
        try:
            response = requests.get(self.api_endpoint, params=params)
            response.raise_for_status()
            api_data = response.json()
            
            if 'data' not in api_data:
                print("No data found in API response")
                return []

            # Process data: flatten and keep relevant fields
            processed_data = []
            for item in api_data['data']:
                processed_data.append({
                    'symbol': item.get('symbol'),
                    'date': item.get('date', '')[:10], # format date YYYY-MM-DD
                    'open': item.get('open'),
                    'high': item.get('high'),
                    'low': item.get('low'),
                    'close': item.get('close'),
                    'volume': item.get('volume')
                })
            
            self._save_cache(processed_data)
            return processed_data

        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            # Fallback to existing cache if possible, even if old? 
            # For now, return empty or what we have.
            if os.path.exists(self.cache_file):
                print("Falling back to stale cache.")
                return self._read_cache()
            return []

    def _save_cache(self, data):
        """
        Saves the processed data to CSV.
        """
        if not data:
            return

        fieldnames = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        try:
            with open(self.cache_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            print(f"Error saving cache: {e}")
