"""
Timer-triggered Azure Function: checks product availability every minute
and sends email notifications when a product becomes available.
"""
import logging
from datetime import datetime, timezone
import azure.functions as func
from shared import cosmos_client as db
from shared.scraper import check_availability
from shared.email_sender import send_availability_email

logger = logging.getLogger(__name__)


def main(mytimer: func.TimerRequest) -> None:
    utc_now = datetime.now(timezone.utc).isoformat()
    logger.info("Availability checker triggered at %s", utc_now)

    products = db.list_all_products_for_checker()
    logger.info("Checking %d products", len(products))

    for product in products:
        product_id = product["id"]
        user_id = product["user_id"]
        url = product.get("url", "")
        desired_size = product.get("desired_size", "")
        user_email = product.get("user_email", "")

        if not url or not desired_size:
            logger.warning("Skipping product %s: missing url or size", product_id)
            continue

        try:
            is_available = check_availability(url, desired_size)
            updates = {
                "last_checked": utc_now,
                "status": "available" if is_available else "unavailable",
            }
            db.update_product(user_id, product_id, updates)

            if is_available and user_email:
                logger.info(
                    "Size %s available for product %s - notifying %s",
                    desired_size, product_id, user_email,
                )
                send_availability_email(user_email, url, desired_size)
                # Mark as notified so we don't spam
                db.update_product(user_id, product_id, {"status": "available", "notified": True})

        except Exception as exc:
            logger.error("Error checking product %s: %s", product_id, exc)
