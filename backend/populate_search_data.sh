#!/bin/bash

# Script to populate sample data for search features
# Run this after migrations are complete

echo "🔄 Populating sample data for search features..."

# Run SQL file in Docker container
docker-compose exec -T db psql -U postgres -d kiosk_pos << 'EOF'

-- First, add new columns if they don't exist
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_popular BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS has_promo BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS promo_price DECIMAL(10,2);

-- Now populate the data
\i /docker-entrypoint-initdb.d/sample_data_search.sql

EOF

echo "✅ Sample data populated successfully!"
echo ""
echo "📊 Summary:"
echo "   - Popular Items: 12 products (⭐)"
echo "   - Promo Items: 7 products (🔥)"
echo "   - Available: 18 products (✓)"
echo "   - Sold Out: 2 products"
echo ""
echo "🧪 Test the search features:"
echo "   1. Open http://localhost:5174/kiosk"
echo "   2. Try searching for 'nasi', 'ayam', 'pedas', etc."
echo "   3. Click [⭐ Populer] to show popular items"
echo "   4. Click [🔥 Promo] to show promo items"
echo "   5. Click [✓ Tersedia] to toggle availability filter"
