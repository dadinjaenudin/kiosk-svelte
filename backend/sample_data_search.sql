-- Sample data untuk fitur search: is_popular, has_promo, is_available
-- Update products dengan flag yang berbeda-beda

-- ============================================
-- AYAM GEPREK MANTAP PRODUCTS
-- ============================================

-- Ayam Geprek Original (Popular + Available)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'pedas,ayam,geprek,populer'
WHERE sku = 'AG-001';

-- Ayam Geprek Keju (Popular + Promo)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = TRUE,
    promo_price = 38000,  -- Original: 42000
    is_available = TRUE,
    tags = 'pedas,ayam,geprek,keju,promo,populer'
WHERE sku = 'AG-002';

-- Ayam Geprek Sambal Matah (Available)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'pedas,ayam,geprek,sambal matah'
WHERE sku = 'AG-003';

-- Ayam Geprek Jumbo (Popular)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'pedas,ayam,geprek,jumbo,besar,populer'
WHERE sku = 'AG-004';

-- Ayam Geprek Mozarella (Promo)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = TRUE,
    promo_price = 43000,  -- Original: 48000
    is_available = TRUE,
    tags = 'pedas,ayam,geprek,keju,mozarella,promo'
WHERE sku = 'AG-005';

-- Ayam Geprek Pedas Gila (Popular + Not Available - Sold Out)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = FALSE, 
    is_available = FALSE,
    tags = 'pedas,ayam,geprek,extra pedas,sold out'
WHERE sku = 'AG-006';

-- ============================================
-- SOTO HOUSE PRODUCTS
-- ============================================

-- Soto Ayam (Popular + Available)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'soto,ayam,berkuah,hangat,populer'
WHERE sku = 'SH-001';

-- Soto Betawi (Popular + Promo)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = TRUE,
    promo_price = 27000,  -- Original: 32000
    is_available = TRUE,
    tags = 'soto,sapi,berkuah,betawi,promo,populer'
WHERE sku = 'SH-002';

-- Soto Kudus (Available)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'soto,ayam,berkuah,kudus'
WHERE sku = 'SH-003';

-- Soto Daging (Available)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'soto,sapi,daging,berkuah'
WHERE sku = 'SH-004';

-- ============================================
-- NASI PADANG SEDERHANA PRODUCTS
-- ============================================

-- Nasi Rendang (Popular + Available)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'nasi,rendang,padang,populer'
WHERE sku = 'NP-001';

-- Nasi Gulai Ayam (Promo)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = TRUE,
    promo_price = 22000,  -- Original: 28000
    is_available = TRUE,
    tags = 'nasi,gulai,ayam,padang,promo'
WHERE sku = 'NP-002';

-- Nasi Gulai Kambing (Popular + Promo)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = TRUE,
    promo_price = 38000,  -- Original: 45000
    is_available = TRUE,
    tags = 'nasi,gulai,kambing,padang,promo,populer'
WHERE sku = 'NP-003';

-- Nasi Dendeng Balado (Available)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'nasi,dendeng,balado,pedas,padang'
WHERE sku = 'NP-004';

-- Nasi Ayam Pop (Not Available - Sold Out)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = FALSE, 
    is_available = FALSE,
    tags = 'nasi,ayam,pop,padang,sold out'
WHERE sku = 'NP-005';

-- ============================================
-- MIE AYAM BAROKAH PRODUCTS
-- ============================================

-- Mie Ayam Original (Popular + Available)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'mie,ayam,bakso,populer'
WHERE sku = 'MA-001';

-- Mie Ayam Bakso (Popular + Promo)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = TRUE,
    promo_price = 18000,  -- Original: 22000
    is_available = TRUE,
    tags = 'mie,ayam,bakso,promo,populer'
WHERE sku = 'MA-002';

-- Mie Ayam Jumbo (Available)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'mie,ayam,jumbo,besar'
WHERE sku = 'MA-003';

-- Mie Ayam Pangsit (Available)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'mie,ayam,pangsit,wonton'
WHERE sku = 'MA-004';

-- ============================================
-- MINUMAN & DESSERT (Generic Tenant)
-- ============================================

-- Es Teh Manis (Popular + Available)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'minuman,es,teh,manis,populer'
WHERE sku = 'BV-001';

-- Es Jeruk (Available)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'minuman,es,jeruk,segar'
WHERE sku = 'BV-002';

-- Jus Alpukat (Promo)
UPDATE products 
SET is_popular = FALSE, 
    has_promo = TRUE,
    promo_price = 12000,  -- Original: 15000
    is_available = TRUE,
    tags = 'minuman,jus,alpukat,sehat,promo'
WHERE sku = 'BV-003';

-- Es Campur (Popular + Available)
UPDATE products 
SET is_popular = TRUE, 
    has_promo = FALSE, 
    is_available = TRUE,
    tags = 'dessert,es campur,manis,segar,populer'
WHERE sku = 'DS-001';

-- SUMMARY:
-- Popular Items: 9 products (AG-001, AG-002, AG-004, AG-006, SH-001, SH-002, NP-001, NP-003, MA-001, MA-002, BV-001, DS-001)
-- Promo Items: 6 products (AG-002, AG-005, SH-002, NP-002, NP-003, MA-002, BV-003)
-- Available: 18 products (all except AG-006 and NP-005)
-- Not Available (Sold Out): 2 products (AG-006, NP-005)
