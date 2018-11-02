"""Library for interacting with ClearBooks."""

from datetime import date, timedelta
from io import StringIO
import logging
import os
import sys
from typing import List

import pandas as pd
import requests

__version__ = '0.0.2'

TIMEOUT = 20  # seconds
DATE_FORMAT = '%d/%m/%Y'
"""Date format DD/MM/YYYY accepted by ClearBooks URLs"""

HOURS_PER_DAY = 8  # hours per working day
CB_START_DATE = date(2013, 1, 1)
ONE_YEAR = timedelta(days=365)
CB_DOMAIN = 'https://secure.clearbooks.co.uk/'
LOGIN_URL = CB_DOMAIN + 'account/action/login/'
LOGIN_FORM = CB_DOMAIN + 'account/action/login/cb'
TIMESHEET_URL = CB_DOMAIN + 'springboardproltd/accounting/timetracking/view/'
HOMEPAGE = CB_DOMAIN + 'springboardproltd/accounting/home/dashboard'


class Session:

    def __enter__(self):
        logger = logging.getLogger('clearbooks.Session.__enter__')

        post_data = {}

        try:
            post_data['email'] = os.environ['CB_USER']
            post_data['password'] = os.environ['CB_PASSWORD']

        except KeyError as ex:
            logger.error(f'Cannot log in. Please set the {ex} environment variable')
            raise

        # Start a HTTP session
        try:
            self._session = requests.Session().__enter__()

            # Log in to ClearBooks
            response = self._session.post(LOGIN_FORM, data=post_data, timeout=TIMEOUT)
            response.raise_for_status()

            if response.url == LOGIN_URL:
                msg = 'Incorrect username or password.'
                logger.error(msg)
                raise ValueError(msg)

            return self

        except Exception:
            self.__exit__(*sys.exec_info())

    def __exit__(self, *args, **kwargs) -> bool:
        return self._session.__exit__(*args, **kwargs)

    def get_timesheets(self,
                       from_: date=CB_START_DATE,
                       to: date=date.today(),
                       step: timedelta=ONE_YEAR) -> pd.DataFrame:
        """Download timesheets in chunks because there is a bug in ClearBooks
        where requests for large amounts of data get no respone.

        Perhaps the ClearBooks server times-out internally.
        A technique that seems to work is to get one year at a time.

        Add columns for Quarter and Working Days (sum of Days, Hours, Minutes).
        """
        dataframes: List[pd.DataFrame] = []

        while from_ <= to:
            target_end_date = from_ + step
            end_date = to if to <= target_end_date else target_end_date

            dataframes.append(_get_timesheet(self._session, from_, end_date))

            from_ = from_ + step + timedelta(days=1)

        timesheets = pd.concat(dataframes)

        # Change leading underscores to periods because matplotlib does not
        # plot variables with leading underscores
        timesheets.replace('^_', '.', regex=True, inplace=True)

        # Add column for Working Days booked
        timesheets['Working Days'] = timesheets['Days'] + \
            timesheets['Hours'] / HOURS_PER_DAY + \
            timesheets['Minutes'] / (HOURS_PER_DAY * 60)

        # Categorise each entry into its quarter.
        # Note that the quarter is financial (Q1 is Apr - Jun inclusive)
        # The year is the financial year ENDING so 2016Q1 means Apr - Jun 2015
        timesheets['Quarter'] = pd.PeriodIndex(timesheets['Datetime'], freq='Q-MAR')

        return timesheets


def get_timesheets(from_: date=CB_START_DATE,
                   to: date=date.today(),
                   step: timedelta=ONE_YEAR) -> pd.DataFrame:
    """Convenience function to get timesheets.

    If you want to download other data from ClearBooks on the same connection,
    use the `clearbooks.Session` context manager.
    """
    with Session() as session:
        return session.get_timesheets(from_, to, step)


def _get_timesheet(session: requests.Session,
                   from_: date,
                   to: date=date.today()) -> pd.DataFrame:
    """Download one CSV timesheet as a DataFrame.

    ClearBooks throws a HTTP 500 Server Error if a large amount of data is
    requested. Use Session.get_timesheets() instead.
    """

    logger = logging.getLogger('_get_timesheet')
    params = {'csv': '1'}
    params['from'] = from_.strftime(DATE_FORMAT)
    params['to'] = to.strftime(DATE_FORMAT)

    # ClearBooks needs at least one filter to be defined, otherwise it does
    # not return CSV data!
    params['filter[employee_id]'] = '*'

    # ClearBooks needs the filter-submit parameter set for some reason,
    # otherwise it throws a HTTP 500 Server Error!
    params['filter-submit'] = 'Find'

    logger.debug(f'Requesting timesheets from {from_} to {to}')
    response = session.get(TIMESHEET_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()

    if response.text:
        return pd.read_csv(StringIO(response.text), parse_dates={'Datetime': ['Date', 'Time']})

    else:
        logger.warning(f'No timesheets found between {from_} and {to}')
        return pd.DataFrame()
