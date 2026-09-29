# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError,UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    # account_id_cs = fields.Many2one('account.move','Account move')

    created_purchase_request_line_id = fields.Many2one(
        comodel_name="purchase.request.line",
        string="Created Purchase Request Line",
        ondelete="set null",
        readonly=True,
        copy=False,
    )

    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="stock_move_id",
        copy=False,
        string="Purchase Request Allocation",
    )

    purchase_request_ids = fields.One2many(
        comodel_name="purchase.request",
        string="Purchase Requests",
        compute="_compute_purchase_request_ids",
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields += ["created_purchase_request_line_id"]
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted += [
            move.purchase_line_id.id,
            move.created_purchase_request_line_id.id,
        ]
        return keys_sorted

    def _action_cancel(self):
        for move in self:
            if move.created_purchase_request_line_id:
                try:
                    activity_type_id = self.env.ref("mail.mail_activity_data_todo").id
                except ValueError:
                    activity_type_id = False
                pr_line = move.created_purchase_request_line_id
                self.env["mail.activity"].sudo().create(
                    {
                        "activity_type_id": activity_type_id,
                        "note": _(
                            "A sale/manufacturing order that generated this "
                            "purchase request has been cancelled/deleted. "
                            "Check if an action is needed."
                        ),
                        "user_id": pr_line.product_id.responsible_id.id,
                        "res_id": pr_line.request_id.id,
                        "res_model_id": self.env.ref(
                            "purchase_request.model_purchase_request"
                        ).id,
                    }
                )
        return super(StockMove, self)._action_cancel()

    @api.depends("purchase_request_allocation_ids")
    def _compute_purchase_request_ids(self):
        for rec in self:
            rec.purchase_request_ids = rec.purchase_request_allocation_ids.mapped(
                "purchase_request_id"
            )

    def _merge_moves_fields(self):
        res = super(StockMove, self)._merge_moves_fields()
        res["purchase_request_allocation_ids"] = [
            (4, m.id) for m in self.mapped("purchase_request_allocation_ids")
        ]
        return res

    @api.constrains("company_id")
    def _check_company_purchase_request(self):
        if not self.ids:
            return
        self.env.cr.execute(
            """
            SELECT 1
            FROM purchase_request_allocation pra
            INNER JOIN stock_move sm
               ON sm.id=pra.stock_move_id
            WHERE pra.company_id != sm.company_id
                AND sm.id IN %s
            LIMIT 1
        """,
            (tuple(self.ids),),
        )
        if self.env.cr.fetchone():
            raise ValidationError(
                _(
                    "The company of the purchase request must match with "
                    "that of the location."
                )
            )

    def copy_data(self, default=None):
        if not default:
            default = {}
        if "allocation_ids" not in default:
            default["purchase_request_allocation_ids"] = []
        first_it = True
        for alloc in self.purchase_request_allocation_ids.filtered(
            lambda al: al.requested_product_uom_qty > al.allocated_product_qty
        ):
            qty_done = sum(alloc.stock_move_id.mapped("move_line_ids.qty_done"))
            if first_it:
                qty_left = qty_done
                first_it = False
            if qty_left >= alloc.open_product_qty:
                qty_left = qty_done - alloc.open_product_qty
                continue
            else:
                open_qty = alloc.open_product_qty - qty_left
            default["purchase_request_allocation_ids"].append(
                (
                    0,
                    0,
                    {
                        "purchase_request_line_id": alloc.purchase_request_line_id.id,
                        "requested_product_uom_qty": open_qty,
                    },
                )
            )
        return super(StockMove, self).copy_data(default)

    def _get_dest_account(self, accounts_data):
        equipment = self.env['master_asset_maintenance'].search([('nama_asset','=',self.picking_id.unit_code)])
        asset_category = self.env['master.asset.category'].search([('id','=',equipment.category.id)])
        fuel_account_id = self.env['account.account'].search([('id', '=', self.consumption_id.equipment_id.category.outgoing_account.id)])
        account = False
        if self.picking_id.reference_from == 'req':
            account = asset_category.outgoing_product.id
        if self.consumption_id:
            account = fuel_account_id.id
        return account or self.location_dest_id.valuation_in_account_id.id or accounts_data['stock_output'].id

    def _prepare_common_svl_vals(self):
        """When a `stock.valuation.layer` is created from a `stock.move`, we can prepare a dict of
        common vals.

        :returns: the common values when creating a `stock.valuation.layer` from a `stock.move`
        :rtype: dict
        """
        self.ensure_one()
        if self.consumption_id:
            return {
                'stock_move_id': self.id,
                'company_id': self.company_id.id,
                'product_id': self.product_id.id,
                'description': '%s - %s' % (self.consumption_id.operation, self.consumption_id.name),
            }
        else:
            return {
                'stock_move_id': self.id,
                'company_id': self.company_id.id,
                'product_id': self.product_id.id,
                'description': self.picking_id.mr_operation and '%s - %s - %s' % (self.picking_id.mr_operation,self.reference, self.product_id.name) or self.product_id.name,
            }

    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()
        self = self.with_company(self.company_id)
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()

        acc_src = self._get_src_account(accounts_data)
        acc_dest = self._get_dest_account(accounts_data)

        acc_valuation = accounts_data.get('stock_valuation', False)
        if acc_valuation:
            acc_valuation = acc_valuation.id
        if not accounts_data.get('stock_journal', False):
            raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts.'))
        if not acc_src:
            raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_dest:
            raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_valuation:
            raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))
        journal_id = accounts_data['stock_journal'].id
        return journal_id, acc_src, acc_dest, acc_valuation
