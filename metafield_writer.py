"""
Safe metafield writer with type validation and transformation.
"""

import json
from typing import Dict, Any, Optional, Union, List
from shopify_client import ShopifyClient


class MetafieldTypeTransformer:
    """Transforms values to match Shopify metafield type requirements."""
    
    # Map of Shopify metafield types to their expected value formats
    TYPE_FORMATS = {
        # Text types
        "single_line_text_field": str,
        "multi_line_text_field": str,
        "page_reference": str,
        "product_reference": str,
        "variant_reference": str,
        "file_reference": str,
        
        # Number types
        "number_integer": int,
        "number_decimal": float,
        
        # Boolean
        "boolean": bool,
        
        # Date/time
        "date": str,  # ISO 8601 format
        "date_time": str,  # ISO 8601 format
        
        # JSON
        "json": (dict, list),  # Will be serialized to JSON string
        
        # Color
        "color": str,
        
        # Rating
        "rating": int,  # 1-5 typically
        
        # Dimension
        "dimension": dict,  # {value: float, unit: str}
        "volume": dict,
        "weight": dict,
        
        # List types
        "list.single_line_text_field": list,
        "list.number_integer": list,
        "list.number_decimal": list,
        "list.product_reference": list,
        "list.variant_reference": list,
        "list.file_reference": list,
    }
    
    @classmethod
    def transform_value(cls, value: Any, metafield_type: str) -> str:
        """
        Transform value to match Shopify metafield type format.
        
        All values are returned as strings (Shopify requirement).
        
        Args:
            value: Value to transform
            metafield_type: Shopify metafield type (e.g., 'single_line_text_field')
            
        Returns:
            Transformed value as string
        """
        # Handle list types
        if metafield_type.startswith("list."):
            return cls._transform_list_value(value, metafield_type)
        
        # Handle JSON types
        if metafield_type == "json":
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            elif isinstance(value, str):
                # Try to parse and re-stringify to validate JSON
                try:
                    parsed = json.loads(value)
                    return json.dumps(parsed)
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid JSON string: {value}")
            else:
                return json.dumps(value)
        
        # Handle number types
        if metafield_type == "number_integer":
            if isinstance(value, str):
                try:
                    int_value = int(float(value))  # Handle "123.0" -> 123
                    return str(int_value)
                except (ValueError, TypeError):
                    raise ValueError(f"Cannot convert '{value}' to integer")
            return str(int(value))
        
        if metafield_type == "number_decimal":
            if isinstance(value, str):
                try:
                    float_value = float(value)
                    return str(float_value)
                except (ValueError, TypeError):
                    raise ValueError(f"Cannot convert '{value}' to decimal")
            return str(float(value))
        
        # Handle boolean
        if metafield_type == "boolean":
            if isinstance(value, bool):
                return str(value).lower()
            if isinstance(value, str):
                return value.lower() if value.lower() in ("true", "false") else str(bool(value))
            return str(bool(value)).lower()
        
        # Handle dimension/volume/weight types
        if metafield_type in ("dimension", "volume", "weight"):
            if isinstance(value, dict):
                return json.dumps(value)
            if isinstance(value, str):
                try:
                    # Validate it's valid JSON
                    parsed = json.loads(value)
                    return json.dumps(parsed)
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid JSON for {metafield_type}: {value}")
            raise ValueError(f"{metafield_type} must be a dict or JSON string")
        
        # Handle text types (default) - convert to string
        return str(value)
    
    @classmethod
    def _transform_list_value(cls, value: Any, list_type: str) -> str:
        """Transform value for list types."""
        # Ensure value is a list
        if not isinstance(value, list):
            # If it's a string, try to parse as JSON array
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    # If not JSON, treat as single-item list
                    value = [value]
            else:
                # Single value -> convert to list
                value = [value]
        
        # Get base type (e.g., "single_line_text_field" from "list.single_line_text_field")
        base_type = list_type.replace("list.", "")
        
        # Transform each item
        transformed_items = []
        for item in value:
            transformed = cls.transform_value(item, base_type)
            transformed_items.append(transformed)
        
        # Return as JSON array string
        return json.dumps(transformed_items)


class SafeMetafieldWriter:
    """Safely writes metafields with validation and error handling."""
    
    def __init__(self, shopify_client: ShopifyClient):
        """
        Initialize safe metafield writer.
        
        Args:
            shopify_client: Initialized ShopifyClient instance
        """
        self.client = shopify_client
        self.transformer = MetafieldTypeTransformer()
        self._definition_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_cached_definition(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        """Get metafield definition from cache or API."""
        cache_key = f"{namespace}:{key}"
        
        if cache_key not in self._definition_cache:
            definition = self.client.get_product_metafield_definition(namespace, key)
            if definition:
                self._definition_cache[cache_key] = definition
        
        return self._definition_cache.get(cache_key)
    
    def write_product_metafield(
        self,
        product_id: str,
        namespace: str,
        key: str,
        value: Any,
        metafield_type: Optional[str] = None,
        force_type: bool = False
    ) -> Dict[str, Any]:
        """
        Safely write a product metafield with type validation.
        
        Args:
            product_id: Product GID (e.g., 'gid://shopify/Product/123')
            namespace: Metafield namespace
            key: Metafield key
            value: Value to write (will be transformed to match type)
            metafield_type: Optional explicit type (if not provided, will fetch from definition)
            force_type: If True, use provided type even if definition exists
            
        Returns:
            Mutation result with product and userErrors
            
        Raises:
            ValueError: If type cannot be determined or value transformation fails
        """
        # Step 1: Get or determine metafield type
        determined_type = metafield_type
        
        if not force_type:
            # Try to get from existing definition
            definition = self._get_cached_definition(namespace, key)
            
            # If no definition, try to get from existing metafield on product
            if not definition:
                existing_metafield = self.client.get_product_metafield(product_id, namespace, key)
                if existing_metafield:
                    determined_type = existing_metafield.get("type")
        
        # If still no type, use provided or raise error
        if not determined_type:
            if metafield_type:
                determined_type = metafield_type
            else:
                raise ValueError(
                    f"Cannot determine metafield type for {namespace}.{key}. "
                    f"Please provide metafield_type or ensure definition exists."
                )
        
        # Step 2: Transform value to match type
        try:
            transformed_value = self.transformer.transform_value(value, determined_type)
        except ValueError as e:
            raise ValueError(
                f"Value transformation failed for {namespace}.{key} "
                f"(type: {determined_type}): {e}"
            )
        
        # Step 3: Write metafield via GraphQL mutation
        mutation = """
        mutation productUpdateMetafield($input: ProductInput!) {
            productUpdate(input: $input) {
                product {
                    id
                    metafields(identifiers: [{namespace: $namespace, key: $key}]) {
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
        
        variables = {
            "input": {
                "id": product_id,
                "metafields": [{
                    "namespace": namespace,
                    "key": key,
                    "type": determined_type,
                    "value": transformed_value
                }]
            },
            "namespace": namespace,
            "key": key
        }
        
        try:
            result = self.client.graphql_request(mutation, variables)
            update_result = result.get("productUpdate", {})
            
            # Check for user errors
            user_errors = update_result.get("userErrors", [])
            if user_errors:
                error_messages = [f"{e.get('field', '')}: {e.get('message', '')}" for e in user_errors]
                raise Exception(f"Metafield write failed: {'; '.join(error_messages)}")
            
            return update_result
            
        except Exception as e:
            # Re-raise with context
            raise Exception(
                f"Failed to write metafield {namespace}.{key} to product {product_id}: {e}"
            )
