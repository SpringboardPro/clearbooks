"""Unit tests for clearbooks module."""

from datetime import date
import unittest

import pandas as pd

import clearbooks

SKIP_SLOW_TESTS = False


class TestGetBills(unittest.TestCase):

    @unittest.skipIf(SKIP_SLOW_TESTS, 'Slow test')
    def test_bills(self):
        from_ = date(2021, 4, 1)
        to = date(2021, 4, 30)
        bills = clearbooks.get_bills(from_, to)
        self.assertEqual(bills.shape, (285, 24))

    @unittest.skipIf(SKIP_SLOW_TESTS, 'Slow test')
    def test_no_bills(self):
        from_ = date(2020, 12, 26)
        to = date(2020, 12, 26)
        bills = clearbooks.get_bills(from_, to)

        expected = pd.DataFrame(columns=clearbooks.BILL_COL_NAMES)

        pd.testing.assert_frame_equal(bills, expected)


class TestGetInvoices(unittest.TestCase):

    @unittest.skipIf(SKIP_SLOW_TESTS, 'Slow test')
    def test_invoices(self):
        from_ = date(2021, 4, 1)
        to = date(2021, 4, 30)
        bills = clearbooks.get_invoices(from_, to)
        self.assertEqual(bills.shape, (15, 22))

    @unittest.skipIf(SKIP_SLOW_TESTS, 'Slow test')
    def test_no_invoices(self):
        from_ = date(2020, 12, 26)
        to = date(2020, 12, 26)
        invoices = clearbooks.get_invoices(from_, to)

        expected = pd.DataFrame(columns=clearbooks.INVOICE_COL_NAMES)

        pd.testing.assert_frame_equal(invoices, expected)


class TestGetPurchaseOrders(unittest.TestCase):

    @unittest.skipIf(SKIP_SLOW_TESTS, 'Slow test')
    def test_get_some(self):
        from_ = date(2021, 4, 1)
        to = date(2021, 4, 30)
        pos = clearbooks.get_purchase_orders(from_, to)
        self.assertEqual(pos.shape, (129, 12))

    @unittest.skipIf(SKIP_SLOW_TESTS, 'Slow test')
    def test_get_none(self):
        from_ = date(2020, 12, 25)
        to = date(2020, 12, 25)
        pos = clearbooks.get_purchase_orders(from_, to)

        expected = pd.DataFrame(columns=clearbooks.PO_COL_NAMES)

        pd.testing.assert_frame_equal(pos, expected)


class TestCheckDateOrder(unittest.TestCase):

    def setUp(self) -> None:
        self.to = date(2021, 10, 24)

    def test_to_after_from(self):
        from_ = date(2021, 10, 23)
        self.assertTrue(clearbooks._check_date_order(from_, self.to))

    def test_to_equals_from(self):
        self.assertTrue(clearbooks._check_date_order(self.to, self.to))

    def test_from_after_to(self):
        from_ = date(2021, 10, 25)

        with self.assertRaises(ValueError):
            clearbooks._check_date_order(from_, self.to)


if __name__ == '__main__':
    unittest.main()
