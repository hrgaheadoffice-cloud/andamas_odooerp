# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class tbl_batch_notif_po(models.Model):
    _name = "tbl_batch_notif_po"
    _description = "Batch Notif PO"
    _order = "id desc"

    date = fields.Date(
        string="Tanggal",
        default=fields.Date.context_today
    )
    cek = fields.Char(
        string="Cek"
    )
    line_ids = fields.One2many(
        comodel_name="tbl_notif_po_user",
        inverse_name="detail_id",
        string="Line"
    )
    def action_get_data(self):
        for rec in self:
            if rec.line_ids:
                for line in rec.line_ids:
                    if line.line_ids:
                        line.line_ids.unlink()
                rec.line_ids.unlink()
            cari_user = self.env['res.users'].sudo().search([])
            if cari_user:
                # raise UserError(_(cari_user))
                for user in cari_user:
                    if user.company_ids:
                        # raise UserError(_(user.company_ids))
                        for comp in user.company_ids:
                            cari_po = self.env['purchase.order'].sudo().search([('company_id','=',comp.id),
                                    ('next_approver','=',user.id)])
                            # cari_po_appr = self.env['purchase.request'].sudo().search([('company_id','=',comp.id),
                            #         ('procurement_officer','=',user.id),('state','=','approved')])
                            # if cari_po or cari_po_appr:
                            if cari_po:
                                # raise UserError(_(cari_po))
                                notif_user = self.env['tbl_notif_po_user'].create({
                                    'user_id': user.id,
                                    'company_id': comp.id,
                                    'date': rec.date,
                                    'detail_id': rec.id,
                                })
                            if cari_po:
                                for po in cari_po:
                                    if po.order_line:
                                        for pol in po.order_line:
                                            notif_user_line = self.env['tbl_notif_po_detail'].create({
                                                'po_line_id': pol.id,
                                                'date': rec.date,
                                                'detail_id': notif_user.id,
                                            })
                            # if cari_po_appr:
                            #     for pr in cari_po_appr:
                            #         if pr.line_ids:
                            #             for prl in pr.line_ids:
                            #                 notif_user_line = self.env['tbl_notif_po_detail'].create({
                            #                     'pr_line_id': prl.id,
                            #                     'date': rec.date,
                            #                     'detail_id': notif_user.id,
                            #                 })

    # @api.model
    def schedule_get_data(self):
        # if not batch:
        batch = self.env['tbl_batch_notif_po'].create({
                                    'cek': 'bagus'
                                })
        batch_old = self.env['tbl_batch_notif_po'].sudo().search([('id','<',batch.id)])
        if batch_old:
            for rec in batch_old:
                if rec.line_ids:
                    for line in rec.line_ids:
                        if line.line_ids:
                            line.line_ids.unlink()
                    rec.line_ids.unlink()
                rec.unlink()
                
        # batch.date = datetime.date.today()
        # raise UserError(_('sssssssssssssss'))
        batch.action_get_data()
        if batch.line_ids:
            for line in batch.line_ids:
                line.action_send_email()

