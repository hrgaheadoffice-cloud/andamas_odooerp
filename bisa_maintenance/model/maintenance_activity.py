from odoo import api, fields, models


class MaintenanceActivity(models.Model):
    _name = "maintenance.activity"

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char()
    service_type = fields.Char('Type Service')
    brand = fields.Many2one('brand', 'Brand')
    model = fields.Many2one('model', 'Model')
    cycle = fields.Char()
    sparepart_ids = fields.One2many('maintenance.activity.sparepart', 'maintenance_activity_id')
    asset_list = fields.One2many('activity.asset.list', 'maintenance_activity_id')

    @api.model
    def create(self, vals):
        model = self.env['model'].search([('id','=', vals['model'])]).name
        vals['name'] = '{} - {} - {}'.format(vals['service_type'], model, vals['cycle'])
        return super(MaintenanceActivity, self).create(vals)


class MaintenanceActivitySparepart(models.Model):
    _name = "maintenance.activity.sparepart"

    maintenance_activity_id = fields.Many2one('maintenance.activity')

    component = fields.Many2one('component')
    product_id = fields.Many2one('product.product', required=1)
    item_desc = fields.Char('Item Description', related='product_id.product_tmpl_id.name')
    product_uom_qty = fields.Float(required=1)
    product_uom = fields.Many2one('uom.uom',related='product_id.uom_id')
    coa = fields.Selection([
        ('backlog', 'Backlog'),
        ('stock', 'Stock'),
        ('part_service', 'Part Service'),
        ('lubrication', 'Lubrication'),
        ('tools', 'Tools'),
        ('wheel_tyre', 'Wheel & Tyre'),
        ('workshop', 'Workshop'),
        ('consumable', 'Consumable'),
    ], 'COA')
    location_id = fields.Many2one(
        'stock.location', 'Source Location')
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location')
    remark = fields.Char()


class MaintenanceActivityAssetList(models.Model):
    _name = "activity.asset.list"

    maintenance_activity_id = fields.Many2one('maintenance.activity')

    unit_code = fields.Many2one('master_asset_maintenance')
    asset_name = fields.Many2one('asset_maintenance_kategori', related='unit_code.kat_asset',
                                 string='Asset Name', readonly=True)

class ProductTemplate(models.Model):
    _inherit = "product.product"
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


