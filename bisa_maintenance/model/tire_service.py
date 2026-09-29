from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError, AccessError



class TireService(models.Model):
    _name = "tire.service"
    _order = "id desc"

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char()
    work_order_id = fields.Many2one('work.order', 'No. Work Order')
    created_by = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.uid, readonly=1, store=1)
    location_problem = fields.Char(related='work_order_id.location_problem')
    equipment_id = fields.Many2one(related='work_order_id.equipment_id')
    start_date = fields.Datetime('Date & Time Start')
    end_date = fields.Datetime('Date & Time Finish')
    status = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel')
    ], default='draft')
    tyre_removal_ids = fields.One2many('tyre.removal', 'tire_service_id')
    tyre_fitment_ids = fields.One2many('tyre.fitment', 'tire_service_id')
    search_ids = fields.Char(compute="_compute_search_ids", search="search_ids_search")

    # Tyre Detail
    @api.depends('rtd', 'rtd_2')
    def _compute_rtd_average(self):
        for line in self:
            rtd_average = (line.rtd + line.rtd_2) / 2
            line.update({
                'rtd_average': rtd_average
            })

    @api.depends('otd', 'rtd_average')
    def _compute_rtd_percentage(self):
        for line in self:
            rtd_percentage = ((line.rtd_average - 5) / line.otd if line.otd else 0) * 100
            line.update({
                'rtd_percentage': rtd_percentage
            })

    @api.depends('rtd_percentage')
    def _compute_tur(self):
        for line in self:
            tur = 100 - line.rtd_percentage
            line.update({
                'tur': tur
            })

    @api.depends('product_price', 'rtd_percentage')
    def _compute_remove_price(self):
        for line in self:
            remove_price = line.product_price * line.rtd_percentage / 100
            line.update({
                'remove_price': remove_price
            })
    pos = fields.Selection(
        [
            ('1', '1',),
            ('2', '2',),
            ('3', '3',),
            ('4', '4',),
            ('5', '5',),
            ('6', '6',),
            ('7', '7',),
            ('8', '8',),
            ('9', '9',),
            ('10', '10',),
        ], default='1'
    )
    size = fields.Char('Size')
    serial_number = fields.Char('Serial Number')
    product_id = fields.Many2one('product.template', 'Product')
    product_price = fields.Float('Price', related='product_id.standard_price')
    pattern = fields.Char()
    problem = fields.Char()
    remarks = fields.Char()

    # Tyre Condition
    otd = fields.Float('OTD')
    rtd = fields.Float('RTD 1')
    rtd_2 = fields.Float('RTD 2')
    rtd_average = fields.Float('AVG RTD', compute=_compute_rtd_average, readonly=1, store=1)
    rtd_percentage = fields.Float('RTD (%)', compute=_compute_rtd_percentage, readonly=1, store=1)
    tur = fields.Float('TUR (%)', compute=_compute_tur, readonly=1, store=1)
    pressure_hc = fields.Float('Pressure H/C')
    pressure_hp = fields.Float('Pressure H/P')
    remove_price = fields.Float(compute=_compute_remove_price, readonly=1, store=1)

    @api.depends('created_by')
    def _compute_search_ids(self):
        print('my compute')

    def search_ids_search(self, operator, operand):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        tags = employee_id.category_ids

        obj = []
        for tag in tags:
            if tag.name in ('LDP-SPGA','LDP-BP'):
                objek = self.env['tire.service'].search([]).ids
                for ob in objek:
                    obj.append(ob)
            elif not tag.name:
                objek = self.env['tire.service'].search([]).ids
                for ob in objek:
                    obj.append(ob)
            else:
                objek = self.env['tire.service'].search([('equipment_id.plotting_location', '=', tag.id)]).ids
                for ob in objek:
                    obj.append(ob)

        return [('id', 'in', obj)]

    def action_confirm(self):
        self.status = 'confirm'

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('seq_tire_service')
        plot_name = self.env['master_asset_maintenance'].search([('id', '=', vals['equipment_id'])]).plotting_location.name
        if not plot_name:
            raise UserError("Plotting Location is Empty")
        else:
            vals['name'] = plot_name + '.' + sequence
        res = super(TireService, self).create(vals)
        return res

    def get_legend(self,res_id):
        # Search for the attachment
        attachment = self.env['ir.attachment'].search([('name', 'like', 'dt-legend')], limit=1)

        # Return the image data if found, else return None
        return attachment.datas if attachment else None
    def get_legend2(self,res_id):
        # Search for the attachment
        attachment = self.env['ir.attachment'].search([('name', 'like', 'legend-detail')], limit=1)

        # Return the image data if found, else return None
        return attachment.datas if attachment else None


