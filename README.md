# Shopify Metafield Write Fix

Fixes intermittent metafield write failures in Shopify Admin API by:
1. **Reading metafield definitions** before writing
2. **Validating and transforming values** to match expected types
3. **Handling errors gracefully** with proper type checking

## Problem

Metafield writes fail with errors like:
- "value is invalid"
- "metafield definition not found"  
- "type mismatch"

This happens when values are written in the wrong format for the metafield type.

## Solution

The `SafeMetafieldWriter` class:
- ✅ Fetches metafield definition to determine correct type
- ✅ Transforms values to match Shopify's required format
- ✅ Handles all common metafield types (text, numbers, JSON, lists, etc.)
- ✅ Provides clear error messages when transformation fails

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `env.example` to `.env` and set your Shopify credentials:

```bash
cp env.example .env
```

Edit `.env`:
```
SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_admin_api_access_token
SHOPIFY_API_VERSION=2024-10
```

## Usage

### Basic Example

```python
from shopify_client import ShopifyClient
from metafield_writer import SafeMetafieldWriter

# Initialize client
client = ShopifyClient(
    shop_domain="your-shop.myshopify.com",
    access_token="your_token"
)

# Create safe writer
writer = SafeMetafieldWriter(client)

# Write metafield (type auto-detected from definition)
result = writer.write_product_metafield(
    product_id="gid://shopify/Product/123",
    namespace="custom",
    key="description",
    value="Product description text"
)
```

### With Explicit Type

```python
# Write number metafield
result = writer.write_product_metafield(
    product_id="gid://shopify/Product/123",
    namespace="custom",
    key="inventory_count",
    value=42,  # Can be int or string
    metafield_type="number_integer"
)
```

### JSON Metafields

```python
json_data = {"tags": ["tag1", "tag2"], "metadata": {"key": "value"}}

result = writer.write_product_metafield(
    product_id="gid://shopify/Product/123",
    namespace="custom",
    key="json_data",
    value=json_data,
    metafield_type="json"
)
```

### List Metafields

```python
# List of text
result = writer.write_product_metafield(
    product_id="gid://shopify/Product/123",
    namespace="custom",
    key="tags",
    value=["tag1", "tag2", "tag3"],
    metafield_type="list.single_line_text_field"
)
```

## Supported Metafield Types

The writer handles transformation for:

- **Text types**: `single_line_text_field`, `multi_line_text_field`
- **Numbers**: `number_integer`, `number_decimal`
- **JSON**: `json` (dict/list → JSON string)
- **Boolean**: `boolean`
- **Lists**: `list.single_line_text_field`, `list.number_integer`, etc.
- **References**: `product_reference`, `variant_reference`, `page_reference`
- **Dates**: `date`, `date_time`
- **Complex**: `dimension`, `volume`, `weight`

## How It Works

1. **Type Detection**: Writer checks metafield definition or existing metafield to determine type
2. **Value Transformation**: `MetafieldTypeTransformer` converts values to correct format
   - Numbers → string representation
   - Lists → JSON array string
   - JSON → JSON string
   - All values → strings (Shopify requirement)
3. **Safe Write**: GraphQL mutation with proper type and transformed value

## Testing

Run validation tests:

```bash
python test_fix.py
```

Run example usage:

```bash
python example_usage.py
```

## Key Features

- ✅ **Automatic type detection** from metafield definitions
- ✅ **Type transformation** for all common metafield types
- ✅ **Error handling** with clear messages
- ✅ **Retry logic** for transient API errors
- ✅ **Definition caching** to reduce API calls

## Common Issues Fixed

1. **"value is invalid"**: Fixed by transforming values to correct format
2. **"type mismatch"**: Fixed by detecting and using correct type from definition
3. **"metafield definition not found"**: Handled gracefully with explicit type fallback

## API Version

Uses Shopify Admin API GraphQL (2024-10 recommended). For API versions 2021-07+, uses `type` field (not deprecated `valueType`).

## Project Structure

```
shopify-metafield-fix/
├── shopify_client.py          # Shopify API client wrapper
├── metafield_writer.py        # Safe metafield writer with validation
├── example_usage.py           # Usage examples
├── test_fix.py                # Validation tests
├── requirements.txt           # Dependencies
└── README.md                  # This file
```
