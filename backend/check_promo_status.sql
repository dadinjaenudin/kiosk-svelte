-- Quick SQL queries to check promo/popular data status
-- Run these in PostgreSQL to diagnose issues

-- 1. Check if columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'products_product' 
  AND column_name IN ('is_popular', 'has_promo', 'promo_price', 'tags');

-- Expected output: 4 rows with these columns

-- 2. Count products by status
SELECT 
    COUNT(*) as total_products,
    COUNT(CASE WHEN is_popular = true THEN 1 END) as popular_count,
    COUNT(CASE WHEN has_promo = true THEN 1 END) as promo_count,
    COUNT(CASE WHEN is_popular = true AND has_promo = true THEN 1 END) as popular_promo_count,
    COUNT(CASE WHEN is_available = true THEN 1 END) as available_count
FROM products_product;

-- Expected output:
-- total_products | popular_count | promo_count | popular_promo_count | available_count
-- ---------------|---------------|-------------|---------------------|----------------
-- 20+            | 8+            | 7+          | 4+                  | 18+

-- 3. List all promo products
SELECT 
    sku, 
    name, 
    price, 
    promo_price,
    is_popular,
    is_available,
    tags
FROM products_product
WHERE has_promo = true
ORDER BY sku;

-- Expected output: 7 products (AG-002, AG-005, SH-002, NP-002, NP-003, MA-002, BV-003)

-- 4. List all popular products
SELECT 
    sku, 
    name, 
    is_popular,
    has_promo,
    is_available
FROM products_product
WHERE is_popular = true
ORDER BY sku;

-- Expected output: 8+ products

-- 5. List popular + promo products (best combo!)
SELECT 
    sku, 
    name, 
    price, 
    promo_price,
    ROUND((price - promo_price) / price * 100, 0) as discount_percent
FROM products_product
WHERE is_popular = true AND has_promo = true
ORDER BY discount_percent DESC;

-- Expected output: 4 products (AG-002, SH-002, NP-003, MA-002)

-- 6. Check for products with missing data
SELECT 
    sku,
    name,
    CASE 
        WHEN is_popular IS NULL THEN 'is_popular is NULL'
        WHEN has_promo IS NULL THEN 'has_promo is NULL'
        WHEN has_promo = true AND promo_price IS NULL THEN 'promo_price missing'
        ELSE 'OK'
    END as status
FROM products_product
WHERE is_popular IS NULL 
   OR has_promo IS NULL 
   OR (has_promo = true AND promo_price IS NULL);

-- Expected output: No rows (empty result = all data is valid)

-- 7. Summary by tenant
SELECT 
    t.name as tenant_name,
    COUNT(*) as total_products,
    COUNT(CASE WHEN p.is_popular = true THEN 1 END) as popular,
    COUNT(CASE WHEN p.has_promo = true THEN 1 END) as promo
FROM products_product p
JOIN tenants_tenant t ON p.tenant_id = t.id
GROUP BY t.name
ORDER BY t.name;

-- Expected output: Multiple tenants with their product counts

-- 8. Find products that need seeding (no flags set)
SELECT 
    sku,
    name,
    is_popular,
    has_promo,
    is_available
FROM products_product
WHERE is_popular = false 
  AND has_promo = false
ORDER BY sku;

-- These are products that are not marked as special (normal products)

-- 9. Verify specific SKUs from seed command
SELECT 
    sku,
    name,
    is_popular,
    has_promo,
    promo_price,
    is_available
FROM products_product
WHERE sku IN (
    'AG-002',  -- Should be: popular=true, promo=true, promo_price=38000
    'SH-002',  -- Should be: popular=true, promo=true, promo_price=27000
    'NP-003',  -- Should be: popular=true, promo=true, promo_price=38000
    'MA-002'   -- Should be: popular=true, promo=true, promo_price=18000
)
ORDER BY sku;

-- Expected: 4 rows with all flags set correctly

-- 10. Check tags
SELECT 
    sku,
    name,
    tags
FROM products_product
WHERE tags IS NOT NULL AND tags != ''
LIMIT 10;

-- Expected: Products with comma-separated tags
