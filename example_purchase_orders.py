"""Example showing how to get Purchase Orders from ClearBooks."""

from datetime import date, timedelta

import clearbooks


from_ = date.today() - timedelta(weeks=52)
orders = clearbooks.get_purchase_orders(from_)

# Print the top few rows of the DataFrame
print(orders[
    orders.company_name == 'RS Components'][
        orders.status == 'po_draft'].net.sum())

# Calculate the total VAT
print('Total VAT', orders['vat'].sum())

# Calculate the mean and median of net Purchase Order value
print('Averages for net values:')
print(orders['net'].agg(['mean', 'median']))
