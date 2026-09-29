import string
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("done", "Done"),
]
READONLY_STATES = {
        "done": [("readonly", True)],
    }
class tbl_quotation_selection(models.Model):
    _name = "tbl_quotation_selection"
    _description = "Quotation Selection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _rec_name = "pr_id"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    name = fields.Char(
        string="Nomor",
        # required=True,
        # default=_get_default_name,
        # default = 'New',
        readonly=True,
        track_visibility="onchange",
    )
    selection_user = fields.Many2one(
        comodel_name="res.users",
        string="Selection User",
        required=True,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
    selection_datetime = fields.Datetime('Select Date/Time')
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,
        track_visibility="onchange",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )

    pr_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        copy=False,
        required=True,
        states=READONLY_STATES,
        track_visibility="onchange",
        domain=lambda self: [
            (
                "state",
                "=",
                'approved',
            )
        ]
    )
    line_ids = fields.One2many(
        comodel_name="tbl_quotation_selection_line",
        inverse_name="quotation_id",
        string="RFQ",
        readonly=False,
        states=READONLY_STATES,
        copy=False,
        track_visibility="onchange",
    )
    
    def action_confirm(self):
        for rec in self:
            if rec.line_ids:
                select = self.mapped("line_ids.pilih")
                if True not in select:
                    raise UserError(
                            _("Please select at least one.")
                        )
                for line in rec.line_ids:
                    if line.pilih == True:
                        selection_line = self.env['tbl_quotation_selection_line'].search([('pilih', '=', True),
                                        ('quotation_id', '=', rec.id),('pr_line_id', '=', line.pr_line_id.id),
                                        ('product_add_id', '=', line.product_add_id.id)])
                        total_qty = sum(selection_line.mapped('product_qty'))
                        if line.pr_line_id:
                            if total_qty > (line.pr_line_id.product_qty - line.pr_line_id.purchased_qty_done):
                                raise UserError(_("Quantity to purchase exceeds PR Qty."))
                        if not line.price_unit or line.price_unit == 0:
                            raise UserError(_("Price unit must not be 0."))
                for line in rec.line_ids:
                    if line.pilih == True:
                        # line.name.button_confirm()
                        line.state = 'done'
                        line.po_line_id.product_qty = line.product_qty
                        line.po_line_id.price_unit = line.price_unit
                        line.po_line_id.discount = line.discount
                        line.po_line_id.taxes_id = line.taxes_id
                        line.po_line_id.show_in_po = True
                        if not line.pr_line_id:
                            po_lines = self.env['purchase.order.line'].create({
                                    "name": line.product_add_id.name,
                                    "order_id": line.name.id,
                                    "product_id": line.product_add_id.id,
                                    "product_uom": line.product_add_id.uom_po_id.id,
                                    "price_unit": line.price_unit,
                                    "product_qty": line.product_qty,
                                    "discount": line.discount,
                                    "taxes_id": line.taxes_id,
                                    'show_in_po' : True,
                                })
                    else:
                        line.state = 'cancel'
                        # line.po_line_id.unlink()

                    line.name.qs_id = rec.id
                    if line.name.rfq_line:
                            for rfq in line.name.rfq_line:
                                if rfq.po_line_id.id == line.po_line_id.id:
                                    rfq.product_qty = line.product_qty
                                    rfq.price_unit = line.price_unit
                                    rfq.discount = line.discount
                                    # rfq.harga_setelah_discount = line.harga_setelah_discount
                                    # rfq.price_total = line.price_total
                                    rfq.taxes_id = line.taxes_id
                                    rfq.state = line.state
                                    rfq.quotation_id = line.quotation_id.id
                
                for line in rec.line_ids:
                    if line.pilih == True:
                        cari = self.env['tbl_quotation_selection_line'].search([("quotation_id", "=", rec.id),("name", "=", line.name.id),("pilih", "=", False)])
                        if cari:
                            for detail in cari:
                                detail.po_line_id.unlink()
                        # line.name.button_confirm()
                        if line.name.state in ('draft','sent') :
                            line.name.update({'state': 'po_draft', 'status_rfq': 'done'})
                for line in rec.line_ids:
                    if line.pilih == False and line.po_line_id:
                        if line.name.state == 'draft':
                            line.name.button_cancel()


            rec.state = 'done'
            rec.selection_datetime = fields.Datetime.now()

    def action_get_data(self):
        lines = self.mapped("pr_id.line_ids.purchase_lines.order_id")
        for rec in self:
            qs_lain = self.env['tbl_quotation_selection'].search([("pr_id", "=", rec.pr_id.id),("id", "!=", rec.id),("state", "=", 'draft')])
            if qs_lain:
                raise UserError(
                            _("Purchase Request %s already has a quotation selection not Done")
                            % rec.pr_id.name
                        )
            if rec.line_ids:
                rec.line_ids.unlink()
            # cari = self.env['purchase.order'].search([("id", "in", lines.ids),("state", "=", 'draft')])
            # if cari:
            #     for po in cari:
            #         self.env['tbl_quotation_selection_line'].create({
            #                 'quotation_id' : rec.id,
            #                 'name' : po.id,
            #             })
            if rec.pr_id.line_ids:
                rfq = False
                for line in rec.pr_id.line_ids:
                    if line.purchase_lines.filtered(lambda x: x.state in ('draft','sent')):
                        for po_line in line.purchase_lines.filtered(lambda x: x.state in ('draft','sent')):
                            rfq = True
                            lines = self.env['tbl_quotation_selection_line'].create({
                                'quotation_id' : rec.id,
                                'pr_line_id' : line.id,
                                'name' : po_line.order_id.id,
                                'po_line_id' : po_line.id,
                                'product_qty' : po_line.product_qty,
                                'price_unit' : po_line.price_unit,
                                # 'diskon' : po_line.product_qty,
                                # 'harga_setelah_discount' : po_line.product_qty,
                                'price_total' : po_line.price_subtotal,
                                # 'taxes_id' : po_line.product_qty,
                            })
                            rfq_line = self.env['tbl_bisa_rfq_line'].search([('po_line_id', '=', po_line.id)], limit=1)
                            if rfq_line:
                                lines.product_qty = rfq_line.product_qty
                                lines.price_unit = rfq_line.price_unit
                                lines.discount = rfq_line.discount
                                lines.taxes_id = rfq_line.taxes_id
                                lines.product_add_id = rfq_line.product_add_id.id
                purchase = self.env['purchase.order'].search([('pr_id', '=', rec.pr_id.id),('state', 'in', ('draft','sent'))])
                if purchase:
                    for po in purchase:
                        if po.rfq_line:
                            for rfq_line in po.rfq_line:
                                if not rfq_line.pr_id:
                                    rfq = True
                                    lines = self.env['tbl_quotation_selection_line'].create({
                                        'quotation_id' : rec.id,
                                        'name' : po.id,
                                        'product_qty' : rfq_line.product_qty,
                                        'price_unit' : rfq_line.price_unit,
                                        'product_add_id' : rfq_line.product_add_id.id,
                                        'discount' : rfq_line.discount,
                                        'taxes_id' : rfq_line.taxes_id,
                                        'price_total' : rfq_line.price_total,
                                        'rfq_line_id' : rfq_line.id,
                                    })
                if rfq == False:
                    

                    # else:
                    #     # title = _("Warning for %s") % rec.pr_id.name
                    #     # # message = _("Purchase Request %s does not have a RFQ.") % rec.pr_id.name
                    #     # message = rec.pr_id.name
                    #     # warning = {
                    #     #         'title': title,
                    #     #         'message': message,
                    #     # }
                    #     # # if rec.line_ids:
                    #     # #     rec.line_ids.unlink()
                    #     # return {'warning': warning}
                        raise UserError(
                            _("Purchase Request %s does not have a RFQ.")
                            % rec.pr_id.name
                            # % line.purchase_lines.order_id.id
                        )

