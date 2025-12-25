"""
Xendit REST API Client for Payment Integration
Direct HTTP integration without relying on unstable SDK packages
Documentation: https://developers.xendit.co/api-reference/
"""
import os
import base64
import requests
from typing import Dict, Optional


class XenditClient:
    """
    Xendit Payment Gateway Client using REST API
    Supports: QRIS, E-Wallet (GoPay, OVO, Dana, ShopeePay), Virtual Account
    """
    
    BASE_URL = "https://api.xendit.co"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('XENDIT_SECRET_KEY', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self._encode_api_key()}'
        }
    
    def _encode_api_key(self) -> str:
        """Encode API key for Basic Auth (Xendit requires base64 of api_key:)"""
        credentials = f"{self.api_key}:"
        return base64.b64encode(credentials.encode()).decode()
    
    def create_qris_payment(self, amount: int, external_id: str, callback_url: str) -> Dict:
        """
        Create QRIS Payment
        
        Args:
            amount: Amount in IDR (e.g., 100000 for Rp 100,000)
            external_id: Unique order ID from your system
            callback_url: URL for payment webhook callback
            
        Returns:
            dict with qr_string (base64 image) and payment details
        """
        url = f"{self.BASE_URL}/qr_codes"
        payload = {
            "external_id": external_id,
            "type": "DYNAMIC",
            "callback_url": callback_url,
            "amount": amount
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def create_ewallet_payment(
        self,
        ewallet_type: str,
        amount: int,
        external_id: str,
        phone_number: str,
        callback_url: str,
        redirect_url: str
    ) -> Dict:
        """
        Create E-Wallet Payment (GoPay, OVO, Dana, ShopeePay, LinkAja)
        
        Args:
            ewallet_type: 'ID_OVO', 'ID_DANA', 'ID_LINKAJA', 'ID_SHOPEEPAY'
            amount: Amount in IDR
            external_id: Unique order ID
            phone_number: Customer phone (e.g., '+62812345678')
            callback_url: Webhook callback URL
            redirect_url: Redirect after payment success
            
        Returns:
            dict with checkout_url and payment details
        """
        url = f"{self.BASE_URL}/ewallets/charges"
        payload = {
            "reference_id": external_id,
            "currency": "IDR",
            "amount": amount,
            "checkout_method": "ONE_TIME_PAYMENT",
            "channel_code": ewallet_type,
            "channel_properties": {
                "mobile_number": phone_number,
                "success_redirect_url": redirect_url
            },
            "metadata": {
                "branch": "POS Kiosk"
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def create_virtual_account(
        self,
        bank_code: str,
        amount: int,
        external_id: str,
        name: str
    ) -> Dict:
        """
        Create Virtual Account Payment (BCA, BNI, BRI, Mandiri, Permata)
        
        Args:
            bank_code: 'BCA', 'BNI', 'BRI', 'MANDIRI', 'PERMATA'
            amount: Amount in IDR (or None for open amount)
            external_id: Unique order ID
            name: Customer name for VA
            
        Returns:
            dict with account_number and bank details
        """
        url = f"{self.BASE_URL}/callback_virtual_accounts"
        payload = {
            "external_id": external_id,
            "bank_code": bank_code,
            "name": name,
            "is_closed": True,
            "expected_amount": amount,
            "is_single_use": True
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def get_payment_status(self, payment_id: str) -> Dict:
        """
        Get Payment Status by ID
        
        Args:
            payment_id: Xendit payment/charge ID
            
        Returns:
            dict with payment status and details
        """
        url = f"{self.BASE_URL}/v2/invoices/{payment_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def verify_callback(self, callback_token: str, request_token: str) -> bool:
        """
        Verify Xendit Callback Webhook Token
        
        Args:
            callback_token: Your stored callback verification token
            request_token: Token from webhook request header
            
        Returns:
            bool: True if token is valid
        """
        return callback_token == request_token


# Convenience function for easy import
def get_xendit_client() -> XenditClient:
    """Factory function to get Xendit client instance"""
    return XenditClient()
