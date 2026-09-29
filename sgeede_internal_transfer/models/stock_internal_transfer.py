from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import json
import time
import sys
sys.path.insert(0, '/opt/odoo-14.0/custom/msi_cs/models/')
# import tbl_msi_project


from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

from odoo import fields, models
from odoo.tools import float_compare
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import SUPERUSER_ID, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class StockInternalTransfer(models.Model):
	_name = 'stock.internal.transfer'
	_inherit = 'mail.thread'

	@api.model
	def _get_default_name(self):
		return self.env["ir.sequence"].next_by_code('stock.internal.transfer')

	@api.onchange('ekspedisi')
	def onchange_eta(self):
		def date_by_adding_business_days(from_date, add_days):
			business_days_to_add = add_days
			current_date = from_date
			while business_days_to_add > 0:
				current_date += relativedelta(days=1)
				weekday = current_date.weekday()
				if weekday >= 6: # sunday = 6
					continue
				business_days_to_add -= 1
			return current_date
		if self.ekspedisi:
			# date_1 = (datetime.strptime(str(self.create_date),
			#							 "%Y-%m-%d")+relativedelta(days=+ 0))
			date_2 = date_by_adding_business_days(fields.Date.today(), self.ekspedisi.eta)
			self.eta_date = date_2

	@api.model
	def create(self, vals):
		if vals.get("name", _("New")) == _("New"):
			vals["name"] = self._get_default_name()
		return super(StockInternalTransfer, self).create(vals)

	def action_cancel(self):
		if self.state in ['done', 'cancel']:
			raise UserError("Cannot cancel transfer in state {}".format(self.state))
		# create return if any picking
		if self.picking_ids:
			for picking in self.picking_ids:
				return_obj = self.env['stock.return.picking'].with_context(active_id=picking.id).create({
					'picking_id': picking.id,
					'location_id': picking.location_id.id
				})
				return_obj._onchange_picking_id()
				res = return_obj.create_returns()
				res_obj = self.env[res['res_model']].browse(res['res_id'])
				res_obj.force_validate()
		self.write({'state': 'cancel'})
		return True

	def action_confirm(self):
		for rec in self.line_ids:
			if rec.on_hand <= 1 :
				raise UserError('Qty %s Tidak tersedia pada source warehouse'%rec.product_id.name)
		self.write({'state': 'confirm'})
		return True

	
	def action_draft(self):
		self.write({'states': 'draft'})
		return True

	
	def action_send(self):
		self.write({'states': 'send'})
		return True

	
	def action_receive(self):
		for rec in self.picking_ids:
			if rec.state == 'assigned':
				rec.button_validate()
				rec._action_done()
				if rec.state == 'done':
					self.write({'state': 'done'})
		return True

	
	def do_enter_wizard(self):
		for rec in self.line_ids:
			stock = self.env['stock.quant'].search([('location_id', '=', self.source_warehouse_id.lot_stock_id.id), ('product_id', '=', rec.product_id.id)])
			if stock.quantity == 0 :
				raise UserError("Qty on hand dari %s di gudang %s tidak tersedia"%(str(rec.product_id.name),self.source_warehouse_id.name))

		ctx = dict(self._context)

		ctx.update({
			'active_model': self._name,
			'active_ids': self._ids,
			'active_id': len(self._ids) and self._ids[0] or False
			})

		created_id = self.env['wizard.stock.internal.transfer'].with_context(ctx).create({'transfer_id': len(self._ids) and self._ids or False}).id
		return self.env['wizard.stock.internal.transfer'].with_context(ctx).wizard_view(created_id)


	# name = fields.Char(string= 'Reference', track_visibility="onchange", default= lambda self: self.env['ir.sequence'].next_by_code('stock.internal.transfer') or '')
	name = fields.Char(
		string="Reference",
		required=True,
		default=lambda self: _("New"),
		tracking=True,
	)
	date = fields.Datetime(string= 'Date', track_visibility="onchange", default= lambda self: time.strftime('%Y-%m-%d %H:%M:%S'))
	source_warehouse_id = fields.Many2one('stock.warehouse', string="Source Warehouse", track_visibility="onchange")
	dest_warehouse_id = fields.Many2one('stock.warehouse', string="Destination Warehouse", track_visibility="onchange")
	state = fields.Selection([('draft', 'Draft'),('confirm', 'Confirm'), ('send', 'Send'), ('done', 'Done'), ('cancel', 'Cancel')], string="Status", track_visibility="onchange", default="draft")
	line_ids = fields.One2many('stock.internal.transfer.line', 'transfer_id', string="Stock Internal Transfer Line")
	picking_ids = fields.One2many('stock.picking', 'transfer_id', string="Picking")
	backorder_id = fields.Many2one('stock.internal.transfer', 'Backorder')
	no_resi = fields.Char('No Resi')
	ekspedisi = fields.Many2one("tbl_ekspedisi",'Ekspedisi')
	eta_date = fields.Date("ETA date")
	note = fields.Text('Notes')
	prepared_by = fields.Many2one(comodel_name="res.users",string="Prepared By",copy=False)
	prepare_dt = fields.Datetime('Prepare Datetime',copy=False)
	checked_by = fields.Many2one(comodel_name="res.users",string="Checked By",copy=False)
	checked_dt = fields.Datetime('Checked Datetime',copy=False)
	driver_by = fields.Many2one(comodel_name="res.users",string="Driver By",copy=False)
	driver_dt = fields.Datetime('Driver Datetime',copy=False)
	receiver_by = fields.Many2one(comodel_name="res.users",string="Receiver By",copy=False)
	receiver_dt = fields.Datetime('Receiver Datetime',copy=False)
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