class TyreRemoval(models.Model):
    _name = "tyre.removal"

    @api.depends('rtd', 'rtd_2')
    def _compute_rtd_average(self):
        for line in self:
            rtd_average = (line.rtd + line.rtd_2) / 2
            line.update({
                'rtd_average': rtd_average
            })

    @api.depends('otd', 'rtd_average')
    def _compute_rtd_percentage(self):
        for line in self:
            rtd_percentage = ((line.rtd_average - 5) / line.otd if line.otd else 0) * 100
            line.update({
                'rtd_percentage': rtd_percentage
            })

    @api.depends('rtd_percentage')
    def _compute_tur(self):
        for line in self:
            tur = 100 - line.rtd_percentage
            line.update({
                'tur': tur
            })

    @api.depends('product_price', 'rtd_percentage')
    def _compute_remove_price(self):
        for line in self:
            remove_price = line.product_price * line.rtd_percentage / 100
            line.update({
                'remove_price': remove_price
            })

    date = fields.Datetime('Date & Time', default=datetime.today())
    tire_service_id = fields.Many2one('tire.service')
    equipment_id = fields.Many2one(related='tire_service_id.equipment_id')
    pos = fields.Char('POS')
    size = fields.Char()
    serial_number = fields.Char()
    km_running = fields.Integer()
    product_id = fields.Many2one('product.template', 'Product')
    product_price = fields.Float('Price', related='product_id.standard_price')
    pattern = fields.Char()
    otd = fields.Float('OTD')
    rtd = fields.Float('RTD 1')
    rtd_2 = fields.Float('RTD 2')
    rtd_average = fields.Float('AVG RTD', compute=_compute_rtd_average, readonly=1, store=1)
    rtd_percentage = fields.Float('RTD (%)', compute=_compute_rtd_percentage, readonly=1, store=1)
    tur = fields.Float('TUR (%)', compute=_compute_tur, readonly=1, store=1)
    pressure_hc = fields.Float('Pressure H/C')
    pressure_hp = fields.Float('Pressure H/P')
    remove_price = fields.Float(compute=_compute_remove_price, readonly=1, store=1)
    problem = fields.Char()
    remarks = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class TyreFitment(models.Model):
    _name = "tyre.fitment"

    @api.depends('rtd', 'rtd_2')
    def _compute_rtd_average(self):
        for line in self:
            rtd_average = (line.rtd + line.rtd_2) / 2
            line.update({
                'rtd_average': rtd_average
            })

    @api.depends('otd', 'rtd')
    def _compute_rtd_percentage(self):
        for line in self:
            rtd_percentage = (line.rtd / line.otd if line.otd else 0) * 100
            line.update({
                'rtd_percentage': rtd_percentage
            })

    @api.depends('rtd_percentage')
    def _compute_tur(self):
        for line in self:
            tur = 100 - line.rtd_percentage
            line.update({
                'tur': tur
            })

    @api.depends('product_price', 'rtd_percentage')
    def _compute_install_price(self):
        for line in self:
            install_price = line.product_price * line.rtd_percentage / 100
            line.update({
                'install_price': install_price
            })

    date = fields.Datetime('Date & Time', default=datetime.today())
    tire_service_id = fields.Many2one('tire.service')
    equipment_id = fields.Many2one(related='tire_service_id.equipment_id')
    pos = fields.Char('POS')
    size = fields.Char()
    serial_number = fields.Char()
    km_running = fields.Integer()
    product_id = fields.Many2one('product.template', 'Product')
    product_price = fields.Float('Price', related='product_id.standard_price')
    pattern = fields.Char()
    otd = fields.Float('OTD')
    rtd = fields.Float('RTD 1')
    rtd_2 = fields.Float('RTD 2')
    rtd_average = fields.Float('AVG RTD', compute=_compute_rtd_average, readonly=1, store=1)
    rtd_percentage = fields.Float('RTD (%)', compute=_compute_rtd_percentage, readonly=1, store=1)
    tur = fields.Float('TUR (%)', compute=_compute_tur, readonly=1, store=1)
    pressure_hc = fields.Float('Pressure H/C')
    pressure_hp = fields.Float('Pressure H/P')
    install_price = fields.Float(compute=_compute_install_price, readonly=1, store=1)
    tyre_type = fields.Selection([
        ('new', 'New'),
        ('spare', 'Spare')
    ])
    remarks = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class TyreProblem(models.Model):
    _name = "tyre.problem"

    name = fields.Char()
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)


class TyreRemarks(models.Model):
    _name = "tyre.remarks"

    name = fields.Char()
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
