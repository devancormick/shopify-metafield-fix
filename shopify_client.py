"""
Shopify Admin API client wrapper for metafield operations.
"""

import json
import time
from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ShopifyClient:
    """Client for interacting with Shopify Admin API."""
    
    def __init__(self, shop_domain: str, access_token: str, api_version: str = "2024-10"):
        """
        Initialize Shopify client.
        
        Args:
            shop_domain: Shop domain (e.g., 'your-shop.myshopify.com')
            access_token: Admin API access token
            api_version: API version (default: 2024-10)
        """
        self.shop_domain = shop_domain.rstrip('/')
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://{self.shop_domain}/admin/api/{self.api_version}"
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        })
    
    def graphql_request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute GraphQL request.
        
        Args:
            query: GraphQL query/mutation string
            variables: Query variables
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}/graphql.json"
        payload = {"query": query, "variables": variables or {}}
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for GraphQL errors
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result.get("data", {})
    
    def get_product_metafield_definition(
        self,
        namespace: str,
        key: str,
        product_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get metafield definition for a product by namespace and key.
        
        Args:
            namespace: Metafield namespace
            key: Metafield key
            product_id: Optional product ID to check product-specific metafields
            
        Returns:
            Metafield definition dict or None if not found
        """
        query = """
        query getMetafieldDefinition($namespace: String!, $key: String!) {
            metafieldDefinitions(
                namespace: $namespace
                keys: [$key]
                first: 1
            ) {
                edges {
                    node {
                        id
                        name
                        namespace
                        key
                        type {
                            name
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "namespace": namespace,
            "key": key
        }
        
        try:
            data = self.graphql_request(query, variables)
            edges = data.get("metafieldDefinitions", {}).get("edges", [])
            
            if edges:
                node = edges[0]["node"]
                return {
                    "id": node["id"],
                    "namespace": node["namespace"],
                    "key": node["key"],
                    "type": node["type"]["name"],
                    "name": node.get("name")
                }
        except Exception as e:
            print(f"Warning: Could not fetch metafield definition: {e}")
        
        return None
    
    def get_product_metafield(
        self,
        product_id: str,
        namespace: str,
        key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing metafield value from a product.
        
        Args:
            product_id: Product GID (e.g., 'gid://shopify/Product/123')
            namespace: Metafield namespace
            key: Metafield key
            
        Returns:
            Metafield dict or None if not found
        """
        query = """
        query getProductMetafield($productId: ID!, $namespace: String!, $key: String!) {
            product(id: $productId) {
                metafield(namespace: $namespace, key: $key) {
                    id
                    namespace
                    key
                    type
                    value
                }
            }
        }
        """
        
        variables = {
            "productId": product_id,
            "namespace": namespace,
            "key": key
        }
        
        try:
            data = self.graphql_request(query, variables)
            product = data.get("product")
            
            if product and product.get("metafield"):
                return product["metafield"]
        except Exception as e:
            print(f"Warning: Could not fetch product metafield: {e}")
        
        return None
