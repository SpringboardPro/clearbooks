"""Example showing how to get timesheets from ClearBooks."""

from datetime import date, timedelta
import logging

import clearbooks

logging.basicConfig(level=logging.DEBUG)

one_year_ago = date.today() - timedelta(days=365)

times = clearbooks.get_timesheets(from_=one_year_ago)

# Print the top few rows of timesheet data
print(times.loc[times['Days'] != 0])
print()

# Print the data types
print(times.dtypes)
print()

# Print the total amount of time booked by employee
print(times.groupby('Employee')['Hours_Booked'].sum().sort_values())
