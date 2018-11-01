"""Library for interacting with ClearBooks."""

from datetime import date, timedelta
from io import StringIO
import logging
import os
from typing import List

import pandas as pd
import requests

__version__ = '0.0.1'

TIMEOUT = 20  # seconds
DATE_FORMAT = '%d/%m/%Y'
"""Date format DD/MM/YYYY accepted by ClearBooks URLs"""

HOURS_PER_DAY = 8  # hours per working day
CB_START_DATE = date(2013, 1, 1)
ONE_YEAR = timedelta(days=365)
LOGIN_URL = 'https://secure.clearbooks.co.uk/account/action/login/'
LOGIN_FORM = 'https://secure.clearbooks.co.uk/account/action/login/cb'
TIMESHEET_URL = 'https://secure.clearbooks.co.uk/springboardproltd/accounting/timetracking/view/'
HOMEPAGE = 'https://secure.clearbooks.co.uk/springboardproltd/accounting/home/dashboard'


class Session:

    def __enter__(self, username: str=None, password: str=None):
        logger = logging.getLogger('clearbooks.Session.__enter__')

        post_data = {}

        try:
            post_data['email'] = username or os.environ['CB_USER']
            post_data['password'] = password or os.environ['CB_PASSWORD']

        except KeyError as ex:
            logger.error(f'Cannot log in. Please set the {ex} environment variable')
            raise

        # Start a HTTP session
        self._session = requests.Session().__enter__()

        # Log in to ClearBooks
        response = self._session.post(LOGIN_URL, data=post_data, timeout=TIMEOUT)
        response.raise_for_status()

        if response.url == LOGIN_URL:
            msg = 'Incorrect username or password.'
            logger.error(msg)
            raise ValueError(msg)

        return self

    def __exit__(self, *args, **kwargs):
        self._session.__exit__(*args, **kwargs)

    def get_timesheets(self,
                       from_: date=CB_START_DATE,
                       to: date=date.today(),
                       step: timedelta=ONE_YEAR) -> pd.DataFrame:
        """Download timesheets in chunks because there is a bug in ClearBooks
        where requests for large amounts of data get no respone.

        Perhaps the ClearBooks server times-out internally.
        A technique that seems to work is to get one year at a time.
        """
        dataframes: List[pd.DataFrame] = []

        while from_ <= to:
            target_end_date = from_ + step
            end_date = to if to <= target_end_date else target_end_date

            dataframes.append(_get_timesheet(self._session, from_, end_date))

            from_ = from_ + step + timedelta(days=1)

        timesheets = pd.concat(dataframes)

        # Add column for Working Days booked
        timesheets['Working Days'] = timesheets['Days'] + \
            timesheets['Hours'] / HOURS_PER_DAY + \
            timesheets['Minutes'] / (HOURS_PER_DAY * 60)

        return timesheets


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

    logger.debug('Requesting timesheets from {} to {}'.format(from_, to))
    response = session.get(TIMESHEET_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()

    return pd.read_csv(StringIO(response.text))
