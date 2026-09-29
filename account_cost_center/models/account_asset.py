# Copyright 2015-2020 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    cost_center_id = fields.Many2one("account.cost.center",  help="Default Cost Center",)