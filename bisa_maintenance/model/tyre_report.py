# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class TyreReport(models.Model):
    _name = 'tyre.report'
    _description = "Tyre Report"
    _rec_name = 'id'
    _auto = False

    id = fields.Integer("", readonly=1)
    date = fields.Datetime('Date & Time', readonly=1)
    tire_service_id = fields.Many2one('tire.service', readonly=1)
    equipment_id = fields.Many2one(related='tire_service_id.equipment_id', readonly=1)
    pos = fields.Char('POS', readonly=1)
    size = fields.Char(readonly=1)
    serial_number = fields.Char(readonly=1)
    product_id = fields.Many2one('product.template', 'Product', readonly=1)
    product_price = fields.Float('Price', related='product_id.standard_price', readonly=1)
    pattern = fields.Char(readonly=1)
    otd = fields.Float('OTD', readonly=1)
    rtd = fields.Float('RTD 1', readonly=1)
    rtd_2 = fields.Float('RTD 2', readonly=1)
    rtd_average = fields.Float('AVG RTD', readonly=1)
    rtd_percentage = fields.Float('RTD (%)', readonly=1)
    tur = fields.Float('TUR (%)', readonly=1)
    pressure_hc = fields.Selection(selection=[
        ('hot', 'Hot'),
        ('cold', 'Cold')
    ], string='Pressure H/C', readonly=1)
    pressure_hp = fields.Float('Pressure AP', readonly=1)
    price = fields.Float(readonly=1)
    problem = fields.Char('Tyre Problem', readonly=1)
    tyre_type = fields.Selection([
        ('new', 'New'),
        ('spare', 'Spare'),
        ('repair', 'Repaired')
    ], readonly=1)
    remarks = fields.Char('Remarks',readonly=1)
    changer_type = fields.Selection([
        ('removal', 'Removal'),
        ('fitment', 'Fitment'),
    ], readonly=1)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                            WITH cte AS (
                                SELECT date, tire_service_id, pos, size, serial_number, product_id, pattern, otd, rtd, rtd_2,rtd_average, rtd_percentage, tur, pressure_hc, pressure_hp, remove_price price, problem, null as tyre_type, remarks, 'removal' AS changer_type, company_id FROM tyre_removal
                                UNION
                                SELECT date, tire_service_id, pos, size, serial_number, product_id, pattern, otd, rtd, rtd_2,rtd_average, rtd_percentage, tur, pressure_hc, pressure_hp, install_price price, null as problem, tyre_type, remarks, 'fitment' AS changer_type, company_id FROM tyre_fitment
                            )
                            SELECT
                                ROW_NUMBER () OVER (
                                   ORDER BY date
                                ) id
                                , *
                            FROM
                                cte
            )""" % (self._table))

