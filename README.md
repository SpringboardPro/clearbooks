# clearbooks

Python library for interacting with ClearBooks.

## Installation

1. Ideally, install the Anaconda Python distribution because it installs the required
   dependencies at the same time.  Ensure that you have Python 3.6+. You can then skip
   step 2.

2. If you do not want to install Anaconda for some reason, you can install 
   Python 3.6+ on its own and use `pip install` to install the following required packages:

   * `pandas`
   * `reqests`

3. Copy `clearbooks.py` to your working directory, or clone using `git` then install using `pip`.

## Use

1. For convenient repeated use, set the environment variables `CB_USER` and `CB_PASSWORD`
   to the username (normally the email address) and password of the account used to log
   in to ClearBooks.

2. See the files called `example_*.py` for examples of how to use `clearbooks.py`

## Development

* Use mypy and flake8 to check code quality.
* Use Python 3.6+

## TODO

- [x] time sheets
- [x] Purchase Orders
- [ ] Bills - paid bills on a project
- [ ] Invoices – what we have invoiced
