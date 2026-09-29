from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime, timedelta

from odoo.tests import users


class Requisition(models.Model):
    _name = "requisition"
    _order = "id desc"

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)

    date = fields.Datetime(string='Date & Time', default=datetime.now())
    name = fields.Char('Requisition No.')
    wo_number = fields.Many2one('work.order', 'WO No.')
    equipment_id = fields.Many2one('master_asset_maintenance', string='Unit Code',
                                   domain="[('plotting_location', 'in', tags)]")
    asset_name = fields.Char('Asset Name', related='equipment_id.nama_asset')
    status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('close', 'Close'),
    ], default='draft')
    created_by = fields.Many2one('res.users', default=lambda self: self.env.uid, string='Request by', readonly=1,
                                 store=1)
    request_dt = fields.Datetime(readonly=1, store=True)
    description = fields.Text('Description', related='wo_number.description')
    req_product = fields.One2many('requisition_product', 'requisition_id', 'Product')
    @api.depends('created_by')
    def _compute_approval(self):
        users = self.env.uid
        company = self.env.company.id
        parent_user = self.env['hr.employee'].search([('user_id', '=', users),('company_id', '=', company)], limit=1).coach_id.user_id.id
        if parent_user:
            self.approval = parent_user
        else:
            self.approval = False

    approval = fields.Many2one('res.users', compute=_compute_approval, string='Approval By', readonly='True')
    approval_dt = fields.Datetime(readonly=1, store=True)
    tags = fields.Many2many(comodel_name='hr.employee.category', default=lambda self: self._compute_category(), store=1)
    search_ids = fields.Char(compute="_compute_search_ids", search="search_ids_search")
    maintenance_type = fields.Selection(string='Maintenance Type', related='wo_number.maintenance_type')
    maintenance_activity = fields.Many2one('maintenance.activity', related='wo_number.maintenance_activity',
                                           string='Maintenance Activity')
    schedule_activity = fields.Many2many('schedule.activity', 'Schedule Activity',
                                         related='wo_number.schedule_activity')
    is_periodic = fields.Boolean(related='wo_number.is_periodic')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def compute_product(self):
        for rec in self:
            if rec.maintenance_activity:
                part_list = self.env['maintenance.activity.sparepart'].search(
                    [('maintenance_activity_id', '=', rec.maintenance_activity.id)])
                for part in part_list:
                    # Cari produk yang sudah ada di req_product
                    existing_line = rec.req_product.filtered(
                        lambda line: line.product_code.id == part.product_id.product_tmpl_id.id
                    )

                    if existing_line:
                        # Jika produk sudah ada, update data
                        existing_line.write({
                            'qty': part.product_uom_qty,
                            'remark': part.remark
                        })
                    else:
                        # Jika produk belum ada, tambahkan data baru
                        rec.write({'req_product': [(0, 0, {
                            'product_code': part.product_id.product_tmpl_id.id,
                            'qty': part.product_uom_qty,
                            'remark': part.remark
                        })]})
                else:
                    continue

    @api.model
    def _compute_category(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return [(6, 0, employee_id.category_ids.ids)]

    @api.depends('created_by')
    def _compute_search_ids(self):
        print('my compute')

    def search_ids_search(self, operator, operand):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        tags = employee_id.category_ids

        obj = []
        for tag in tags:
            if tag.name in ('LDP-SPGA') and tag.name in ('LDP-BP'):
                objek = self.env['requisition'].search([]).ids
                for ob in objek:
                    obj.append(ob)
            elif not tag.name:
                objek = self.env['requisition'].search([]).ids
                for ob in objek:
                    obj.append(ob)
            else:
                objek = self.env['requisition'].search([('equipment_id.plotting_location', '=', tag.id)]).ids
                for ob in objek:
                    obj.append(ob)

        return [('id', 'in', obj)]

    def action_apply_pr(self):
        for rec in self:
            for product in rec.req_product:
                purchase_requisition = self.env['product.category'].search(
                    [('name', 'like', 'PURCHASE REQUISITION')])
                if product.product_code.categ_id.parent_id in [purchase_requisition]:
                    # select = self.mapped("req_product.toggle")
                    # if True not in select:
                    #     raise UserError(
                    #         _("Please select at least one.")
                    #     )
                    # else:
                    #     if product.toggle:
                            # if product.avail_qty > product.qty:
                            #     raise UserError(
                            #         _("Available Qty lebih besar dari Qty")
                            #     )
                    purchase_request = self.env['purchase.request'].create({
                        'origin': self.name,
                    })
                    purchase_request_line = purchase_request.line_ids.create({
                        'request_id': purchase_request.id,
                        'product_id': product.product_code.product_variant_id.id,
                        'name': product.item_description,
                        'product_qty': product.qty,
                        'product_uom_id': product.product_code.uom_id.id,
                        'description': product.product_code.name,
                        'estimated_price_unit': product.product_code.standard_price,
                    })

    def action_do(self):
        for rec in self:
            if not rec.wo_number:
                raise UserError("Tidak bisa dilakukan, No WO belum terisi")
            stock_picking = self.env['stock.picking']
            stock_picking_product = self.env['stock.move']
            requisition_product = self.env['requisition_product']

            # Ensure at least one product is selected
            if rec.req_product:
                # select = self.mapped("req_product.toggle")
                # if True not in select:
                #     raise UserError(
                #         _("Please select at least one.")
                #     )

                # Initialize variables to be used for creating a single GI
                picking_type = False
                location_ids = False
                dest_location_ids = False
                equipment_plot = self.env['hr.employee.category'].search(
                    [('id', '=', rec.equipment_id.plotting_location.id)], limit=1).name
                equipment_plot_id = self.env['hr.employee.category'].search(
                    [('id', '=', rec.equipment_id.plotting_location.id)], limit=1).id

                if equipment_plot:
                    equipment_plots = equipment_plot.split('-', 1)[-1]
                    picking_type = self.env['stock.picking.type'].search(
                        [('name', '=', 'Delivery Orders'), ('barcode', 'like', equipment_plots)], limit=1)
                    # location_ids = self.env['stock.location'].search(
                    #     [('name', '=', 'Stock'), ('location_id.name', 'like', equipment_plots)], limit=1)
                    location_ids = self.env['stock.warehouse'].search(
                        [('lot_stock_id.name', '=', 'Stock'), ('plotting_location', '=', equipment_plot_id)], limit=1)
                    dest_location_ids = self.env['stock.location'].search([('name', '=', 'Customers')], limit=1)
                else:
                    picking_type = False

                # Create a single stock.picking record
                picking = stock_picking.create({
                    'picking_type_id': picking_type.id,
                    # 'origin': rec.name,
                    'location_id': location_ids.lot_stock_id.id,
                    'location_dest_id': dest_location_ids.id,
                    'scheduled_date': rec.date,
                    'date_deadline': rec.date,
                    'reference_from': 'req',
                    'origin': rec.name,
                    'wo_number': rec.wo_number.display_name,
                    'unit_code': rec.wo_number.equipment_id.display_name,
                    'mr_operation': str(dict(self.wo_number._fields['operation'].selection).get(self.wo_number.operation)),

                })

                for lines in rec.req_product:
                    parent_issue_req = self.env['product.category'].search(
                        [('name', 'like', 'ISSUE REQUISITION')])
                    if lines.product_code.categ_id.parent_id.id in (parent_issue_req.ids):
                        # if lines.toggle:
                            # if lines.avail_qty < lines.qty:
                            #     parent_issue_req = self.env['product.category'].search(
                            #         [('name', 'like', 'ISSUE REQUISITION')]).id
                            #     if lines.product_code.categ_id == parent_issue_req:
                            #         continue
                            #     else:
                            #         raise UserError(
                            #             _("Available Qty lebih kecil dari Qty")
                            #         )

                        if lines.no_gi:
                            raise UserError('Sudah ada data DO %s' % (lines.no_gi.name))

                        # Update the requisition product with the picking ID
                        requisition_product.update({
                            'no_gi': picking.id,
                        })
                        product = self.env['product.product'].search([('product_tmpl_id', '=', lines.product_code.id)],
                                                                     limit=1)
                        # Create stock.move for each product line
                        picking_product = stock_picking_product.create({
                            'picking_id': picking.id,
                            'product_id': product.id,
                            'name': product.name,
                            'location_id': location_ids.lot_stock_id.id,
                            'location_dest_id': dest_location_ids.id,
                            'product_uom_qty': lines.qty,
                            'product_uom': lines.uom.id,
                            'description_picking': self.display_name
                        })
                        lines.no_gi = picking.id

    def action_req_appr(self):
        self.status = 'waiting'
        sequence = self.env['ir.sequence'].next_by_code('mnt_requisition')

        plot = self.equipment_id.plotting_location.name
        if not plot:
            raise UserError("Plotting Location is Empty")
        else:
            name = plot + '.' + sequence
        self.update({
            'name': name,
            'request_dt': datetime.now(),
        })

        if self.req_product:
            self.action_apply_pr()
            self.action_do()
        return self.env.ref('bisa_maintenance.action_print_out_requisition').report_action(docids=self.id, config=False)

    def action_req_appr_batch(self):
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['requisition'].browse(active_ids) or self

        for record in records:
            if record.status != 'draft':
                raise UserError("Please select draft record!")

            record.status = 'waiting'
            sequence = self.env['ir.sequence'].next_by_code('mnt_requisition')

            plot = record.equipment_id.plotting_location.name
            if not plot:
                raise UserError("Plotting Location is Empty")
            else:
                name = plot + '.' + sequence
            record.update({
                'name': name,
                'request_dt': datetime.now(),
            })

            if record.req_product:
                self.action_apply_pr()
                self.action_do()
            # return self.env.ref('bisa_maintenance.action_print_out_requisition').report_action(docids=record.id, config=False)
        return

    def action_appr(self):
        self.status = 'approved'
        self.approval_dt = datetime.now()
        # doc_ids = self.env.context.get('active_ids')


    def action_done(self):
        if self.status != 'waiting':
            raise UserError("Cannot set to done document that is not in progress")
        self.rfu_date = datetime.today()
        self.move_ids._action_done()
        self.status = 'done'
        return

    def action_close(self):
        self.status = 'close'

    def action_reject(self):
        self.status = 'rejected'

    def action_reset(self):
        self.status = 'draft'

    def action_cancel(self):
        self.status = 'cancel'




class RequisitionProduct(models.Model):
    _name = "requisition_product"
    _order = "id desc"

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    requisition_id = fields.Many2one(comodel_name='requisition', string="Requisition", readonly=True)
    product_code = fields.Many2one(comodel_name='product.template', string='Product Code')
    item_description = fields.Char(related='product_code.name', string='Item Description')
    interchange = fields.Many2many(comodel_name="multiple.reference.per.product",
                                   domain="[('product_id', '=', product_code)]", string="Interchange")
    qty = fields.Float('Qty')
    avail_qty = fields.Float(compute='_get_avail_qty', string="Available Qty")
    uom = fields.Many2one(comodel_name='uom.uom', related='product_code.uom_id', sting='UOM')
    toggle = fields.Boolean()
    no_gi = fields.Many2one('stock.picking', 'No. GI')
    status_gi = fields.Selection('Status GI', related='no_gi.state')
    date = fields.Datetime(related='no_gi.date_done')
    equipment_id = fields.Many2one('master_asset_maintenance', string='Unit Code')
    kmhm_running = fields.Float(string="KM/HM Running")
    price = fields.Float(related='product_code.standard_price', store=True)
    total_amount = fields.Float(compute='_compute_total')
    remark = fields.Char()

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.onchange('product_code','requisition_id.equipment_id')
    def _get_avail_qty(self):
        for rec in self:
            if rec.requisition_id.equipment_id:
                product = self.env['product.product'].search([('product_tmpl_id','=',rec.product_code.id)])
                warehouse = self.env['stock.warehouse'].search([('company_id','=', rec.company_id.id),('plotting_location','=', rec.requisition_id.equipment_id.plotting_location.id)], limit=1).lot_stock_id.id
                stock = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',warehouse)]).available_quantity
                rec.avail_qty = stock

    def _compute_total(self):
        for me in self:
            me.total_amount = me.product_code.list_price * me.qty

    @api.onchange('equipment_id')
    def onchange_equipment(self):
        self.kmhm_running = self.equipment_id.kmhm_running

    @api.depends('requisition_id')
    def get_remark(self):
        maintenance_activity_id = self.requisition_id.maintenance_activity
        sparepart_id = self.env['maintenance.activity.sparepart'].search([('product_id', '=', self.product_code.id), ('maintenance_activity_id', '=', maintenance_activity_id.id)], limit=1)
        self.remark = sparepart_id.remark

class ProductTemplate(models.Model):
    _inherit = "product.template"
    _order = "name"

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'default_code'])
        entah = self._context.get('display_product_code')
        if entah:
            return [(template.id, '%s%s' % (template.default_code and '%s' % template.default_code or '', ''))
                    for template in self]
        else:
            return [(template.id, '%s%s' % (template.default_code and '%s' % template.default_code or '', ''))
                    for template in self]
class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    plotting_location = fields.Many2many('hr.employee.category')