"""Cosmos DB client singleton and helper functions."""
import os
import uuid
import logging
from datetime import datetime, timezone
from azure.cosmos import CosmosClient, PartitionKey, exceptions

logger = logging.getLogger(__name__)

ENDPOINT = os.environ["COSMOS_ENDPOINT"]
KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["COSMOS_DATABASE"]
CONTAINER_NAME = os.environ["COSMOS_CONTAINER"]

_client = None
_container = None


def get_container():
    global _client, _container
    if _container is None:
        _client = CosmosClient(ENDPOINT, credential=KEY)
        db = _client.create_database_if_not_exists(DATABASE_NAME)
        _container = db.create_container_if_not_exists(
            id=CONTAINER_NAME,
            partition_key=PartitionKey(path="/user_id"),
            offer_throughput=400,
        )
    return _container


def create_product(user_id: str, url: str, desired_size: str) -> dict:
    container = get_container()
    item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "url": url,
        "desired_size": desired_size,
        "status": "pending",
        "last_checked": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    container.create_item(body=item)
    return item


def list_products(user_id: str) -> list:
    container = get_container()
    query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.created_at DESC"
    items = list(container.query_items(
        query=query,
        parameters=[{"name": "@user_id", "value": user_id}],
        enable_cross_partition_query=False,
    ))
    return items


def get_product(user_id: str, product_id: str) -> dict:
    container = get_container()
    try:
        return container.read_item(item=product_id, partition_key=user_id)
    except exceptions.CosmosResourceNotFoundError:
        return None


def update_product(user_id: str, product_id: str, updates: dict) -> dict:
    container = get_container()
    item = get_product(user_id, product_id)
    if not item:
        return None
    item.update(updates)
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    container.replace_item(item=product_id, body=item)
    return item


def delete_product(user_id: str, product_id: str) -> bool:
    container = get_container()
    try:
        container.delete_item(item=product_id, partition_key=user_id)
        return True
    except exceptions.CosmosResourceNotFoundError:
        return False


def list_all_products_for_checker() -> list:
    """Used by the timer trigger to fetch all tracked products across all users."""
    container = get_container()
    return list(container.query_items(
        query="SELECT * FROM c WHERE c.status != 'available'",
        enable_cross_partition_query=True,
    ))
