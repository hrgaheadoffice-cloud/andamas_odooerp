# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    description = fields.Text('Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Delivery'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    reference_from = fields.Selection([
        ('po','Purchase Order'),
        ('req', 'Requisition')
    ],'Reference From')
    requisition_numb = fields.Char('Requisition Number')
    wo_number = fields.Char()
    unit_code = fields.Char()
    mr_operation = fields.Char('Operation')

    # @api.onchange('origin','requisition_numb')
    # def compute_reference(self):
    #     for rec in self:
    #         if rec.requisition_numb:
    #             self.reference_from = 'req'
    #         elif rec.origin:
    #             self.reference_from = 'po'
    #         else:
    #             self.reference_from = False
    #     return




    @api.model
    def _purchase_request_picking_confirm_message_content(
        self, picking, request, request_dict
    ):
        if not request_dict:
            request_dict = {}
        title = _("Receipt confirmation %s for your Request %s") % (
            picking.name,
            request.name,
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "have now been received in Incoming Shipment %s:"
        ) % (request.name, picking.name)
        message += "<ul>"
        for line in request_dict.values():
            message += _("<li><b>%s</b>: Received quantity %s %s</li>") % (
                line["name"],
                line["product_qty"],
                line["product_uom"],
            )
        message += "</ul>"
        return message

    def action_done(self):
        super(StockPicking, self).action_done()
        request_obj = self.env["purchase.request"]
        for picking in self:
            requests_dict = {}
            if picking.picking_type_id.code != "incoming":
                continue
            for move in picking.move_lines:
                if move.purchase_line_id:
                    for (
                        request_line
                    ) in move.purchase_line_id.sudo().purchase_request_lines:
                        request_id = request_line.request_id.id
                        if request_id not in requests_dict:
                            requests_dict[request_id] = {}
                        data = {
                            "name": request_line.name,
                            "product_qty": move.product_qty,
                            "product_uom": move.product_uom.name,
                        }
                        requests_dict[request_id][request_line.id] = data
            # for request_id in requests_dict:
            #     request = request_obj.sudo().browse(request_id)
            #     message = self._purchase_request_picking_confirm_message_content(
            #         picking, request, requests_dict[request_id]
            #     )
            #     request.sudo().message_post(
            #         body=message,
            #         subtype="mail.mt_comment",
            #         author_id=self.env.user.partner_id.id,
            #     )

class PRStocklocation(models.Model):
    _inherit = "stock.location"

    location = fields.Many2one(
        'account.analytic.account',
        string="Location",
        track_visibility="onchange",
        required=True,
        domain=lambda self: [
            (
                "tipe",
                "=",
                1,
            )
        ],
    )
