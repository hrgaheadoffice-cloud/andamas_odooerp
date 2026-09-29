# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero
from itertools import groupby




class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # priority = fields.Many2one(
    #     "priority", 'Priority')
    pr_id = fields.Many2one('purchase.request','Purchase Request', readonly=True)
    # priority_pr = fields.Selection(
    #     selection=[
    #         ("normal", "normal"),
    #         ("urgent", "Urgent"),
    #         ("top_urgent", "Top Urgent"),],
    #     string="Priority",
    #     related='pr_id.priority',)
    priority_pr = fields.Many2one(
        comodel_name="priority",
        related='pr_id.priority')
    proc_group_id = fields.Many2one(
        comodel_name="tbl_proc_group",
        string="Procurement Category", 
        required=True
    )
    location = fields.Many2one(
        'account.analytic.account',
        string="Location",
        track_visibility="onchange",
        )
    no_rfq = fields.Char('No RFQ')
    # cost_center = fields.Many2one('account.cost.center','Cost Center', required=True)
    qs_id = fields.Many2one('tbl_quotation_selection','Quotation Selection')
    order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
        domain=[('show_in_po', '=', True)])
    rfq_line = fields.One2many('tbl_bisa_rfq_line', 'name', string='RFQ Lines', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_rfq_untaxed = fields.Monetary(string='Untaxed Amount RFQ', store=True, readonly=True, compute='_amount_all_rfq', tracking=True)
    amount_rfq_tax = fields.Monetary(string='Taxes RFQ', store=True, readonly=True, compute='_amount_all_rfq')
    amount_rfq_total = fields.Monetary(string='Total RFQ', store=True, readonly=True, compute='_amount_all_rfq')

    @api.depends('rfq_line','rfq_line.harga_setelah_discount')
    def _amount_all_rfq(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.rfq_line:
                line._compute_amount()
                amount_untaxed += line.price_total
                amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_rfq_untaxed': currency.round(amount_untaxed),
                'amount_rfq_tax': currency.round(amount_tax),
                'amount_rfq_total': amount_untaxed + amount_tax,
            })


    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('rfq') or '/'
            # vals['no_rfq'] = self_comp.env['ir.sequence'].next_by_code('rfq') or '/'
            vals['no_rfq'] = vals['name']
        vals, partner_vals = self._write_partner_values(vals)
        res = super(PurchaseOrder, self_comp).create(vals)
        if partner_vals:
            res.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        return res

    def _purchase_request_confirm_message_content(self, request, request_dict=None):
        self.ensure_one()
        if not request_dict:
            request_dict = {}
        title = _("Order confirmation %s for your Request %s") % (
            self.name,
            request.name,
        )
        message = "<h3>%s</h3><ul>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "have now been confirmed in Purchase Order %s:"
        ) % (request.name, self.name)

        for line in request_dict.values():
            message += _(
                "<li><b>%s</b>: Ordered quantity %s %s, Planned date %s</li>"
            ) % (
                line["name"],
                line["product_qty"],
                line["product_uom"],
                line["date_planned"],
            )
        message += "</ul>"
        return message

    def _purchase_request_confirm_message(self):
        request_obj = self.env["purchase.request"]
        for po in self:
            requests_dict = {}
            for line in po.order_line:
                for request_line in line.sudo().purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    date_planned = "%s" % line.date_planned
                    data = {
                        "name": request_line.name,
                        "product_qty": line.product_qty,
                        "product_uom": line.product_uom.name,
                        "date_planned": date_planned,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict:
                request = request_obj.sudo().browse(request_id)
                message = po._purchase_request_confirm_message_content(
                    request, requests_dict[request_id]
                )
                request.message_post(
                    body=message, subtype_id=self.env.ref("mail.mt_comment").id
                )
        return True

    def _purchase_request_line_check(self):
        for po in self:
            for line in po.order_line:
                for request_line in line.purchase_request_lines:
                    if request_line.sudo().purchase_state == "done":
                        raise exceptions.UserError(
                            _("Purchase Request %s has already been completed")
                            % request_line.request_id.name
                        )
        return True

    def button_confirm(self):
        self._purchase_request_line_check()
        res = super(PurchaseOrder, self).button_confirm()
        # self.name = self.env["ir.sequence"].next_by_code("purchase.order")
        self._purchase_request_confirm_message()
        return res

    # def button_approve(self):
    #     for rec in self:
    #         if rec.qs_id:
    #             for po in rec.qs_id.line_ids:
    #                 if po.name.state == 'draft':
    #                     po.name.button_cancel()
    #     return super(PurchaseOrder, self).button_approve()

    def unlink(self):
        alloc_to_unlink = self.env["purchase.request.allocation"]
        for rec in self:
            for alloc in (
                rec.order_line.mapped("purchase_request_lines")
                .mapped("purchase_request_allocation_ids")
                .filtered(lambda alloc: alloc.purchase_line_id.order_id.id == rec.id)
            ):
                alloc_to_unlink += alloc
        res = super().unlink()
        alloc_to_unlink.unlink()
        return res

    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        line_vals = pending_section._prepare_account_move_line()
                        line_vals.update({'sequence': sequence})
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                        sequence += 1
                        pending_section = None
                    line_vals = line._prepare_account_move_line()
                    line_vals.update({'sequence': sequence})
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                    sequence += 1
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(
                _('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (
        x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
            attachment = self.env['ir.attachment'].search(
                [('res_model', '=', 'purchase.order'), ('res_id', '=', line.order_id.id)])
            for attachment_item in attachment:
                self.env['ir.attachment'].create({
                    'name': attachment_item.name,
                    'type': 'binary',
                    'datas': attachment_item.datas,
                    'res_model': 'account.move',
                    'res_id': moves.id,
                })

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(
            lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
        return self.action_view_invoice(moves)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    pr_id = fields.Many2one('purchase.request','Purchase Request', related='order_id.pr_id')
    show_in_po = fields.Boolean('Show in PO', default=True)
    purchase_request_lines = fields.Many2many(
        comodel_name="purchase.request.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_order_line_id",
        column2="purchase_request_line_id",
        string="Purchase Request Lines",
        readonly=True,
        copy=False,
    )

    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_line_id",
        string="Purchase Request Allocation",
        copy=False,
    )
    
    analytic_tag_id = fields.Many2one('account.analytic.tag', string='Analytic Tags')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Analytic Tags', compute='_compute_analytic_tag_id')

    @api.depends('analytic_tag_id')
    def _compute_analytic_tag_id(self):
        for record in self:
            # Mengambil nilai dari many2one_field
            related_record = record.analytic_tag_id
            
            # Mengisi many2many_field dengan nilai dari many2one_field
            record.analytic_tag_ids = [(6, 0, [related_record.id])] if related_record else False

    def action_open_request_line_tree_view(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids += line.purchase_request_lines.ids

        domain = [("id", "in", request_line_ids)]

        return {
            "name": _("Purchase Request Lines"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.request.line",
            "view_mode": "tree,form",
            "domain": domain,
        }

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        val = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        all_list = []
        for v in val:
            all_ids = self.env["purchase.request.allocation"].search(
                [("purchase_line_id", "=", v["purchase_line_id"])]
            )
            for all_id in all_ids:
                all_list.append((4, all_id.id))
            v["purchase_request_allocation_ids"] = all_list
        return val

    def update_service_allocations(self, prev_qty_received):
        for rec in self:
            allocation = self.env["purchase.request.allocation"].search(
                [
                    ("purchase_line_id", "=", rec.id),
                    ("purchase_line_id.product_id.type", "=", "service"),
                ]
            )
            if not allocation:
                return
            qty_left = rec.qty_received - prev_qty_received
            for alloc in allocation:
                allocated_product_qty = alloc.allocated_product_qty
                if not qty_left:
                    alloc.purchase_request_line_id._compute_qty()
                    break
                if alloc.open_product_qty <= qty_left:
                    allocated_product_qty += alloc.open_product_qty
                    qty_left -= alloc.open_product_qty
                    alloc._notify_allocation(alloc.open_product_qty)
                else:
                    allocated_product_qty += qty_left
                    alloc._notify_allocation(qty_left)
                    qty_left = 0
                alloc.write({"allocated_product_qty": allocated_product_qty})

                message_data = self._prepare_request_message_data(
                    alloc, alloc.purchase_request_line_id, allocated_product_qty
                )
                message = self._purchase_request_confirm_done_message_content(
                    message_data
                )
                alloc.purchase_request_line_id.request_id.message_post(
                    body=message, subtype_id=self.env.ref("mail.mt_comment").id
                )

                alloc.purchase_request_line_id._compute_qty()
        return True

    @api.model
    def _purchase_request_confirm_done_message_content(self, message_data):
        title = _("Service confirmation for Request %s") % (
            message_data["request_name"]
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested services from Purchase"
            " Request %s requested by %s "
            "have now been received:"
        ) % (message_data["request_name"], message_data["requestor"])
        message += "<ul>"
        message += _("<li><b>%s</b>: Received quantity %s %s</li>") % (
            message_data["product_name"],
            message_data["product_qty"],
            message_data["product_uom"],
        )
        message += "</ul>"
        return message

    def _prepare_request_message_data(self, alloc, request_line, allocated_qty):
        return {
            "request_name": request_line.request_id.name,
            "product_name": request_line.product_id.name_get()[0][1],
            "product_qty": allocated_qty,
            "product_uom": alloc.product_uom_id.name,
            "requestor": request_line.request_id.requested_by.partner_id.name,
        }

    def write(self, vals):
        #  As services do not generate stock move this tweak is required
        #  to allocate them.
        prev_qty_received = {}
        if vals.get("qty_received", False):
            service_lines = self.filtered(lambda l: l.product_id.type == "service")
            for line in service_lines:
                prev_qty_received[line.id] = line.qty_received
        res = super(PurchaseOrderLine, self).write(vals)
        if prev_qty_received:
            for line in service_lines:
                line.update_service_allocations(prev_qty_received[line.id])
        return res


class tbl_bisa_rfq_line(models.Model):
    _name = "tbl_bisa_rfq_line"

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
        string="PR No",readonly=True
    )

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
                                     compute="_compute_product_add_id", store=True, readonly=False)

    name = fields.Many2one(
        comodel_name="purchase.order",
        string="No"
    )
    no_rfq = fields.Char('No RFQ', related="name.no_rfq")
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
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    price_ori = fields.Float(string='Original Price', digits='Product Price')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    discount = fields.Float(string="Discount (%)", digits="Discount")
    harga_setelah_discount = fields.Float(string="Price after discount", digits="Product Price", compute="_compute_discounted_price_unit", store=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', store=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=[('active', '=', True)])
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

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
    currency_id = fields.Many2one(related="name.currency_id", readonly=True,
        store=True)
    partner_id = fields.Many2one('res.partner', string='Vendor',related="name.partner_id")
    
    _sql_constraints = [
        (
            "discount_limit",
            "CHECK (discount <= 100.0)",
            "Discount must be lower than 100%.",
        )
    ]

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
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_excluded'],
                # 'price_subtotal': taxes['total_excluded'],
            })

    @api.depends('pr_line_id', 'pr_line_id.product_id')
    def _compute_product_add_id(self):
        for rec in self:
            if rec.pr_line_id and rec.pr_line_id.product_id:
                rec.product_add_id = rec.pr_line_id.product_id.id

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
        res = super(tbl_bisa_rfq_line, self).write(vals)
        # raise ValidationError(_('The default Unit of Measure and the purchase Unit of Measure must be in the same category.'))
        # if 'after_balance' in vals:
        for rec in self:
            if rec.price_ori == 0 and rec.price_unit > 0:
                rec.price_ori = rec.price_unit
        return res
    
    def unlink(self):
        for request in self:
            if request.pr_id:
                raise UserError(
                    _("You cannot delete this product because it originates from a PR.")
                )
        return super(tbl_bisa_rfq_line, self).unlink()