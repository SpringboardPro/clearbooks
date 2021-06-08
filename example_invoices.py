"""Example showing how to get Invoices from ClearBooks."""

from datetime import date, timedelta

import clearbooks


from_ = date.today() - timedelta(weeks=4)
invoices = clearbooks.get_invoices(from_)

# Print the top few rows of the DataFrame
print(invoices.head())

# Calculate the total VAT
print('Total VAT', invoices['vat'].sum())
print()

# # Calculate the mean and median of net bill value
print('Averages for net values:')
print(invoices['net'].agg(['mean', 'median']))
