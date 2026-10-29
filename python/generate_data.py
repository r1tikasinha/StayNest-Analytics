"""Generate the StayNest simulated dataset (fictional data) -> ../data/*.csv"""
import numpy as np, pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parent.parent / "data"
TODAY = pd.Timestamp("2026-10-29")
START, END = pd.Timestamp("2025-01-01"), pd.Timestamp("2026-12-31")
N_CUST, N_BOOK = 5000, 25000

# ---------- Rooms (100) ----------
rows = []
for floor in range(1, 11):
    rtype, cap, price = (("Standard", 2, 2500) if floor <= 4 else
                         ("Deluxe", 3, 4000) if floor <= 8 else ("Suite", 4, 7500))
    for n in range(1, 11):
        rows.append([floor*100+n, rtype, cap, price, floor,
                     rng.choice(["City", "Pool", "Garden"], p=[.45, .25, .30]), "Available"])
rooms = pd.DataFrame(rows, columns=["Room_ID","Room_Type","Capacity","Base_Price","Floor","View_Type","Room_Status"])
rooms.loc[rng.choice(len(rooms), 3, replace=False), "Room_Status"] = "Maintenance"

# ---------- Customers ----------
cities = {"Delhi":"Delhi","Mumbai":"Maharashtra","Bengaluru":"Karnataka","Hyderabad":"Telangana",
          "Chennai":"Tamil Nadu","Kolkata":"West Bengal","Pune":"Maharashtra","Jaipur":"Rajasthan",
          "Ahmedabad":"Gujarat","Lucknow":"Uttar Pradesh","Gurugram":"Haryana","Chandigarh":"Chandigarh"}
cw = np.array([.17,.15,.13,.09,.08,.06,.07,.05,.05,.04,.07,.04]); cw /= cw.sum()
first_f = ["Priya","Riya","Ananya","Sneha","Kavya","Neha","Pooja","Isha","Meera","Divya","Aditi","Simran"]
first_m = ["Aarav","Rohan","Arjun","Vikram","Karan","Rahul","Aman","Siddharth","Nikhil","Yash","Varun","Harsh"]
last = ["Sharma","Singh","Gupta","Verma","Patel","Reddy","Iyer","Nair","Mehta","Das","Khan","Joshi","Kapoor","Sinha"]
gender = rng.choice(["Male","Female","Other"], N_CUST, p=[.50,.48,.02])
names = [f"{rng.choice(first_m if g=='Male' else first_f)} {rng.choice(last)}" for g in gender]
city = rng.choice(list(cities), N_CUST, p=cw)
customers = pd.DataFrame({
    "Customer_ID": np.arange(1001, 1001+N_CUST), "Customer_Name": names,
    "Age": np.clip(rng.normal(34, 10, N_CUST).round(), 18, 70).astype(int),
    "Gender": gender, "City": city, "State": [cities[c] for c in city]})

# ---------- Bookings ----------
days = pd.date_range(START, END)
month_w = {1:1.3,2:1.2,3:.9,4:.9,5:1.2,6:1.2,7:.8,8:.8,9:.9,10:1.3,11:1.3,12:1.5}
dw = np.array([month_w[d.month] * (1.25 if d.dayofweek in (4,5) else 1.0) for d in days]); dw /= dw.sum()
check_in = pd.DatetimeIndex(rng.choice(days, N_BOOK, p=dw))
nights = rng.choice([1,2,3,4,5,6,7], N_BOOK, p=[.15,.30,.25,.14,.08,.05,.03])
lead = np.minimum(rng.gamma(2.0, 18, N_BOOK).astype(int), 150)
book_date = check_in - pd.to_timedelta(lead, unit="D")
late = book_date > TODAY
book_date = book_date.where(~late, TODAY - pd.to_timedelta(rng.integers(0, 30, N_BOOK), unit="D"))
book_date = pd.DatetimeIndex(np.maximum(book_date.values, np.datetime64(START)))
check_out = check_in + pd.to_timedelta(nights, unit="D")

active = rooms[rooms.Room_Status == "Available"].reset_index(drop=True)
pw = active.Room_Type.map({"Standard":1.0,"Deluxe":0.8,"Suite":0.45}).values; pw = pw / pw.sum()
rm = active.iloc[rng.choice(len(active), N_BOOK, p=pw)].reset_index(drop=True)

guests = np.array([rng.integers(1, c+1) for c in rm.Capacity])
channel = rng.choice(["Website","App","OTA","Walk-in"], N_BOOK, p=[.30,.25,.38,.07])
discount = rng.choice([0,.05,.10,.15,.20,.25], N_BOOK, p=[.30,.20,.20,.15,.10,.05])
season = np.array([month_w[d.month] for d in check_in])
weekend = np.array([1.12 if d.dayofweek in (4,5) else 1.0 for d in check_in])
rate = (rm.Base_Price.values * (0.9 + 0.2*season/1.5) * weekend * rng.normal(1, .03, N_BOOK)).round(-1)
revenue = (rate * nights * (1 - discount)).round(2)

