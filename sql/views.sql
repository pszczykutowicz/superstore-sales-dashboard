-- =============================================================================
-- Superstore Sales Analytics
-- Widoki SQL dla Power BI Dashboard
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. vw_sales_summary
--    Agregacja sprzedazy po miesiacu, regionie, kategorii i segmencie
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_sales_summary AS
SELECT
    YEAR(order_date)                 AS `year`,
    MONTH(order_date)                AS `month`,
    region,
    category,
    sub_category,
    segment,
    COUNT(DISTINCT order_id)         AS orders_count,
    COUNT(*)                         AS order_lines,
    ROUND(SUM(sales), 2)             AS total_sales
FROM orders
GROUP BY
    YEAR(order_date),
    MONTH(order_date),
    region,
    category,
    sub_category,
    segment;


-- -----------------------------------------------------------------------------
-- 2. vw_products
--    Agregacja sprzedazy po produkcie z mozliwoscia filtrowania po roku i regionie
--    Uzywany na stronie "Top 10 Products"
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_products AS
SELECT
    YEAR(order_date)                  AS `year`,
    region,
    category,
    sub_category,
    product_name,
    ROUND(SUM(sales), 2)              AS total_sales,
    COUNT(DISTINCT order_id)          AS orders_count,
    COUNT(DISTINCT customer_id)       AS customers_count
FROM orders
GROUP BY
    YEAR(order_date),
    region,
    category,
    sub_category,
    product_name;


-- -----------------------------------------------------------------------------
-- 3. vw_segments
--    Agregacja sprzedazy po segmencie klienta z order_id i customer_id
--    do poprawnego liczenia unikalnych zamowien i klientow przez DAX
--    Uzywany na stronie "Customer Segments"
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_segments AS
SELECT
    YEAR(order_date)                                    AS `year`,
    MONTH(order_date)                                   AS `month`,
    region,
    segment,
    category,
    order_id,
    customer_id,
    ROUND(SUM(sales), 2)                                AS total_sales
FROM orders
GROUP BY
    YEAR(order_date),
    MONTH(order_date),
    region,
    segment,
    category,
    order_id,
    customer_id;

