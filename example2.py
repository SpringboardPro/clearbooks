"""Example program using the clearbooks module with an HTTP session."""

from datetime import date, timedelta

import clearbooks


def main():
    one_year_ago = date.today() - timedelta(days=365)

    # Show how to use a ClearBooks session so the HTTP session
    # stays open to allow multiple HTTP requests without
    # needing to log in each time
    with clearbooks.Session() as session:
        times = session.get_timesheets(from_=one_year_ago)

    # Print the top few rows of timesheet data
    print(times.head())
    print()

    # Print the data types
    print(times.dtypes)
    print()

    # Print the sum of days booked by employee, by quarter
    print(times.pivot_table(values='Working_Days',
                            index='Employee',
                            columns='Quarter',
                            aggfunc='sum'))


if __name__ == '__main__':
    main()
