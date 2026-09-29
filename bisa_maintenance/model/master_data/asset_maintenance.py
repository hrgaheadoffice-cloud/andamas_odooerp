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
import requests
import json
import hashlib


class MasterAssetMaintenance(models.Model):
    _name = "master_asset_maintenance"
    _description = "Master Asset Maintenance"
    _rec_name = 'nama_asset'
    _order = 'nama_asset'

    _sql_constraints = [
        ('equipment_uniq',
         'unique(equipment_id)',
         'Choose another value for "Equipment ID" field, it has to be unique!'),
        ('asset_uniq',
         'unique(nama_asset)',
         'Choose another value for "Unit Code" field, it has to be unique!')
    ]

    @api.depends('hm', 'km')
    def _compute_hm_km(self):
        for rec in self:
            rec.hm_km = str(rec.hm) + "/" + str(rec.km)

    # HISTORY
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,default=lambda self: self.env.company)
    history_location_lines = fields.One2many('master_history_location', 'asset_id', 'History Location')
    document_lines = fields.One2many('master_document', 'asset_id', 'Document')
    history_usage_lines = fields.One2many('master_history_usage', 'asset_id', 'History Usage')
    history_maintenance_lines = fields.One2many('work.order', 'equipment_id', 'History Maintenance')
    detail_service = fields.One2many('tbl_mnt_request', 'details_asset', 'History service')

    # IDENTITAS
    kat_asset = fields.Many2one('asset_maintenance_kategori', string="Asset Name")
    no_asset = fields.Char(string="Asset Number", default='/', readonly=True)
    nama_asset = fields.Char(string="Unit Code")
    product_asset = fields.Many2one('product.template', string="Unit")
    own_status = fields.Selection([
        ('Owned', 'Owned'),
        ('Rental', 'Rental'),
    ], string='Ownership', copy=False, index=True, tracking=True, default='Owned')
    rental_detail = fields.One2many('aset_rental_line', 'details', 'Rental Detail')
    plat_no = fields.Char(string="License Plate")
    merek = fields.Char(string="Merk")
    brand = fields.Many2one('brand')
    tipe = fields.Char(string="Model")
    model = fields.Many2one('model', domain="[('brand', '=', brand)]")
    tahun_buat = fields.Char(string="Manufacture Year")
    # warna = fields.Many2one('tbl_mnt_warna',string="Color")
    no_mesin = fields.Char(string="Machine Number")
    no_rangka = fields.Char(string="VIN")
    detail = fields.Text('Detail')

    # STATUS
    tgl_beli = fields.Date(string="Purchase Date")
    nama_vendor = fields.Many2one('res.partner', string="Vendor Name")
    state = fields.Selection([
        ('draft', 'New'),
        ('running', 'Running'),
        ('service', 'in Service'),
        ('standby', 'Standby'),
        ('broken', 'Disposal'),
    ], string='Status', copy=False, index=True, tracking=True, default='draft', readony=True)
    tgl_serah_terima_update = fields.Date('Tanggal ST Terkini', index=True, help='Tanggal Serah Terima terkini',
                                          readony=True)
    lokasi_update = fields.Char(string="Lokasi Terkini")
    pic_update = fields.Many2one('hr.employee', 'PIC terkini', readony=True)

    lokasi = fields.Many2one('tbl_aset_lokasi', string="Lokasi")
    harga_beli = fields.Float(string="Harga Beli")
    acc_asset_id = fields.Many2one('account.asset', 'Asset Akuntansi')
    kmhm_running = fields.Float(string="KM/HM Running")
    meter_type = fields.Selection(selection=[('km', 'KM'), ('hm', 'HM'), ], default='km', )
    is_in_service_periodic = fields.Boolean(compute='_compute_in_service_periodic')
    driver = fields.Many2one('hr.employee', 'Driver name', readony=True)
    hm = fields.Float()
    km = fields.Float()
    hm_km = fields.Char('HM/KM', compute=_compute_hm_km)
    used_to = fields.Selection([
        ('rental', 'Rental'),
        ('hauling', 'Hauling')
    ])
    daily_rent_price = fields.Float()
    hour_rent_price = fields.Float()
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        auto_join=True, index=True, ondelete="cascade")
    category = fields.Many2one('master.asset.category')
    category_class = fields.Char()
    plotting_location = fields.Many2one('hr.employee.category')
    plotting_function = fields.Char()
    equipment_id = fields.Char()
    unit_status = fields.Selection([
        ('mt', 'Maintenance'),
        ('mt_period', 'Maintenance Period'),
        ('need_mt', 'Need Maintenance'),
        ('running', 'Running'),
    ])
    bd_date = fields.Datetime()
    problem = fields.Char()

    timesheet_equipment_ids = fields.One2many('tbl_mnt_timesheet_equipment', 'name')
    periodic_calculation_plan_ids = fields.One2many('periodic.calculation.plan', 'unit_code')

    def write(self, vals):
        res = super(MasterAssetMaintenance, self).write(vals)
        if self.state != 'draft' and not (len(vals) == 1 and not (not (vals.get('kmhm_running')))):
            # generate token
            token = self.action_generate_token()

            data = json.dumps({
                "category": self.category.name,
                "category_class": self.category_class,
                "equipment_id": self.equipment_id,
                "unit_code": self.nama_asset,
                "asset_name": self.kat_asset.name,
                "brand": self.brand.name,
                "model": self.model.name,
                "manufacture_year": self.tahun_buat,
                "plotting_location": self.plotting_location.name,
                "plotting_function": self.plotting_function,
                "lokasi": self.lokasi.name,
                "state": dict(self._fields['state'].selection).get(self.state).upper(),
                "date_time": (self.bd_date + timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%S") if self.bd_date else None,
                "problem": self.problem if self.problem else None,
                "token": token
            })

            headers = {
                'Content-Type': 'application/json'
            }
            url = "http://103.174.114.79:85/api/Equipment" #dev
            # url = "http://103.174.114.79:83/api/Equipment" #prod
            response = requests.request("POST", url, headers=headers, data=data)
            if response.status_code == 200:
                return
            elif response.status_code == 400:
                raise ValidationError("Integration with smartmining error \n%s" % (response.text))
            else:
                raise ValidationError("Integration with smartmining error")
        return res

    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the maintenance views.
        """
        self.check_access_rights('read')

        result = {
            'all_under_maintenance': 0,
            'all_under_maintenance_period': 0,
            'all_immediately_need': 0,
            'all_safe_running': 0,
        }

        all_under_maintenance = self.search_count([('unit_status', '=', 'mt'),])
        all_under_maintenance_period = self.search_count([('unit_status', '=', 'mt_period'),])
        all_immediately_need = self.search_count([('unit_status', '=', 'need_mt'),])
        all_safe_running = self.search_count([('unit_status', '=', 'running'),])
        result.update({
            'all_under_maintenance': all_under_maintenance,
            'all_under_maintenance_period': all_under_maintenance_period,
            'all_immediately_need': all_immediately_need,
            'all_safe_running': all_safe_running,
        })

        return result

    def compute_unit_status(self):
        for me in self:
            under_maintenance = self.env['work.order'].search_count([('equipment_id', '=', me.id), ('status', 'in', ['open', 'rfu', 'pending']), ('maintenance_type', '!=', 'preventive')])
            under_maintenance_period = self.env['work.order'].search_count([('equipment_id', '=', me.id), ('status', 'in', ['open', 'rfu', 'pending']), ('maintenance_type', '=', 'preventive')])
            immediately_need = self.env['tbl_mnt_timesheet_equipment'].search_count([('name', '=', me.id), ('plan_bd', '=', True)])
            if under_maintenance:
                me.unit_status = 'mt'
            elif under_maintenance_period:
                me.unit_status = 'mt_period'
            elif immediately_need:
                me.unit_status = 'need_mt'
            elif me.state == 'running':
                me.unit_status = 'running'
            else:
                me.unit_status = False

    def action_submit(self):
        for rec in self:
            rec.write({
                'state': 'running',
                'no_asset': self.env['ir.sequence'].next_by_code('asset_mnt')
            })

    def action_standby(self):
        self.state = 'standby'

    def action_disposal(self):
        self.state = 'broken'

    def action_running(self):
        self.state = 'running'

    def _compute_in_service_periodic(self):
        params = self.env['ir.config_parameter'].sudo()
        service_periodic_schedule = params.get_param('service_periodic_schedule', "5000")
        max_kmhm = service_periodic_schedule + 1
        max_unit = self.search_read([], ['kmhm_running'], order='kmhm_running desc', limit=1)
        if max_unit:
            max_kmhm = max_unit[0]['kmhm_running'] + 1

        service_periodic_schedule = [x for x in range(service_periodic_schedule, max_kmhm, service_periodic_schedule)]
        km_min_warning = int(params.get_param('km_min_warning', "500"))
        km_max_warning = int(params.get_param('km_max_warning', "300"))
        hm_min_warning = int(params.get_param('hm_min_warning', "25"))
        hm_max_warning = int(params.get_param('hm_max_warning', "15"))
        for me in self:
            is_in_service_periodic = False
            min_warn = km_min_warning
            max_warn = km_max_warning
            meter = me.kmhm_running
            if me.meter_type == "hm":
                min_warn = hm_min_warning
                max_warn = hm_max_warning
                meter *= 20
            for periodic in service_periodic_schedule:
                if (periodic - min_warn) <= meter <= (periodic + max_warn):
                    is_in_service_periodic = True
                    break
            me.is_in_service_periodic = is_in_service_periodic
        return

    def action_generate_token(self):
        day = date.today().day
        month = date.today().month
        year = date.today().year
        a = day + (3 + 5) * 1
        b = month + (3 * 7) - 1
        c = year + (7 - 1) * 5
        d = year * (year + a)
        e = d * b + (c * c)
        token = f"b04bd{a}c9503d547b{b}d8c9e160b52{c}580d54{d}b04bd34c9503d547b26d8c9e160b522054580d54{e}"
        token = hashlib.sha256(token.encode()).hexdigest()
        return token


class asset_maintenance_kategori(models.Model):
    _name = "asset_maintenance_kategori"
    _description = "asset_maintenance_kategori"
    # _rec_name = 'display_name'

    name = fields.Char(string="Name")
# parent = fields.Many2one('asset_maintenance_kategori',string="Parent")
# display_name = fields.Char(string="Display_name",compute="compute_display_name", store=True)

# @api.depends('name','parent')
# def compute_display_name(self):
# 	for rec in self:
# 		if rec.name and not rec.parent:
# 			rec.display_name = rec.name
# 		elif rec.name and rec.parent:
# 			rec.display_name = rec.parent.name +'-'+rec.name
# 		else:
# 			rec.display_name = ''


class tbl_mnt_warna(models.Model):
    _name = "tbl_mnt_warna"
    _description = "tbl_mnt_warna"

    name = fields.Char(string="Name")


class aset_rental_line(models.Model):
    _name = "aset_rental_line"
    _description = "aset_rental_line"
    # _order = "id desc"

    # ASSET ID
    details = fields.Many2one('master_asset_maintenance', string="Detail Aset")

    tanggal_mulai = fields.Date(string="Tanggal Mulai")
    tanggal_akhir = fields.Date(string="Tanggal Akhir")
    vendor = fields.Many2one('res.partner', string="Vendor")
    no_kontrak = fields.Char(string="No kontrak")
    nama_asset = fields.Char(string="Name", related='details.nama_asset', store=True)
    ket = fields.Char(string="Keterangan")
    attachment_ids = fields.Many2many(comodel_name="ir.attachment", string="Attachment", )



class MasterDocument(models.Model):
    _name = "master_document"
    _description = "Master Document Asset"

    asset_id = fields.Many2one('master_asset_maintenance', string="Asset ID")

    name = fields.Char()
    attachment_ids = fields.Many2many(comodel_name="ir.attachment", string="Attachment", )


class MasterHistoryLocation(models.Model):
    _name = "master_history_location"
    _description = "Master Asset History Location"
    # _order = "id desc"

    # ASSET ID
    asset_id = fields.Many2one('master_asset_maintenance', string="Asset ID")

    lokasi = fields.Many2one('tbl_aset_lokasi', 'Lokasi')
    pic = fields.Many2one('hr.employee', 'PIC')
    tanggal_serah_terima = fields.Date('Tanggal Serah Terima', required=True)
    status = fields.Selection([
        ('draft', 'New'),
        ('running', 'Running'),
        ('repair', 'in Repair'),
        ('broken', 'Broken'),
    ], string='Status Aset', copy=False, index=True, tracking=True, default='draft')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', copy=False, index=True, tracking=True, default='draft')
    is_submit = fields.Boolean('Submit')

    def action_submit(self):
        for rec in self:
            if rec.lokasi:
                rec.is_submit = True
                rec.asset_id.lokasi = rec.lokasi.id


class MasterHistoryUsage(models.Model):
    _name = "master_history_usage"
    _description = "Master Asset History Usage"
    # _order = "id desc"

    # ASSET ID
    asset_id = fields.Many2one('master_asset_maintenance', string="Asset ID")

    tanggal = fields.Date(string="Tanggal")
    km_hm_awal = fields.Char(string="Km/Hm Awal")
    km_hm_akhir = fields.Char(string="Km/Hm Akhir")
    user = fields.Char(string="User")


class MasterHistoryMaintenance(models.Model):
    _name = "master_history_maintenance"
    _description = "Master Asset History Maintenance"
    # _order = "id desc"

    # ASSET ID
    asset_id = fields.Many2one('master_asset_maintenance', string="Asset ID")

    # DETAIL
    history_maintenance_detail = fields.One2many('history_maintenance_detail', 'history_mt_id', 'History Detail')

    tanggal = fields.Date(string="Tanggal")
    deskripsi = fields.Char(string="Deskripsi")
    tipe_mt = fields.Char(string="Tipe Maintenance")
    nama_vendor = fields.Char(string="Nama Vendor")
    tgl_jam_masuk = fields.Datetime(string="Tanggal, Jam Masuk")
    tgl_jam_keluar = fields.Datetime(string="Tanggal, Jam Keluar")
    mekanik = fields.Char(string="Mekanik")


class HistoryMaintenanceDetail(models.Model):
    _name = "history_maintenance_detail"
    _description = "Master Asset History MT Detail"
    # _order = "id desc"

    # HISTORY ID
    history_mt_id = fields.Many2one('master_history_maintenance', string="History MT ID")

    tanggal = fields.Date(string="Tanggal")
    no_po = fields.Char(string="Nomor PO")
    nama_part = fields.Char(string="Nama Part")
    quantity = fields.Integer(string="Quantity")
    price_unit = fields.Integer(string="Price/Unit")
    price_total = fields.Integer(string="Price Total", compute="compute_price_total", store=True)

    @api.depends('price_unit', 'quantity')
    def compute_price_total(self):
        for rec in self:
            if rec.quantity and rec.price_unit:
                rec.price_total = rec.quantity * rec.price_unit
                

class MasterAssetCategory(models.Model):
    _name = "master.asset.category"
    _description = "Master Asset Category"

    name = fields.Char()
    incoming_account = fields.Many2one('account.account', 'Incoming Account')
    outgoing_account = fields.Many2one('account.account', 'Outgoing Fuel')
    outgoing_product = fields.Many2one('account.account', 'Outgoing Product')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    category_ids = fields.Many2many(
        'hr.employee.category', 'employee_category_rel',
        'emp_id', 'category_id', groups="hr.group_hr_manager,hr.group_hr_user",
        string='Tags')

