import requests
import pandas as pd
from datetime import datetime, timedelta

# Function to fetch data for a specific date
def fetch_data_for_date(date):
    url = f"https://covid-api.com/api/reports?date={date}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        print(f"Failed to fetch data for {date}")
        return None

# Define the date range
start_date = datetime(2020, 3, 9).date()
end_date = datetime(2023, 3, 9).date()

# Fetch data for one day per month
all_data = []
current_date = start_date
while current_date <= end_date:
    print(f"Fetching data for {current_date}...")
    data = fetch_data_for_date(current_date.strftime("%Y-%m-%d"))
    if data:
        all_data.extend(data)
    
    # Move to the first day of the next month
    if current_date.month == 12:
        current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
    else:
        current_date = current_date.replace(month=current_date.month + 1, day=1)

# Convert the data to a DataFrame
df = pd.DataFrame(all_data)

# Save the DataFrame to a CSV file
df.to_csv("covid_data_monthly.csv", index=False)
print("Data saved to covid_data_monthly.csv")