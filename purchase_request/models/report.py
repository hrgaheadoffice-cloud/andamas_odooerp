from odoo import _, api, fields, models
from odoo.exceptions import UserError

# _STATES = [
#     ("draft", "Draft"),
#     ("done", "Done"),
# ]
_STATES = [
    ("draft", "Draft"),
    ("to_request_approve", "Tobe Approve Request"),
    ("to_recommend", "Tobe Recommend"),
    ("to_check", "Tobe Check"),
    ("to_verify", "Tobe Verify"), 
    ("to_approve", "Tobe Apprvd Head Dept"),   
    ("to_approve1", "Tobe Apprvd Mtrx2"),
    ("to_approve2", "Tobe Apprvd Mtrx3"),
    ("to_approve3", "Tobe Apprvd Mtrx4"),
    ("to_approve4", "Tobe Apprvd Mtrx5"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("cancel", "Canceled"),
    ("done", "Done"),
]

class tbl_pr_analisis(models.Model):
    _name = "tbl_pr_analisis"
    _description = "PR Analisis"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    # _rec_name = "pr_id"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,
        track_visibility="onchange",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    # state = fields.Selection(
    #     selection=_STATES,
    #     string="Status",
    #     index=True,
    #     track_visibility="onchange",
    #     required=True,
    #     copy=False,
    #     default="draft",
    # )
# ========================================PR========================================================
    name = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        copy=False,
        required=True,
        track_visibility="onchange",
        domain=lambda self: [
            (
                "state",
                "=",
                'approved',
            )
        ]
    )
    state_pr = fields.Selection(
        selection=_STATES,
        string="Status PR",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    prepared_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested By",
        required=True,
        copy=False,
        track_visibility="onchange",
        index=True,
    )
    fully_approved_date = fields.Datetime('Fully Approved Date')
    procurement_officer = fields.Many2one('res.users', 'Procurement Officer',track_visibility="onchange")
    alasan_reject = fields.Text(
        string="Reason for Rejection",
        track_visibility="onchange"
    )
    alasan_cancel = fields.Text(
        string="Reason for Cancel",
        track_visibility="onchange"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        track_visibility="onchange",
    )
    product_qty = fields.Float(
        string="PR Qty", track_visibility="onchange", digits="Product Unit of Measure"
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM PR",
        track_visibility="onchange",
    )

# =======================================RFQ/PO================================================================

    no_rfq = fields.Char(string='RFQ No')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    status_rfq = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ], string='Status RFQ',  copy=False, index=True, default='draft')
    product_qty_rfq = fields.Float(string='Quoted Qty', digits='Product Unit of Measure', required=True)
    product_uom_rfq = fields.Many2one('uom.uom', string='Quoted UoM')
    price_unit_rfq = fields.Float(string='Quoted Price', required=True, digits='Product Price')
    discount_rfq = fields.Float(string="Quoted Discount (%)", digits="Discount")
    net_price_rfq = fields.Float(string='Net Price', required=True, digits='Product Price')
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    price_total_rfq = fields.Float(string='Quoted Total')

    qty_to_po = fields.Float(string='Qty to PO', digits='Product Unit of Measure', required=True)
    selection_user = fields.Many2one(
        comodel_name="res.users",
        string="Selection User"
    )
    selection_datetime = fields.Datetime('Select Date/Time')