import requests
from django.conf import settings

PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET = settings.PAYPAL_CLIENT_SECRET
PAYPAL_API_BASE = "https://api-m.paypal.com"  # Production
# PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"  # Sandbox

def get_paypal_access_token():
    """Obtenir un token d'accès OAuth 2.0 de PayPal."""
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), data=data, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

def verify_paypal_webhook(headers, body):
    """Vérifie la signature du webhook PayPal."""
    access_token = get_paypal_access_token()
    if not access_token:
        return False

    url = f"{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature"
    data = {
        "auth_algo": headers.get("PAYPAL-AUTH-ALGO"),
        "cert_url": headers.get("PAYPAL-CERT-URL"),
        "transmission_id": headers.get("PAYPAL-TRANSMISSION-ID"),
        "transmission_sig": headers.get("PAYPAL-TRANSMISSION-SIG"),
        "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME"),
        "webhook_id": settings.PAYPAL_WEBHOOK_ID,  # Ton Webhook ID PayPal
        "webhook_event": body
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, json=data, headers=headers)

    return response.status_code == 200 and response.json().get("verification_status") == "SUCCESS"
