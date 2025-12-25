"""
Midtrans REST API Client for Payment Integration
Documentation: https://docs.midtrans.com/en/snap/overview
"""
import os
import base64
import requests
from typing import Dict, Optional, List


class MidtransClient:
    """
    Midtrans Payment Gateway Client using REST API
    Supports: Snap (all payment methods), QRIS, GoPay, ShopeePay, Bank Transfer
    """
    
    SANDBOX_URL = "https://app.sandbox.midtrans.com/snap/v1"
    PRODUCTION_URL = "https://app.midtrans.com/snap/v1"
    
    def __init__(self, server_key: Optional[str] = None, is_production: bool = False):
        self.server_key = server_key or os.getenv('MIDTRANS_SERVER_KEY', '')
        self.is_production = is_production
        self.base_url = self.PRODUCTION_URL if is_production else self.SANDBOX_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Basic {self._encode_server_key()}'
        }
    
    def _encode_server_key(self) -> str:
        """Encode server key for Basic Auth"""
        credentials = f"{self.server_key}:"
        return base64.b64encode(credentials.encode()).decode()
    
    def create_snap_transaction(
        self,
        order_id: str,
        gross_amount: int,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        enabled_payments: Optional[List[str]] = None
    ) -> Dict:
        """
        Create Snap Transaction (All-in-one payment page)
        
        Args:
            order_id: Unique order ID
            gross_amount: Total amount in IDR
            customer_name: Customer full name
            customer_email: Customer email
            customer_phone: Customer phone
            enabled_payments: List of payment methods (e.g., ['gopay', 'qris', 'bank_transfer'])
            
        Returns:
            dict with token (for Snap popup) and redirect_url
        """
        url = f"{self.base_url}/transactions"
        
        if enabled_payments is None:
            enabled_payments = ['gopay', 'qris', 'shopeepay', 'bank_transfer', 'echannel']
        
        payload = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": gross_amount
            },
            "customer_details": {
                "first_name": customer_name,
                "email": customer_email,
                "phone": customer_phone
            },
            "enabled_payments": enabled_payments,
            "credit_card": {
                "secure": True
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def create_qris_transaction(
        self,
        order_id: str,
        gross_amount: int,
        customer_name: str
    ) -> Dict:
        """
        Create QRIS-only Transaction
        
        Args:
            order_id: Unique order ID
            gross_amount: Total amount in IDR
            customer_name: Customer name
            
        Returns:
            dict with qr_code string (base64) and transaction details
        """
        return self.create_snap_transaction(
            order_id=order_id,
            gross_amount=gross_amount,
            customer_name=customer_name,
            customer_email=f"{order_id}@pos.local",
            customer_phone="081234567890",
            enabled_payments=['qris']
        )
    
    def create_gopay_transaction(
        self,
        order_id: str,
        gross_amount: int,
        customer_name: str,
        customer_phone: str
    ) -> Dict:
        """
        Create GoPay Transaction
        
        Args:
            order_id: Unique order ID
            gross_amount: Total amount in IDR
            customer_name: Customer name
            customer_phone: Customer phone for GoPay notification
            
        Returns:
            dict with deeplink for GoPay app and qr_code
        """
        return self.create_snap_transaction(
            order_id=order_id,
            gross_amount=gross_amount,
            customer_name=customer_name,
            customer_email=f"{order_id}@pos.local",
            customer_phone=customer_phone,
            enabled_payments=['gopay']
        )
    
    def get_transaction_status(self, order_id: str) -> Dict:
        """
        Get Transaction Status by Order ID
        
        Args:
            order_id: Your order ID
            
        Returns:
            dict with transaction status and details
        """
        base_url = "https://api.sandbox.midtrans.com/v2" if not self.is_production else "https://api.midtrans.com/v2"
        url = f"{base_url}/{order_id}/status"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def cancel_transaction(self, order_id: str) -> Dict:
        """
        Cancel Transaction
        
        Args:
            order_id: Your order ID
            
        Returns:
            dict with cancellation status
        """
        base_url = "https://api.sandbox.midtrans.com/v2" if not self.is_production else "https://api.midtrans.com/v2"
        url = f"{base_url}/{order_id}/cancel"
        
        try:
            response = requests.post(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def verify_notification(self, notification_json: Dict) -> Dict:
        """
        Verify and Parse Midtrans Notification/Webhook
        
        Args:
            notification_json: Webhook payload from Midtrans
            
        Returns:
            dict with parsed transaction status
        """
        order_id = notification_json.get('order_id')
        transaction_status = notification_json.get('transaction_status')
        fraud_status = notification_json.get('fraud_status')
        
        status_map = {
            'capture': 'success' if fraud_status == 'accept' else 'pending',
            'settlement': 'success',
            'pending': 'pending',
            'deny': 'failed',
            'expire': 'expired',
            'cancel': 'cancelled'
        }
        
        return {
            'order_id': order_id,
            'status': status_map.get(transaction_status, 'unknown'),
            'raw_status': transaction_status,
            'fraud_status': fraud_status,
            'payment_type': notification_json.get('payment_type'),
            'gross_amount': notification_json.get('gross_amount')
        }


# Convenience function for easy import
def get_midtrans_client(is_production: bool = False) -> MidtransClient:
    """Factory function to get Midtrans client instance"""
    return MidtransClient(is_production=is_production)
