"""
HTTP-triggered Azure Function: CRUD API for tracked products.

Routes (all require Bearer token):
  GET    /api/products          - list user's products
  POST   /api/products          - add a product
  PATCH  /api/products/{id}     - update desired_size
  DELETE /api/products/{id}     - remove a product
"""
import json
import logging
import azure.functions as func
from shared.auth import validate_token, get_user_id, get_user_email
from shared import cosmos_client as db

logger = logging.getLogger(__name__)


def _json_response(body, status_code=200):
    return func.HttpResponse(
        json.dumps(body),
        status_code=status_code,
        mimetype="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
        },
    )


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return _json_response({}, 204)

    # Authenticate
    try:
        claims = validate_token(req.headers.get("Authorization", ""))
    except ValueError as exc:
        return _json_response({"error": str(exc)}, 401)

    user_id = get_user_id(claims)
    user_email = get_user_email(claims)

    # Route by method and URL segment
    route = req.route_params.get("id")  # None for collection routes

    try:
        if req.method == "GET" and not route:
            products = db.list_products(user_id)
            return _json_response(products)

        elif req.method == "POST" and not route:
            body = req.get_json()
            url = (body.get("url") or "").strip()
            size = (body.get("desired_size") or "").strip()
            if not url or not size:
                return _json_response({"error": "url and desired_size are required"}, 400)
            product = db.create_product(user_id, url, size)
            # Store email alongside product for notifications
            db.update_product(user_id, product["id"], {"user_email": user_email})
            product["user_email"] = user_email
            return _json_response(product, 201)

        elif req.method == "PATCH" and route:
            body = req.get_json()
            updates = {}
            if "desired_size" in body:
                updates["desired_size"] = body["desired_size"].strip()
            if not updates:
                return _json_response({"error": "No valid fields to update"}, 400)
            updated = db.update_product(user_id, route, updates)
            if not updated:
                return _json_response({"error": "Product not found"}, 404)
            return _json_response(updated)

        elif req.method == "DELETE" and route:
            deleted = db.delete_product(user_id, route)
            if not deleted:
                return _json_response({"error": "Product not found"}, 404)
            return _json_response({"message": "Deleted"}, 200)

        else:
            return _json_response({"error": "Method not allowed"}, 405)

    except Exception as exc:
        logger.exception("Unhandled error in products_api")
        return _json_response({"error": "Internal server error"}, 500)
