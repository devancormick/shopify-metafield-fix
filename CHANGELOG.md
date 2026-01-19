# Changelog

## [1.1.0] - Enhanced Features

### Added
- **Batch Writer** (`batch_writer.py`): Write multiple metafields in a single API call
- **Logging System** (`logger.py`): Comprehensive logging for all metafield operations
- **Rate Limiter** (`rate_limiter.py`): Prevent 429 errors with intelligent rate limiting
- **Enhanced Error Handling**: Better error messages and context
- **Operation Logging**: Track all write attempts, successes, and failures

### Improved
- Better type transformation for edge cases
- More efficient API usage with batch operations
- Enhanced debugging capabilities with detailed logs

### Usage Examples

#### Batch Operations
```python
from batch_writer import BatchMetafieldWriter

writer = BatchMetafieldWriter(client)
result = writer.write_product_metafields_batch(
    product_id="gid://shopify/Product/123",
    metafields=[
        {"namespace": "custom", "key": "key1", "value": "value1"},
        {"namespace": "custom", "key": "key2", "value": 42, "type": "number_integer"}
    ]
)
```

#### With Logging
```python
from logger import setup_logger
from metafield_writer import SafeMetafieldWriter

logger = setup_logger(log_file="metafield_operations.log")
writer = SafeMetafieldWriter(client)
# Operations will be automatically logged
```

#### With Rate Limiting
```python
from rate_limiter import ShopifyRateLimiter
from shopify_client import ShopifyClient

rate_limiter = ShopifyRateLimiter(requests_per_second=2.0)

# Before each API call
rate_limiter.wait_if_needed()
client.graphql_request(...)
```

## [1.0.0] - Initial Release

### Features
- Safe metafield writer with type validation
- Automatic definition lookup
- Type transformation for all common metafield types
- Caching to reduce API calls
- Error handling with fallbacks