p_c = pd.Series(channel).map({"Website":.10,"App":.16,"OTA":.27,"Walk-in":.03}).values
p_c = np.clip(p_c + discount*0.35 + np.minimum(lead, 90)/90*0.06, 0, .6)
cancelled = rng.random(N_BOOK) < p_c
status = np.where(cancelled, "Cancelled", np.where(check_out <= TODAY, "Completed", "Confirmed"))
span = np.maximum((check_in - book_date).days, 1)
cancel_date = pd.Series(book_date + pd.to_timedelta((rng.random(N_BOOK) * span).astype(int), unit="D"))
cancel_date = cancel_date.where(cancelled, pd.NaT)

rating = np.where(status == "Completed",
    np.clip(rng.normal(4.1, .6, N_BOOK) + rm.Room_Type.map({"Standard":-.1,"Deluxe":.05,"Suite":.2}).values
            + np.where(discount >= .2, -.1, 0), 1, 5).round(1), np.nan)

cust_w = rng.pareto(2.5, N_CUST) + 1; cust_w /= cust_w.sum()
bookings = pd.DataFrame({
    "Booking_ID": np.arange(100001, 100001+N_BOOK),
    "Customer_ID": rng.choice(customers.Customer_ID, N_BOOK, p=cust_w),
    "Room_ID": rm.Room_ID.values, "Booking_Date": book_date.date,
    "Check_In": check_in.date, "Check_Out": check_out.date, "Guests": guests,
    "Booking_Channel": channel, "Room_Rate": rate, "Discount": discount,
    "Booking_Status": status, "Cancellation_Date": cancel_date.dt.date,
    "Nights": nights, "Revenue": revenue, "Rating": rating})
bookings = bookings.sort_values("Booking_Date").reset_index(drop=True)

# ---------- Customer type + registration ----------
cnt = bookings.groupby("Customer_ID").size()
first = bookings.groupby("Customer_ID").Booking_Date.min()
customers = customers[customers.Customer_ID.isin(cnt.index)].copy()
customers["Customer_Type"] = np.where(customers.Customer_ID.map(cnt) >= 2, "Returning", "New")
customers["Registration_Date"] = [(pd.Timestamp(first[c]) - pd.Timedelta(days=int(rng.integers(0, 60)))).date()
                                  for c in customers.Customer_ID]

# ---------- Payments ----------
pay, pid = [], 500001
for b in bookings.itertuples():
    m = rng.choice(["UPI","Card","Net Banking","Cash"], p=[.45,.30,.15,.10])
    if b.Booking_Status == "Cancelled":
        if rng.random() < .85:
            pay.append([pid, b.Booking_ID, b.Booking_Date, m, b.Revenue, "Refunded"]); pid += 1
    else:
        paid = b.Booking_Status == "Completed" or rng.random() < .7
        pay.append([pid, b.Booking_ID, b.Booking_Date, m, b.Revenue, "Paid" if paid else "Pending"]); pid += 1
payments = pd.DataFrame(pay, columns=["Payment_ID","Booking_ID","Payment_Date","Payment_Method","Amount","Payment_Status"])

# ---------- Save ----------
customers[["Customer_ID","Customer_Name","Age","Gender","City","State","Customer_Type","Registration_Date"]] \
    .to_csv(OUT/"customers_cleaned.csv", index=False)
rooms.to_csv(OUT/"rooms_cleaned.csv", index=False)
bookings.to_csv(OUT/"bookings_cleaned.csv", index=False)
payments.to_csv(OUT/"payments_cleaned.csv", index=False)

ok = bookings[bookings.Booking_Status != "Cancelled"]
print(f"customers {len(customers):,} | rooms {len(rooms)} | bookings {len(bookings):,} | payments {len(payments):,}")
print(f"revenue (excl. cancelled): Rs {ok.Revenue.sum():,.0f} | avg booking: Rs {ok.Revenue.mean():,.0f}")
print("cancellation rate:", round((bookings.Booking_Status=='Cancelled').mean()*100,1), "%")
print(bookings.groupby("Booking_Channel").Booking_Status.apply(lambda s: round((s=='Cancelled').mean()*100,1)).to_dict())
print(bookings.Booking_Status.value_counts().to_dict())
print("orphan FKs:", (~bookings.Customer_ID.isin(customers.Customer_ID)).sum(), (~bookings.Room_ID.isin(rooms.Room_ID)).sum())
