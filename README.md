# StayNest: Hotel Booking Analytics

End-to-end analytics project on a simulated hotel-booking business (fictional data).
Python (data generation) > MySQL (analysis) > Power BI (dashboard).

```
data/       customers, rooms, bookings, payments CSVs
python/     generate_data.py   (rerun to regenerate; seed fixed)

docs/       POWERBI_BUILD_GUIDE.md
```

Dataset: ~4.9K customers, 100 rooms, 25K bookings, ~24K payments, Jan 2025 to Dec 2026.
Revenue = Room_Rate x Nights x (1 - Discount); cancelled bookings are excluded from revenue.
