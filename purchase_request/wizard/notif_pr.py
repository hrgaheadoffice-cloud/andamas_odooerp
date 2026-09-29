# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class tbl_notif_pr(models.TransientModel):
    _name = "tbl_notif_pr"
    _description = "tbl_notif_pr"



    def _get_default_pr(self):
        return self.env['purchase.request.line'].browse(self.env.context.get('active_ids'))

    pr_id = fields.Many2one('purchase.request.line', string="PR", default=_get_default_pr, readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="pr_id.company_id",
        string="Company",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    estimated_cost = fields.Monetary(
        string="Sub Total",
        currency_field="currency_id",
        related='pr_id.estimated_cost')
    avail_budget = fields.Float(string="Est Avail Budget", related='pr_id.avail_budget')
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        related='pr_id.analytic_account_id'
    )
    notif = fields.Char(string="Notif",
     # compute="_compute_notif",
     )


    # def _compute_notif(self):
    #     for rec in self:
    #         if rec.avail_budget < rec.estimated_cost:
    #             rec.notif = "Budget OK"
    #         else:
    #             rec.notif = "Budget KUrang"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        mod = self.env['purchase.request.line'].browse(self.env.context.get('active_ids'))
        if mod.avail_budget < mod.estimated_cost:
            res["notif"] = "Estimasi Cost Lebih besar dari Budget"
        else:
            res["notif"] = "BUdget OK"


        return res






