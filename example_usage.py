"""
Example usage of SafeMetafieldWriter to fix metafield write issues.
"""

import os
from shopify_client import ShopifyClient
from metafield_writer import SafeMetafieldWriter


def main():
    """Example: Write metafields safely with type validation."""
    
    # Initialize Shopify client
    shop_domain = os.getenv("SHOPIFY_SHOP_DOMAIN", "your-shop.myshopify.com")
    access_token = os.getenv("SHOPIFY_ACCESS_TOKEN", "your_token")
    api_version = os.getenv("SHOPIFY_API_VERSION", "2024-10")
    
    client = ShopifyClient(shop_domain, access_token, api_version)
    writer = SafeMetafieldWriter(client)
    
    # Example product ID (replace with actual GID)
    product_id = "gid://shopify/Product/123456789"
    namespace = "custom"
    key = "example_key"
    
    # Example 1: Write text metafield (auto-detects type from definition)
    try:
        result = writer.write_product_metafield(
            product_id=product_id,
            namespace=namespace,
            key="description",
            value="This is a product description"
        )
        print("✅ Text metafield written successfully")
        print(f"   Metafield: {result['product']['metafields'][0]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Write number metafield (with explicit type)
    try:
        result = writer.write_product_metafield(
            product_id=product_id,
            namespace=namespace,
            key="inventory_count",
            value=42,  # Can be int or string "42"
            metafield_type="number_integer"
        )
        print("✅ Number metafield written successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Write JSON metafield
    try:
        json_data = {
            "tags": ["tag1", "tag2"],
            "metadata": {"key": "value"}
        }
        result = writer.write_product_metafield(
            product_id=product_id,
            namespace=namespace,
            key="json_data",
            value=json_data,
            metafield_type="json"
        )
        print("✅ JSON metafield written successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 4: Write list metafield
    try:
        result = writer.write_product_metafield(
            product_id=product_id,
            namespace=namespace,
            key="tags_list",
            value=["tag1", "tag2", "tag3"],
            metafield_type="list.single_line_text_field"
        )
        print("✅ List metafield written successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 5: Write with auto-type detection from existing definition
    try:
        # Writer will fetch the type from metafield definition automatically
        result = writer.write_product_metafield(
            product_id=product_id,
            namespace=namespace,
            key="existing_metafield",
            value="New value"
            # Type will be auto-detected from definition
        )
        print("✅ Metafield written with auto-detected type")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