class tbl_quotation_selection_line(models.Model):
    _name = "tbl_quotation_selection_line"
    _description = "Quotation Selection Line"
    _order = "pr_line_id asc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    quotation_id = fields.Many2one(
        comodel_name="tbl_quotation_selection",
        string="Quotation Selection",
        copy=False,
    )
    pr_id = fields.Many2one(
        comodel_name="purchase.request",
        # related="quotation_id.pr_id",
        related="pr_line_id.request_id",
        store=True
    )
    pr_add_id = fields.Many2one(
        comodel_name="purchase.request",compute="_compute_pr_add_id", store=True, string="PR"
    )
    rfq_line_id = fields.Many2one(comodel_name="tbl_bisa_rfq_line", string="Rfq Line")

    pr_line_id = fields.Many2one(
        comodel_name="purchase.request.line",
        string="PR Line",
        copy=False,
    )
    pr_qty = fields.Float(
        string="PR Qty", related="pr_line_id.product_qty"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product", related="pr_line_id.product_id"
    )
    product_add_id = fields.Many2one(comodel_name="product.product",string="Product",
                                     compute="_compute_product_add_id", store=True)
    name = fields.Many2one(
        comodel_name="purchase.order",
        string="No",
        copy=False,
        required=True,
        track_visibility="onchange",
        domain=lambda self: [
            (
                "state",
                "=",
                'draft',
            )
        ]
    )
    partner_id_id = fields.Many2one(
        comodel_name="res.partner",
        related="name.partner_id",
        store=True
    )
    po_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="PO Line",
        copy=False,
    )
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, readonly=True)
    price_ori = fields.Float(string='Original Price', digits='Product Price')
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price', readonly=True)
    discount = fields.Float(string="Discount (%)", digits="Discount", readonly=True)
    harga_setelah_discount = fields.Float(string="Price after discount", digits="Product Price", compute="_compute_discounted_price_unit", store=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', store=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=[('active', '=', True)], readonly=True)

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("rfq", "RFQ"),
            # ("done", "PO"),
            # ("cancel", "Cancel"),
            ("done", "Selected"),
            ("cancel", "Rejected"),
        ],
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    pilih = fields.Boolean(
        string="Select",
        default=False
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,
        track_visibility="onchange",
    )
    currency_id = fields.Many2one(related="pr_id.currency_id", readonly=True,
        store=True)
    partner_id = fields.Many2one('res.partner', string='Vendor',related="name.partner_id")

    _sql_constraints = [
        (
            "discount_limit",
            "CHECK (discount <= 100.0)",
            "Discount must be lower than 100%.",
        )
    ]

    @api.depends('pr_line_id', 'pr_line_id.product_id')
    def _compute_product_add_id(self):
        for rec in self:
            if rec.pr_line_id and rec.pr_line_id.product_id:
                rec.product_add_id = rec.pr_line_id.product_id.id

    @api.depends('pr_line_id', 'pr_line_id.request_id')
    def _compute_pr_add_id(self):
        for rec in self:
            if rec.pr_line_id and rec.pr_line_id.request_id:
                rec.pr_add_id = rec.pr_line_id.request_id.id

    @api.depends('price_unit','discount')
    def _compute_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).

        :rtype: float
        :return: Unit price after discount(s).
        """
        for rec in self:
            rec.ensure_one()
            if rec.discount:
                rec.harga_setelah_discount = rec.price_unit * (1 - rec.discount / 100)
            else:
                rec.harga_setelah_discount = rec.price_unit


    @api.depends('product_qty', 'harga_setelah_discount', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                # 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_excluded'],
                # 'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.harga_setelah_discount,
            'currency_id': self.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.partner_id,
        }
    
    # def write(self, vals):
    #     if self.price_ori == 0:
    #         self.price_ori = self.price_unit # Because the purchase user doesn't have write on `res.partner`
    #     res = super().write(vals)
    #     return res
    
    def write(self, vals):
        res = super(tbl_quotation_selection_line, self).write(vals)
        # raise ValidationError(_('The default Unit of Measure and the purchase Unit of Measure must be in the same category.'))
        # if 'after_balance' in vals:
        for rec in self:
            if rec.price_ori == 0 and rec.price_unit > 0:
                rec.price_ori = rec.price_unit
        return res