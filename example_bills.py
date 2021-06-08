"""Example showing how to get Bills from ClearBooks."""

from datetime import date, timedelta

import clearbooks


from_ = date.today() - timedelta(weeks=4)
bills = clearbooks.get_bills(from_)

# Print the top few rows of the DataFrame
print(bills.head())

# Calculate the total VAT
print('Total VAT', bills['vat'].sum())
print()

# # Calculate the mean and median of net bill value
print('Averages for net values:')
print(bills['net'].agg(['mean', 'median']))
