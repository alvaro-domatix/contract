# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import fields
from odoo.tools.misc import format_date, get_lang

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionInvoicePeriod(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Invoice period partner"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Invoice period pricelist"}
        )
        cls.template_monthly = cls.env["sale.subscription.template"].create(
            {
                "name": "Monthly template",
                "code": "PER-MTH",
                "recurring_rule_type": "months",
                "recurring_rule_boundary": "unlimited",
            }
        )
        cls.product = cls._create_product(
            name="Period product",
            lst_price=100.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
        )
        cls.subscription = cls.env["sale.subscription"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
                "template_id": cls.template_monthly.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today(),
            }
        )
        cls.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": cls.subscription.id,
                "product_id": cls.product.id,
            }
        )

    def test_get_invoice_period_monthly_is_fixed_value(self):
        # Fixed calendar values computed by hand, not rebuilt from the model.
        self.subscription.recurring_next_date = date(2026, 1, 1)
        start, end = self.subscription._get_invoice_period()
        self.assertEqual(start, date(2026, 1, 1))
        self.assertEqual(end, date(2026, 1, 31))

    def test_get_invoice_period_weekly_is_fixed_value(self):
        # The period honours the template recurrence, not always months.
        self.template_monthly.recurring_rule_type = "weeks"
        self.subscription.recurring_next_date = date(2026, 1, 1)
        start, end = self.subscription._get_invoice_period()
        self.assertEqual(start, date(2026, 1, 1))
        self.assertEqual(end, date(2026, 1, 7))

    def test_manual_invoice_tracks_subscription_period(self):
        self.subscription.recurring_next_date = date(2026, 1, 1)
        invoice = self.subscription.create_invoice()
        for line in invoice.invoice_line_ids:
            self.assertEqual(line.subscription_id, self.subscription)
            self.assertEqual(line.subscription_period_start, date(2026, 1, 1))
            self.assertEqual(line.subscription_period_end, date(2026, 1, 31))

    def test_invoice_line_description_contains_period_dates(self):
        self.subscription.recurring_next_date = date(2026, 1, 1)
        invoice = self.subscription.create_invoice()
        line = invoice.invoice_line_ids[:1]
        lang_code = get_lang(self.env, self.partner.lang).code
        start_str = format_date(self.env, date(2026, 1, 1), lang_code=lang_code)
        end_str = format_date(self.env, date(2026, 1, 31), lang_code=lang_code)
        self.assertIn(f"({start_str} - {end_str})", line.name)