class tbl_notif_po_user(models.Model):
    _name = "tbl_notif_po_user"
    _description = "Notif PO User"
    _order = "id desc"

    detail_id = fields.Many2one(
        comodel_name="tbl_batch_notif_po",
        string="Detail",
        copy=False,
    )
    date = fields.Date(
        string="Tanggal",
        default=fields.Date.context_today
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
    )
    line_ids = fields.One2many('tbl_notif_po_detail', 'detail_id', string='Line')
    isi = fields.Html('Isi Template')

    def get_portal_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = 287  # Gantilah dengan ID aksi yang sesuai
        menu_id = 182    # Gantilah dengan ID menu yang sesuai
        
        # return f"{base_url}/web?#id={self.id}&action={action_id}&model=purchase.request&view_type=form&cids={self.company_id.id}&menu_id={menu_id}"
        return f"{base_url}/web#action={action_id}&model=purchase.order&view_type=list&cids={self.company_id.id}&menu_id={menu_id}"

    def action_send_email(self):
        for rec in self:
            rec.isi = ''
            judul = ''
            body = ''
            footer = ''
            if rec.line_ids:
                judul = '''<table class="MsoTableGrid" border="1" cellspacing="0" cellpadding="0" style="border: none;">
                    <tbody><tr>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">No</p><p></p><p></p>
                    </td>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
                    solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">Date</p><p></p><p></p>
                    </td>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
                    solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">PO NO</p><p></p><p></p>
                    </td>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
                    solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">Item</p><p></p><p></p>
                    </td>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
                    solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">Priority</p><p></p><p></p>
                    </td>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
                    solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">Quantity</p><p></p><p></p>
                    </td>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
                    solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">UoM</p><p></p><p></p>
                    </td>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
                    solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">Price</p><p></p><p></p>
                    </td>
                    <td valign="top" style="border:solid windowtext 1.0pt;
                    border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
                    solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                    <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                    line-height:normal">Total</p><p></p><p></p>
                    </td>
                    </tr>
                    '''
                footer = '</tbody></table>'
                no = 1
                for line in rec.line_ids:
                    tanggal_awal = str(line.date_start)
                    tanggal_objek = datetime.strptime(tanggal_awal, "%Y-%m-%d")
                    cari_language = self.env['res.lang'].sudo().search([('code','=',rec.user_id.lang)])
                    tanggal = tanggal_objek.strftime(str(cari_language.date_format))
                    estimated_price_unit = line.estimated_price_unit
                    formatted_estimated_price_unit = '{:,.0f}'.format(estimated_price_unit)
                    estimated_cost = line.estimated_cost
                    formatted_estimated_cost = '{:,.0f}'.format(estimated_cost)
                    priority = ''
                    if line.priority == 'normal':
                        priority = 'NORMAL'
                    elif line.priority == 'urgent':
                        priority = 'URGENT'
                    elif line.priority == 'top_urgent':
                        priority = 'TOP URGENT'

                    body += f'''
                            <tr>
                            <td valign="top" style="border:solid windowtext 1.0pt;
                            border-top:none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
                            padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{no}</p><p></p><p></p>
                            </td>
                            <td valign="top" style="border-top:none;border-left:none;
                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                            mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
                            mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{tanggal}</p><p></p><p></p>
                            </td>
                            <td valign="top" style="border-top:none;border-left:
                            none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                            mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
                            mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{line.po_id.name}</p><p></p><p></p>
                            </td>
                            <td valign="top" style="border-top:none;border-left:
                            none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                            mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
                            mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{line.product_id.display_name}</p><p></p><p></p>
                            </td>
                            <td valign="top" style="border-top:none;border-left:
                            none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                            mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
                            mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{priority}</p><p></p><p></p>
                            </td>
                            <td valign="top" style="border-top:none;border-left:
                            none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                            mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
                            mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{line.product_qty}</p><p></p><p></p>
                            </td>
                            <td valign="top" style="border-top:none;border-left:
                            none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                            mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
                            mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{line.product_uom_id.name}</p><p></p><p></p>
                            </td>
                            <td valign="top" style="border-top:none;border-left:
                            none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                            mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
                            mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{formatted_estimated_price_unit}</p><p></p><p></p>
                            </td>
                            <td valign="top" style="border-top:none;border-left:
                            none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                            mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
                            mso-border-alt:solid windowtext .5pt;padding:0cm 5.4pt 0cm 5.4pt">
                            <p class="MsoNormal" align="center" style="margin-bottom:0cm;text-align:center;
                            line-height:normal">{formatted_estimated_cost}</p><p></p><p></p>
                            </td>
                            </tr>
                        '''
                    no += 1
            rec.isi = str(judul)+str(body)+str(footer)

        template_id = self.env.ref("purchase_order_approved.email_template_notif_po").id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

class tbl_notif_po_detail(models.Model):
    _name = "tbl_notif_po_detail"
    _description = "Notif po"
    _order = "id desc"

    detail_id = fields.Many2one(
        comodel_name="tbl_notif_po_user",
        string="Detail",
        copy=False,
    )
    po_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="PO Line",
        copy=False,
    )
    po_id = fields.Many2one(
        related="po_line_id.order_id",
        string="PO NO",
    )
    date_start = fields.Date(
        string="Date",
        # related="po_id.date_order", 
        compute='_compute_date_start'
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        related="po_line_id.product_id",
    )
    priority = fields.Selection(
        selection=[
            ("normal", "NORMAL"),
            ("urgent", "URGENT"),
            ("top_urgent", "TOP URGENT"),],
        string="Priority",
        related="po_id.priority")
    product_qty = fields.Float(
        string="Qty", digits="Product Unit of Measure"
        ,related="po_line_id.product_qty"
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM"
        ,related="po_line_id.product_uom"
    )
    estimated_price_unit = fields.Float(
        string="Price Unit",
        currency_field="currency_id",
        default=0.0
        ,related="po_line_id.price_unit"
    )
    estimated_cost = fields.Monetary(
        string="Sub Total",
        currency_field="currency_id"
        ,related="po_line_id.price_subtotal"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="detail_id.company_id",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    
    date = fields.Date(
        string="Tanggal",
        default=fields.Date.context_today
    )

    def _compute_date_start(self):
        for record in self:
            if record.po_line_id:
                # Ambil tanggal dari datetime_field
                date_value = record.po_line_id.order_id.date_order.date()
                record.date_start = date_value
            else:
                record.date_start = False