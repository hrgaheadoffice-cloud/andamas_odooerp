# Copyright 2015-2020 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"


    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    description = fields.Text('Description')
    prepared_by = fields.Many2one(
        comodel_name="res.users",
        string="Prepared By",
        required=False,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
    prepare_dt = fields.Datetime('Prepare Datetime')
    verified_by = fields.Many2one(
        comodel_name="res.users",
        string="Verified By",
        track_visibility="onchange")
    verify_dt = fields.Datetime('Verify Datetime') 
    checked_by = fields.Many2one(
        comodel_name="res.users",
        string="Checked By",
        copy=False,
        track_visibility="onchange",
    )
    checked_dt = fields.Datetime('Checked Datetime')

    appr1 = fields.Many2one(
        comodel_name="res.users",
        string="Approved 1",
        copy=False,
        track_visibility="onchange",
    )
    appr1_dt = fields.Datetime('Appr1 Datetime')
    appr2 = fields.Many2one(
        comodel_name="res.users",
        string="Approved 2",
        copy=False,
        track_visibility="onchange",
    )
    appr2_dt = fields.Datetime('Appr2 Datetime')
    appr3 = fields.Many2one(
        comodel_name="res.users",
        string='Approved 3',
        copy=False,
        track_visibility="onchange",
    )
    appr3_dt = fields.Datetime('Appr3 Datetime')

    