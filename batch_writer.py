"""
Batch metafield writer for efficient bulk operations.
"""

from typing import List, Dict, Any, Optional
from shopify_client import ShopifyClient
from metafield_writer import SafeMetafieldWriter, MetafieldTypeTransformer


class BatchMetafieldWriter:
    """Write multiple metafields in a single API call for efficiency."""
    
    def __init__(self, shopify_client: ShopifyClient):
        """
        Initialize batch writer.
        
        Args:
            shopify_client: Initialized ShopifyClient instance
        """
        self.client = shopify_client
        self.writer = SafeMetafieldWriter(shopify_client)
        self.transformer = MetafieldTypeTransformer()
    
    def write_product_metafields_batch(
        self,
        product_id: str,
        metafields: List[Dict[str, Any]],
        auto_detect_types: bool = True
    ) -> Dict[str, Any]:
        """
        Write multiple metafields to a product in a single mutation.
        
        Args:
            product_id: Product GID
            metafields: List of metafield dicts with keys: namespace, key, value, type (optional)
            auto_detect_types: If True, auto-detect types from definitions
            
        Returns:
            Mutation result with product and userErrors
        """
        processed_metafields = []
        
        # Process each metafield
        for metafield in metafields:
            namespace = metafield.get("namespace")
            key = metafield.get("key")
            value = metafield.get("value")
            metafield_type = metafield.get("type")
            
            if not namespace or not key:
                continue
            
            # Auto-detect type if needed
            if auto_detect_types and not metafield_type:
                definition = self.writer._get_cached_definition(namespace, key)
                if definition:
                    metafield_type = definition.get("type")
                else:
                    existing = self.client.get_product_metafield(product_id, namespace, key)
                    if existing:
                        metafield_type = existing.get("type")
            
            if not metafield_type:
                raise ValueError(f"Cannot determine type for {namespace}.{key}")
            
            # Transform value
            transformed_value = self.transformer.transform_value(value, metafield_type)
            
            processed_metafields.append({
                "namespace": namespace,
                "key": key,
                "type": metafield_type,
                "value": transformed_value
            })
        
        # Batch mutation
        mutation = """
        mutation productUpdateMetafields($input: ProductInput!) {
            productUpdate(input: $input) {
                product {
                    id
                    metafields(identifiers: $identifiers) {
                        id
                        namespace
                        key
                        type
                        value
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        
        identifiers = [
            {"namespace": m["namespace"], "key": m["key"]}
            for m in processed_metafields
        ]
        
        variables = {
            "input": {
                "id": product_id,
                "metafields": processed_metafields
            },
            "identifiers": identifiers
        }
        
        try:
            result = self.client.graphql_request(mutation, variables)
            update_result = result.get("productUpdate", {})
            
            user_errors = update_result.get("userErrors", [])
            if user_errors:
                error_messages = [f"{e.get('field', '')}: {e.get('message', '')}" for e in user_errors]
                raise Exception(f"Batch metafield write failed: {'; '.join(error_messages)}")
            
            return update_result
        except Exception as e:
            raise Exception(f"Failed to write batch metafields to product {product_id}: {e}")
