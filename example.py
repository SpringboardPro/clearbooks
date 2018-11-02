"""Example program using the clearbooks module."""

from datetime import date, timedelta

import clearbooks


def main():
    one_year_ago = date.today() - timedelta(days=365)

    with clearbooks.Session() as session:
        timesheets = session.get_timesheets(from_=one_year_ago)

    # Print the top few rows of timesheet data
    print(timesheets.head())
    print()

    # Print the total amount of time booked by employee
    print(timesheets.groupby('Employee')['Working Days'].sum().sort_values())


if __name__ == '__main__':
    main()
