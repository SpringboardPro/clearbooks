# clearbooks

Python library for interacting with ClearBooks.

## Authorisation

You will need some level of administrator permissions in ClearBooks for the
functions to work.  For example, you cannot query other peoples' timesheets
unless you have that permission in ClearBooks.  Contact your company's
ClearBooks administrator if you have any problems.

## Installation

1. Ideally, install the Anaconda Python distribution because it installs the required
   dependencies at the same time.  Ensure that you have Python 3.6+. You can then skip
   step 2.

2. If you do not want to install Anaconda for some reason, you can install 
   Python 3.6+ on its own and use `pip install` to install the following required packages:

   * `pandas`
   * `requests`

3. Either:
   1. Copy `clearbooks.py` to your working directory, OR
   2. Install from the repository using `pip install https://github.com/blokeley/clearbooks` (untested) OR
   3. Clone the repository using `git` then install from the local repo using `pip`.

## Use

1. For convenient repeated use, set the environment variables `CB_USER` and `CB_PASSWORD`
   to the username (normally the email address) and password of the account used to log
   in to ClearBooks.

2. See the files called `example_*.py` for examples of how to use `clearbooks.py`

## Development

* Use mypy and flake8 to check code quality.
* Use Python 3.6+

## TODO

- [x] Timesheets
- [x] Purchase Orders
- [x] Bills - paid bills on a project
- [ ] Invoices – what we have invoiced
