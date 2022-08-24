"""Example showing how to get Bills from ClearBooks."""

from datetime import date, timedelta

import clearbooks


from_ = date.today() - timedelta(weeks=52)
bills = clearbooks.get_transactions(from_)

bills = bills.loc[
    bills.payment_id.isna()].loc[
        ~bills.account_name.isin([
                'VAT control', 
                'VAT cash control', 
                'Trade creditors', 
                'Trade debtors'
        ])
    ].copy()

# Print the top few rows of the DataFrame
print(bills.amount[bills.entity_name == 'RS Components'].sum())

# Calculate the total VAT
print('Total VAT', bills['vat'].sum())
print()

# # Calculate the mean and median of net bill value
print('Averages for net values:')
print(bills['net'].agg(['mean', 'median']))
