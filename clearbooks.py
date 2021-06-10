"""Library for interacting with ClearBooks."""

from datetime import date, timedelta
from io import StringIO
import logging
import os
import sys
from typing import List

import pandas as pd
import requests

__version__ = '0.1.0'
__all__ = ['Session', 'get_bills', 'get_invoices', 'get_purchase_orders', 'get_timesheets']

TIMEOUT = 20  # seconds
DATE_FORMAT = '%d/%m/%Y'
"""Date format DD/MM/YYYY accepted by ClearBooks URLs"""

HOURS_PER_DAY = 8  # hours per working day
CB_START_DATE = date(2014, 1, 1)
ONE_YEAR = timedelta(days=365)
CB_DOMAIN = 'https://secure.clearbooks.co.uk/'
LOGIN_URL = CB_DOMAIN + 'account/action/login/'
LOGIN_FORM = CB_DOMAIN + 'account/action/login/cb'
REPORT_URL = CB_DOMAIN + 'springboardproltd/accounting/reports/export-csv/'
TIMESHEET_URL = CB_DOMAIN + 'springboardproltd/accounting/timetracking/view/'
HOMEPAGE = CB_DOMAIN + 'springboardproltd/accounting/home/dashboard'

BILL_COL_NAMES = ['clearbooks_id', 'prefix', 'number', 'accounting_date', 'reference',
                  'po_reference', 'transaction_id', 'invoice_date', 'invoice_due',
                  'description', 'company_name', 'net', 'vat', 'gross', 'status',
                  'project_name', 'outstanding', 'mc_net', 'mc_vat', 'mc_gross',
                  'currency_id', 'formatted_invoice_number', 'amount_credited',
                  'currency_code']

INVOICE_COL_NAMES = ['invoice_num', 'prefix', 'accounting_date', 'reference',
                     'transaction_id', 'invoice_date', 'invoice_due', 'description',
                     'company_name', 'net', 'vat', 'gross', 'status', 'project_name',
                     'outstanding', 'mc_net', 'mc_vat', 'mc_gross', 'currency_id',
                     'formatted_invoice_number', 'amount_credited', 'currency_code']

PO_COL_NAMES = ['clearbooks_id', 'prefix', 'accounting_date', 'reference', 'invoice_date',
                'description', 'company_name', 'net', 'vat', 'gross', 'status', 'project_name']


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
            # If there is an error logging in, exit the log-in
            self.__exit__(*sys.exec_info())

    def __exit__(self, exc_type, exc_value, traceback_) -> bool:
        # Exit the HTTP session
        return self._session.__exit__(exc_type, exc_value, traceback_)

    def get(self, *args, **kwargs):
        return self._session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._session.post(*args, **kwargs)


def get_bills(from_: date = CB_START_DATE,
              to: date = None) -> pd.DataFrame:
    """Return bills as pandas.DataFrame."""
    return _get_export('PURCHASES', from_, to, parse_dates=[3, 7, 8])


def get_invoices(from_: date = CB_START_DATE,
                 to: date = None) -> pd.DataFrame:
    """Return invoices as pandas.DataFrame."""
    return _get_export('SALES', from_, to, parse_dates=[2, 5, 6])


def get_purchase_orders(from_: date = CB_START_DATE,
                        to: date = None) -> pd.DataFrame:
    """Return Purchase Orders as pandas.DataFrame."""
    return _get_export('POS', from_, to, parse_dates=[2, 4])


def get_timesheets(from_: date = CB_START_DATE,
                   to: date = None,
                   step: timedelta = ONE_YEAR) -> pd.DataFrame:
    """Download timesheets in chunks because there is a bug in ClearBooks
    where requests for large amounts of data get no respone.

    Perhaps the ClearBooks server times-out internally.
    A technique that seems to work is to get one year at a time.

    Add columns for Quarter and Working Days (sum of Days, Hours, Minutes).
    """
    if to is None:
        to = date.today()

    _check_date_order(from_, to)

    dataframes: List[pd.DataFrame] = []

    with Session() as session:
        while from_ <= to:
            target_end_date = from_ + step
            end_date = to if to <= target_end_date else target_end_date

            dataframes.append(_get_timesheet(session, from_, end_date))

            from_ = from_ + step + timedelta(days=1)

    timesheets = pd.concat(dataframes)

    # Change leading underscores to periods because matplotlib does not
    # plot variables with leading underscores
    timesheets.replace('^_', '.', regex=True, inplace=True)

    # Add column for Working Days booked
    timesheets['Working_Days'] = timesheets['Days'] + \
        timesheets['Hours'] / HOURS_PER_DAY + \
        timesheets['Minutes'] / (HOURS_PER_DAY * 60)

    # Categorise each entry into its quarter.
    # Note that the quarter is financial (Q1 is Apr - Jun inclusive)
    # The year is the financial year ENDING so 2016Q1 means Apr - Jun 2015
    timesheets['Quarter'] = pd.PeriodIndex(timesheets['Datetime'], freq='Q-MAR')

    return timesheets


def _get_timesheet(session: requests.Session,
                   from_: date,
                   to: date = None) -> pd.DataFrame:
    """Download one CSV timesheet as a DataFrame.

    ClearBooks throws a HTTP 500 Server Error if a large amount of data is
    requested so client code should use get_timesheets().
    """

    logger = logging.getLogger('_get_timesheet')

    if to is None:
        to = date.today()

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
        return pd.read_csv(StringIO(response.text),
                           parse_dates={'Datetime': ['Date', 'Time']})

    else:
        logger.info(f'No timesheets found between {from_} and {to}')
        return pd.DataFrame()


def _check_date_order(from_, to) -> bool:
    """Check that from_ is not later than to.

    Returns: True if from_ is not later than to

    Raises: Value error if from_ is later than to
    """
    if from_ > to:
        raise ValueError(f'"to" ({to}) cannot be before "from" ({from_})')

    return True


def _get_export(export_type, from_: date, to: date, parse_dates=None) -> pd.DataFrame:
    """Get export from ClearBooks.

    Returns: pandas.DataFrame of data exported from ClearBooks.  Run example_*.py to see the format

    Raises: ValueError for unrecognised export_type, or from_ later than to
    """
    logger = logging.getLogger(f'clearbooks.get_export({export_type})')

    if to is None:
        to = date.today()

    if parse_dates is None:
        parse_dates = []

    col_mapping = {
            'POS': PO_COL_NAMES,
            'SALES': INVOICE_COL_NAMES,
            'PURCHASES': BILL_COL_NAMES,
    }

    if export_type not in col_mapping:
        raise ValueError(f'Export type {export_type} must be one of {list(col_mapping.keys())}')

    _check_date_order(from_, to)

    params = {'report_type': export_type}
    params['q_from'] = from_.strftime(DATE_FORMAT)
    params['q_to'] = to.strftime(DATE_FORMAT)

    with Session() as session:
        response = session.post(REPORT_URL, params, timeout=TIMEOUT)

    response.raise_for_status()

    if response.text:
        return pd.read_csv(StringIO(response.text), parse_dates=parse_dates)

    else:
        logger.info(f'No {export_type} found between {from_} and {to}')
        return pd.DataFrame(columns=col_mapping[export_type])
