# Superstore Sales Dashboard

End-to-end analytics project built on a global retail dataset.
Raw transactional data is ingested via a Python ETL pipeline, stored in MySQL
with a clean analytical layer of SQL views, and visualized in a fully interactive
Power BI dashboard with advanced DAX measures.

---

## Highlights

- End-to-end data pipeline: Python → MySQL → Power BI
- Star-schema-like model built using SQL views and DAX dimension tables
- Advanced DAX measures: YoY, YTD, dynamic context handling, dynamic titles
- Fully interactive 4-page dashboard with cross-page slicer consistency
- Time intelligence without native Power BI date tables — solved via SUMX + FILTER + IN VALUES pattern

---

## Stack

| Layer | Technology |
|---|---|
| Source data | Kaggle — Superstore Sales Dataset (9 800 rows, 2015–2018) |
| ETL | Python 3 (pandas, SQLAlchemy, pymysql) |
| Database | MySQL 8 via XAMPP |
| Analytical layer | SQL Views |
| Visualization | Power BI Desktop |

---

## Architecture

```
superstore_orders.csv
    │
    ▼
Python ETL (etl_superstore.py)
    │   - robust CSV ingestion with automatic encoding detection
    │   - data cleaning and normalization (column standardization, type casting)
    │   - date parsing from DD/MM/YYYY format
    │   - idempotent load into MySQL (replace strategy)
    │   - separation of raw ingestion logic from transformation
    ▼
MySQL — superstore_db
    │
    ├── orders              raw fact table, 9 800 rows
    ├── vw_sales_summary    aggregated by month / region / category / segment
    ├── vw_products         aggregated by product, year and region
    └── vw_segments         aggregated by segment with order_id and customer_id
    │                       for correct distinct counts in DAX
    ▼
Power BI
    ├── Dimension tables (DAX): dim_date, dim_year,
    │                           dim_region, dim_category, dim_segment
    ├── 15+ DAX measures (YoY, YTD, dynamic titles, best month, avg order value)
    └── 4-page interactive dashboard
```

---

## Business Insights

- **West region** generated the highest total revenue across all four years
- **Technology** category drives the largest share of sales (~37%), followed closely by Furniture and Office Supplies — revenue is distributed relatively evenly across categories
- **Consumer segment** dominates by volume (50% of sales), but **Corporate** shows a comparable average order value — they buy less often but spend more per transaction
- **Strong Q4 seasonality** is visible across all segments, with November consistently being the peak month
- **YoY growth of 30.6% in 2017 vs 2016** — the strongest growth year in the dataset
- **Home Office** is the smallest segment but shows consistent presence — potential growth opportunity

---

## SQL Layer

Views encapsulate all aggregation logic, keeping Power BI queries clean and fast.
Example — monthly sales summary view:

```sql
CREATE OR REPLACE VIEW vw_sales_summary AS
SELECT
    YEAR(order_date)             AS `year`,
    MONTH(order_date)            AS `month`,
    region,
    category,
    sub_category,
    segment,
    COUNT(DISTINCT order_id)     AS orders_count,
    COUNT(*)                     AS order_lines,
    ROUND(SUM(sales), 2)         AS total_sales
FROM orders
GROUP BY
    YEAR(order_date),
    MONTH(order_date),
    region,
    category,
    sub_category,
    segment;
```

---

## Dashboard Pages

### Page 1 — Total Sales Overview
High-level summary of business performance across all dimensions.
- KPI cards: Total Sales, Total Orders, Total Customers
- Line chart: monthly sales trend
- Bar chart: sales by region
- Donut chart: sales split by category
- Slicers: Year, Region, Category, Segment

### Page 2 — Top 10 Products
Product-level analysis focused on best performing items.
- KPI cards: Top 10 Sales, Top 10 Orders, Top 10 Customers — all scoped to Top 10 context via visual-level Top N filters
- Bar chart: Top 10 Products by Sales with category color coding
- Bar chart: Sales by Sub-Category with category breakdown
- Slicers: Year, Region, Category, Sub-Category