class stock_internal_transfer(models.Model):
	_name = 'stock.internal.transfer.line'
	_inherit = 'mail.thread'

	@api.onchange('product_id')
	def product_id_change(self):

		result = {}
		if not self.product_id: {
			'product_uom_id': False,
		}
		product = self.env['product.product'].browse(self.product_id.id)

		product_uom_id = product.uom_id and product.uom_id.id or False

		result['value'] = {'product_uom_id': product_uom_id}
		return result
	
	@api.onchange('product_id')
	def onchange_product_id_warning(self):
		product_info = self.product_id
		# if self.product_id:
		# 	warning = {}
		# 	title = False
		# 	message = False


		# 	if product_info.sit_line_warn != 'no-message':
		# 		title = _("Warning for %s", product_info.name)
		# 		message = product_info.sit_line_warn_msg
		# 		warning['title'] = title
		# 		warning['message'] = message
		# 		if product_info.sit_line_warn == 'block':
		# 			self.product_id = False
		# 		return {'warning': warning}
		# 	return {}

	name = fields.Char(string="Reference", track_visibility='onchange')
	ket = fields.Text(string="Note", track_visibility='onchange')
	product_id = fields.Many2one('product.product', string="Product", track_visibility="onchange")
	product_qty = fields.Float(string="Quantity", track_visibility="onchange", default=1)
	product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure", track_visibility='onchange')
	product_sn = fields.Many2one('stock.production.lot', string="Serial Number", track_visibility='onchange')
	state = fields.Selection([('cancel', 'Cancel'), ('draft', 'Draft'), ('send', 'Send'), ('done', 'Done')],
		string="Status", track_visibility='onchange', default="draft")
	transfer_id = fields.Many2one('stock.internal.transfer', string="Transfer", track_visibility="onchange")
	on_hand = fields.Float('Qty On Hand', compute='_stock_compute')

	# masih ada bug, harus di save dulu baru muncul
	@api.depends('transfer_id','transfer_id.source_warehouse_id','product_id')
	def _stock_compute(self):
		for record in self:
			if record.transfer_id.source_warehouse_id:
				if record.product_id:
					stock = record.env['stock.quant'].search([('location_id', '=', record.transfer_id.source_warehouse_id.lot_stock_id.id), ('product_id', '=', record.product_id.id)])
					if stock:
						record.on_hand = stock.quantity
					else:
						record.on_hand = 0
				else:
					record.on_hand = 0
			else:
				record.on_hand = 0


class Ekspedisi(models.Model):
	_name = 'tbl_ekspedisi'

	name = fields.Char('Ekspedisi')
	eta = fields.Integer('Estimasi Waktu Tiba')

	

