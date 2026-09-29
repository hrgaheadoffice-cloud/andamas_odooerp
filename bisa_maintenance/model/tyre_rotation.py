# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class TyreRotation(models.Model):
    _name = 'tyre.rotation'
    _description = "Tyre Rotation"
    _rec_name = 'id'
    _auto = False

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    # tyre_removal
    tr_date = fields.Datetime('Date & Time', readonly=1)
    tr_tire_service_id = fields.Many2one('tire.service', 'Tire Service', readonly=1)
    tr_equipment_id = fields.Many2one(related='tr_tire_service_id.equipment_id', string='Unit Code', readonly=1)
    tr_pos = fields.Char('POS', readonly=1)
    tr_size = fields.Char('Size', readonly=1)
    tr_serial_number = fields.Char('Serial Number', readonly=1)
    tr_product_id = fields.Many2one('product.template', 'Product', readonly=1)
    tr_product_price = fields.Float('Price', related='tr_product_id.standard_price', readonly=1)
    tr_pattern = fields.Char('Pattern', readonly=1)
    tr_otd = fields.Float('OTD', readonly=1)
    tr_rtd = fields.Float('RTD 1', readonly=1)
    tr_rtd_2 = fields.Float('RTD 2', readonly=1)
    tr_rtd_average = fields.Float('AVG RTD', readonly=1)
    tr_rtd_percentage = fields.Float('RTD (%)', readonly=1)
    tr_tur = fields.Float('TUR (%)', readonly=1)
    tr_pressure_hc = fields.Selection(selection=[
        ('hot', 'Hot'),
        ('cold', 'Cold')
    ], string='Pressure H/C', readonly=1)
    tr_pressure_hp = fields.Float('Pressure AP', readonly=1)
    tr_remove_price = fields.Float('Remove Price', readonly=1)
    tr_problem = fields.Char('Problem', readonly=1)
    tr_remarks = fields.Char('Remarks', readonly=1)

    # tyre_fitment
    tf_date = fields.Datetime('Date & Time', readonly=1)
    tf_tire_service_id = fields.Many2one('tire.service', readonly=1)
    tf_equipment_id = fields.Many2one(related='tf_tire_service_id.equipment_id', readonly=1)
    tf_pos = fields.Char('POS', readonly=1)
    tf_size = fields.Char('Size', readonly=1)
    tf_serial_number = fields.Char('Serial Number', readonly=1)
    tf_product_id = fields.Many2one('product.template', 'Product', readonly=1)
    tf_product_price = fields.Float('Price', related='tf_product_id.standard_price', readonly=1)
    tf_pattern = fields.Char('Pattern', readonly=1)
    tf_otd = fields.Float('OTD', readonly=1)
    tf_rtd = fields.Float('RTD 1', readonly=1)
    tf_rtd_2 = fields.Float('RTD 2', readonly=1)
    tf_rtd_average = fields.Float('AVG RTD', readonly=1)
    tf_rtd_percentage = fields.Float('RTD (%)', readonly=1)
    tf_tur = fields.Float('TUR (%)', readonly=1)
    tf_pressure_hc = fields.Selection(selection=[
        ('hot', 'Hot'),
        ('cold', 'Cold')
    ], string='Pressure H/C', readonly=1)
    tf_pressure_hp = fields.Float('Pressure AP', readonly=1)
    tf_install_price = fields.Float('Install Price', readonly=1)
    tf_tyre_type = fields.Selection([
        ('new', 'New'),
        ('spare', 'Spare'),
        ('repair', 'Repaired')
    ], 'Tyre Type', readonly=1)
    tf_remarks = fields.Char('Remarks', readonly=1)

    work_order_id = fields.Many2one('work.order', 'No. Work Order', related='tr_tire_service_id.work_order_id')
    kmhm_running = fields.Float(string="KM/HM Running", related='work_order_id.kmhm_running', readonly=1)
    meter_type = fields.Selection(selection=[('km', 'KM'), ('hm', 'HM'), ], related='work_order_id.meter_type', readonly=1)
    company_id = fields.Many2one('res.company', related='work_order_id.company_id')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                            with
                                cte_tr as (
                                    select
                                        date tr_date
                                        ,tire_service_id tr_tire_service_id
                                        ,pos tr_pos
                                        ,size tr_size
                                        ,serial_number tr_serial_number
                                        ,product_id tr_product_id
                                        ,pattern tr_pattern
                                        ,otd tr_otd
                                        ,rtd tr_rtd
                                        ,rtd_2 tr_rtd_2
                                        ,rtd_average tr_rtd_average
                                        ,rtd_percentage tr_rtd_percentage
                                        ,tur tr_tur
                                        ,pressure_hc tr_pressure_hc
                                        ,pressure_hp tr_pressure_hp
                                        ,remove_price tr_remove_price
                                        ,problem tr_problem
                                        ,remarks tr_remarks
                                    from tyre_removal tr
                            ),
                                cte_tf as (
                                    select
                                        date tf_date
                                        ,tire_service_id tf_tire_service_id
                                        ,pos tf_pos
                                        ,size tf_size
                                        ,serial_number tf_serial_number
                                        ,product_id tf_product_id
                                        ,pattern tf_pattern
                                        ,otd tf_otd
                                        ,rtd tf_rtd
                                        ,rtd_2 tf_rtd_2
                                        ,rtd_average tf_rtd_average
                                        ,rtd_percentage tf_rtd_percentage
                                        ,tur tf_tur
                                        ,pressure_hc tf_pressure_hc
                                        ,pressure_hp tf_pressure_hp
                                        ,install_price tf_install_price
                                        ,tyre_type tf_tyre_type
                                        ,remarks tf_remarks
                                    from tyre_fitment tf
                            )
                            select
                                ROW_NUMBER () OVER (
                                   ORDER BY tr_date
                                ) id,
                                *
                            from cte_tr
                            join cte_tf on cte_tr.tr_tire_service_id = cte_tf.tf_tire_service_id and cte_tr.tr_pos = cte_tf.tf_pos
            )""" % (self._table))

