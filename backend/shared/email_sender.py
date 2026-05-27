"""Send availability notification emails via Azure Communication Services."""
import os
import logging
from azure.communication.email import EmailClient

logger = logging.getLogger(__name__)

ACS_CONNECTION_STRING = os.environ["ACS_CONNECTION_STRING"]
SENDER = os.environ["EMAIL_SENDER"]


def send_availability_email(to_email: str, product_url: str, desired_size: str) -> None:
    """
    Send an email notification to the user when their product size is available.
    """
    client = EmailClient.from_connection_string(ACS_CONNECTION_STRING)

    hostname = product_url.split("/")[2] if "//" in product_url else product_url

    subject = f"✅ Your size {desired_size} is now available!"
    html_body = f"""
    <html>
    <body style="font-family: Segoe UI, Arial, sans-serif; background: #f3f2f1; padding: 2rem;">
      <div style="max-width: 520px; margin: auto; background: #fff; border-radius: 8px;
                  box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 2rem;">
        <h2 style="color: #0078d4;">🛍️ Product Availability Alert</h2>
        <p>Great news! The product you are tracking is now available in your desired size.</p>
        <table style="width:100%; border-collapse: collapse; margin: 1.2rem 0;">
          <tr>
            <td style="padding: 0.5rem; font-weight: bold; color: #605e5c;">Product</td>
            <td style="padding: 0.5rem;">{hostname}</td>
          </tr>
          <tr style="background: #f3f2f1;">
            <td style="padding: 0.5rem; font-weight: bold; color: #605e5c;">Size</td>
            <td style="padding: 0.5rem; font-weight: bold; color: #107c10;">{desired_size}</td>
          </tr>
        </table>
        <a href="{product_url}"
           style="display: inline-block; background: #0078d4; color: #fff;
                  padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none;
                  font-weight: bold;">View Product</a>
        <p style="margin-top: 1.5rem; font-size: 0.8rem; color: #605e5c;">
          You are receiving this because you set up a tracker on Product Availability Tracker.
        </p>
      </div>
    </body>
    </html>
    """

    message = {
        "senderAddress": SENDER,
        "recipients": {"to": [{"address": to_email}]},
        "content": {"subject": subject, "html": html_body},
    }

    try:
        poller = client.begin_send(message)
        result = poller.result()
        logger.info("Email sent to %s, message_id=%s", to_email, result.get("id"))
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        raise
