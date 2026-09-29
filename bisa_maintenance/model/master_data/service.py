from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime
from datetime import date
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import calendar

import base64
from urllib.request import urlopen

class MaintenanceMasterService(models.Model):
	_name = "maintenance_master_service"
	_description = "Master Service"
	_rec_name = 'nama'

	# ONE2MANY
	sparepart_line_ids = fields.One2many('maintenance_master_sparepart_line', 'service_id', 'List Sparepart')
	jasa_line_ids = fields.One2many('maintenance_master_jasa_line', 'service_id', 'List Sparepart')

	template_id = fields.Char(string="Template ID")
	nama = fields.Char(string="Nama")
	unit = fields.Many2one('product.template',string="Product Asset")
	cycle = fields.Char(string="Cycle (Km/Hm)")
	service_type = fields.Selection([
		('preventive','Preventive'),
		('corrective','Corrective'),
		], string="Tipe Sevice")

class MaintenanceMasterSparepartLine(models.Model):
	_name = "maintenance_master_sparepart_line"
	_description = "Service Sparepart Line"

	service_id = fields.Many2one('maintenance_master_service',string="Service ID")

	produk = fields.Many2one('product.template',string="Product")
	uom = fields.Many2one('uom.uom',string="Unit of Measure", related='produk.uom_id')
	quantity = fields.Float(string="Quantity")

class MaintenanceMasterJasaLine(models.Model):
	_name = "maintenance_master_jasa_line"
	_description = "Service Sparepart Line"

	service_id = fields.Many2one('maintenance_master_service',string="Service ID")

	produk = fields.Many2one('product.template',string="Product")
	uom = fields.Many2one('uom.uom',string="Unit of Measure", related='produk.uom_id')
	quantity = fields.Float(string="Quantity")