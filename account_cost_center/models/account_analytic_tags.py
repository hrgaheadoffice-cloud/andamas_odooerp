# Copyright 2015-2020 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountanalyticTagss(models.Model):
    _inherit = "account.account.tag"
    _description = "Account Cost Center Tags"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
