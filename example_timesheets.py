"""Example showing how to get timesheets from ClearBooks."""

from datetime import date, timedelta

import clearbooks


one_year_ago = date.today() - timedelta(days=365)

times = clearbooks.get_timesheets(from_=one_year_ago)

# Print the top few rows of timesheet data
print(times.head())
print()

# Print the data types
print(times.dtypes)
print()

# Print the total amount of time booked by employee
print(times.groupby('Employee')['Working_Days'].sum().sort_values())
