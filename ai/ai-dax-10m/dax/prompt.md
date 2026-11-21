You are helping a Power BI developer. Write DAX measures for this semantic model. Answer with one DAX code block only: a DEFINE block with one MEASURE line per measure, using exactly the measure names given. No explanation.

Model (Import mode, Power BI):
- Sales (one row per order line): 'Order Number', 'Line Number', 'Order Date', 'Delivery Date', CustomerKey, StoreKey, ProductKey, Quantity, 'Unit Price', 'Net Price', 'Unit Cost', 'Currency Code', 'Exchange Rate'
- Customer: CustomerKey, Name, Country, Continent, ... (one row per customer)
- Product: ProductKey, 'Product Name', Brand, Category, Subcategory, ...
- Store: StoreKey, Country, Name, ...
- 'Date': Date, Year, 'Year Month', Month, 'Month Number', 'Day of Week', 'Working Day' (marked as date table, one row per day)
- Relationships: Sales[CustomerKey] -> Customer, Sales[ProductKey] -> Product, Sales[StoreKey] -> Store, Sales[Order Date] -> 'Date'[Date] (active), Sales[Delivery Date] -> 'Date'[Date] (inactive)
- Existing measures: [Sales Amount] = SUMX ( Sales, Sales[Quantity] * Sales[Net Price] ), [# Customers] = DISTINCTCOUNT ( Sales[CustomerKey] ), [# Orders] = DISTINCTCOUNT ( Sales[Order Number] )

Measures to write (table Sales):
1. Sales LY: Sales Amount for the same period last year.
2. Sales YTD: Sales Amount from the start of the year to the end of the selected period.
3. # New Customers: customers whose first purchase ever happened in the selected period.
4. Sales Growth %: growth of Sales Amount compared with the same period last year, as a percentage.
5. Avg Delivery Days: average number of days between order date and delivery date, per order.
6. # Returning Customers: customers who bought in the selected period and had also bought at any time before it.
7. Category Share %: share of the selected category in the sales of all categories, keeping every other filter.
8. Sales 30D Avg: average daily Sales Amount over the 30 days ending on the last date of the selected period.
