import requests
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CurrencyAPI:
    def __init__(self):
        self.base_url = "https://api.frankfurter.app"
        self._cache = {}
    
    def get_exchange_rates(self, base: str = "USD", symbols: Optional[str] = None) -> Optional[Dict]:
        cache_key = f"{base}_{symbols}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            url = f"{self.base_url}/latest"
            params = {"from": base}
            if symbols:
                params["to"] = symbols
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self._cache[cache_key] = data
            return data
        except Exception as e:
            logger.error(f"Error fetching currency data: {e}")
            return self._get_mock_rates(base)
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return amount
        
        try:
            url = f"{self.base_url}/latest"
            params = {
                "from": from_currency,
                "to": to_currency,
                "amount": amount
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return round(data["rates"][to_currency], 2)
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return amount
    
    def get_currency_symbol(self, currency_code: str) -> str:
        symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "AUD": "A$",
            "CAD": "C$",
            "CHF": "Fr",
            "CNY": "¥",
            "INR": "₹",
            "SGD": "S$",
            "NZD": "NZ$",
            "THB": "฿",
            "AED": "د.إ",
            "BRL": "R$",
            "ZAR": "R",
            "MXN": "$",
            "KRW": "₩",
            "TRY": "₺",
            "IDR": "Rp",
            "MAD": "د.م.",
            "CZK": "Kč",
            "HUF": "Ft",
            "ILS": "₪",
            "DKK": "kr",
            "NOK": "kr",
            "SEK": "kr",
            "PLN": "zł",
            "RUB": "₽",
            "ISK": "kr",
            "COP": "$",
            "ARS": "$",
            "CLP": "$",
            "PEN": "S/",
            "VND": "₫",
            "PHP": "₱",
            "MYR": "RM",
            "EGP": "E£",
            "JOD": "د.ا",
            "MVR": "Rf",
            "TZS": "TSh",
            "CUP": "$",
            "XPF": "₣"
        }
        return symbols.get(currency_code, currency_code)
    
    def _get_mock_rates(self, base: str = "USD") -> Dict:
        return {
            "amount": 1.0,
            "base": base,
            "date": "2025-11-24",
            "rates": {
                "EUR": 0.92,
                "GBP": 0.79,
                "JPY": 149.50,
                "AUD": 1.53,
                "CAD": 1.39,
                "CHF": 0.88,
                "CNY": 7.24,
                "INR": 83.25,
                "SGD": 1.34,
                "THB": 35.20,
                "AED": 3.67,
                "BRL": 4.92,
                "ZAR": 18.15
            }
        }


currency_api = CurrencyAPI()
