# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    subscription_period_date_format = fields.Char(
        string="Subscription period date format",
        config_parameter="subscription_oca.period_date_format",
        help="Babel date format used to display the billed period on the "
        "invoice line description, e.g. dd/MM/yyyy. Leave empty to format "
        "the dates according to the customer language.",
    )