### Page 3 — Customer Segments
Comparison of Consumer, Corporate and Home Office segments.
- KPI cards: Total Sales, Total Orders (distinct), Total Customers (distinct)
- Donut chart: segment share of total sales
- Bar chart: total sales value per segment
- Bar chart: average order value per segment
- Line chart: monthly sales trend split by segment
- Slicers: Year, Region, Category, Segment

### Page 4 — YoY Analysis
Year-over-year and year-to-date comparison with full slicer interactivity.
- KPI cards: Sales Current Year, Sales Last Year, Sales YoY %, Best Month, Avg Monthly Sales
- Line chart: monthly sales current year vs last year
- Line chart: YTD cumulative current year vs last year
- Table: month-by-month breakdown with YoY % per month
- All titles update dynamically based on selected year
- When no year is selected, dashboard automatically defaults to the most recent year
- Slicers: Year, Region, Category, Segment

---

## Key DAX Patterns

### Dynamic year selection
Works correctly with both a specific year selected and the "All" slicer option.

```dax
Selected Year =
IF(
    ISFILTERED(dim_year[year]),
    SELECTEDVALUE(dim_year[year]),
    MAXX(ALL(orders), YEAR(orders[order_date]))
)
```

### YoY — Last Year Sales respecting all slicer filters
The core challenge: `ALL(orders)` removes filters propagated from dimension tables
through relationships. Solution: SUMX + FILTER + IN VALUES preserves slicer context
while overriding only the year filter.

```dax
Sales LY Total =
VAR SelectedYear = [Selected Year]
RETURN
SUMX(
    FILTER(
        ALL(orders),
        orders[year] = SelectedYear - 1 &&
        orders[category] IN VALUES(dim_category[category]) &&
        orders[region] IN VALUES(dim_region[region]) &&
        orders[segment] IN VALUES(dim_segment[segment])
    ),
    orders[sales]
)
```

### YTD cumulative with slicer support

```dax
Sales YTD Current =
VAR SelectedYear = [Selected Year]
VAR CurrentMonth = MAX(dim_date[Month])
RETURN
SUMX(
    FILTER(
        ALL(orders),
        orders[year] = SelectedYear &&
        orders[month] <= CurrentMonth &&
        orders[category] IN VALUES(dim_category[category]) &&
        orders[region] IN VALUES(dim_region[region]) &&
        orders[segment] IN VALUES(dim_segment[segment])
    ),
    orders[sales]
)
```

### Dynamic titles

```dax
Title Sales Current =
VAR SelectedYear = [Selected Year]
RETURN "Sales " & SelectedYear
```

---

## How to Run

### Prerequisites
- Python 3.x
- XAMPP with MySQL running on port 3306
- Power BI Desktop
- MySQL ODBC Connector 9.7 (download from dev.mysql.com)

### 1. Install Python dependencies
```bash
pip install pandas sqlalchemy pymysql
```

### 2. Set up the database
In phpMyAdmin create database `superstore_db` and a user with full privileges.

### 3. Run ETL
Update credentials at the top of the script and run:
```bash
python etl_superstore.py
```

### 4. Create SQL views
Open phpMyAdmin, select `superstore_db`, go to SQL tab and run `sql/views.sql`.

### 5. Connect Power BI
Use Get Data → ODBC with the following connection string:
```
Driver={MySQL ODBC 9.7 Unicode Driver};Server=127.0.0.1;Port=3306;Database=superstore_db;
```
Load: `orders`, `vw_sales_summary`, `vw_products`, `vw_segments`.

---

## Project Structure

```
superstore-sales-dashboard/
├── README.md
├── etl_superstore.py
├── sql/
│   └── views.sql
└── screenshots/
    ├── page1_overview.png
    ├── page2_products.png
    ├── page3_segments.png
    └── page4_yoy.png
```

---

## Dataset Notes

The Superstore dataset is synthetic. Each order line represents a unique
customer-product transaction. This is a characteristic of the dataset, not a data quality issue —
and it was identified and documented during exploratory analysis.

---

## Author

Piotr — Data Analyst  
Stack: Python · SQL · Power BI · MySQL
