# StayNest Power BI Build Guide

Requires Power BI Desktop (Windows). On a Mac: a Windows VM (Parallels trial / UTM) or a borrowed PC.
Everything you need is in this folder; the build takes about 2 to 3 hours.

## 1. Load data
Home > Get Data > Text/CSV. Load all four files from `data/`. In Power Query check types:
dates = Date, Discount = Decimal, Revenue/Amount/Room_Rate = Fixed decimal. Close & Apply.

## 2. Model (Model view)
| From (one) | To (many) |
|---|---|
| customers[Customer_ID] | bookings[Customer_ID] |
| rooms[Room_ID] | bookings[Room_ID] |
| bookings[Booking_ID] | payments[Booking_ID] |
| Calendar[Date] | bookings[Check_In] (active) |

All single direction. Then paste everything in `powerbi/measures.dax`.
View > Themes > Browse for themes > `StayNest_theme.json`.

## 3. Page 1: Executive Overview
- Cards (top row): Total Revenue, Total Bookings, Avg Booking Value, Occupancy Rate, Cancellation Rate, Avg Rating
- Line chart: Calendar[Year-Month] x Total Revenue
- Column chart: Calendar[Year-Month] x Total Bookings
- Bar: rooms[Room_Type] x Total Revenue
- Donut: bookings[Booking_Status] x Total Bookings
- Slicers: Year, Room_Type, City

## 4. Page 2: Customer Analytics
- Donut: customers[Customer_Type] x Total Customers
- Table: Top 10 customers (Customer_Name, City, Total Revenue, Valid Bookings); Filters > Top N
- Bar: customers[City] x Total Revenue
- Column: customers[Age Group] x Avg Booking Value
- Cards: Avg Spend per Customer, Repeat Customer %

## 5. Page 3: Room & Revenue
- Clustered bar: Room_Type x ADR and Avg Rating
- Column: Calendar[Month] x Room Nights Sold (demand by month, sort by Month No)
- Matrix: Room_Type (rows) x Calendar[Day Type] (columns), values Valid Bookings (weekday vs weekend)
- Table: Room_ID, Room_Type, Valid Bookings; sort ascending, Top N bottom 10 (low demand rooms)
- Cards: ADR, RevPAR, Avg Length of Stay

## 6. Page 4: Booking & Cancellation
- Bar: Booking_Channel x Cancellation Rate (sort descending)
- Column: Discount Band x Cancellation Rate
- Column: Lead Time Bucket x Cancellation Rate and Avg Lead Time card
- Donut: payments[Payment_Method] x Count of Payment_ID
- Line: Calendar[Year-Month] x Cancellation Rate
- Card: Lost Revenue

## 7. Finishing
- Sync Year/City/Room_Type slicers across pages (View > Sync slicers).
- Add page navigation buttons (Insert > Buttons > Navigator > Page navigator).
- Rename pages, align visuals using Format > Align, turn on gridlines in View.
- Save as `powerbi/StayNest_Analytics.pbix`, then screenshot each page to `reports/` for your README.

## 8. Insights to look for (check them against your own visuals)
1. Which channel has the highest cancellation rate? Expect OTA to be well above Website.
2. Does cancellation rise with discount band?
3. Which months are peak demand, and does ADR move with them?
4. Which room type has the highest revenue vs. the highest occupancy?
5. Do low-demand rooms cluster in one room type?
Write each as: finding, evidence (number), recommendation.
