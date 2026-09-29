from datetime import datetime
from odoo import fields,models,api, _
from odoo.exceptions import ValidationError

class wipManagement(models.Model):
    _name = 'wip.management'

    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']


   
    
    name = fields.Char()
    document_date = fields.Date()
    vendor_id = fields.Many2one('res.partner')
    project_code = fields.Many2one('wip.project')
    vessel_code = fields.Char(related='project_code.cargo_nomination')
    wip_amount = fields.Monetary()
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.company.currency_id.id)
    state = fields.Selection([('draft','Draft'),('posted','Posted')],default='draft')
    # journal_ids = fields.One2many('account.move.line','wip_id')
    # account_move_ids = fields.One2many("account.move", 'wip_id',string='Journal', copy=False,auto_join=True)
    # do_category = fields.Selection([('do_haulling','DO Haulling'),('do_coal','DO Coal'),('ds_barging','DS Barging'),('ds_surveyor_analysis','DS Surveyor Analysis'),
    #                                 ('do_hauiling_coal_transfer','DO Hauiling Coal Transfer'),
    #                                  ('do_terminal_handling','DO Terminal Handling'),
    #                                  ('ds_floating_crane','DS Floating Crane'),
    #                                  ('ds_stevedooring','DS Stevedooring')
    #                                 ])
    journal_ids =  fields.One2many("account.move.line",'wip_id',string='Journal Items', copy=False,auto_join=True,related='account_move_id.line_ids',store=True)
    do_code = fields.Char("DO Code")
    journal_id = fields.Many2one('account.journal',string='Journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain="[('company_id', '=', company_id), ('code', '=', 'WIP')]")
    account_move_id = fields.Many2one('account.move',copy=False)
    qty = fields.Float()
    bill_id = fields.Many2one('account.move',copy=False)
    is_vendor_bill = fields.Boolean(default=False,copy=False)
    do_category_id = fields.Many2one('do.category')
    hide_vendor_bill_button = fields.Boolean(compute='_compute_hide_vendor_bill_button')
    product_id = fields.Char()
    wip_total_amount = fields.Monetary(compute='_compute_wip_total_amount',store=True)


    @api.depends('qty','wip_amount')
    def _compute_wip_total_amount(self):
        for data in self:
            if data.qty and data.wip_amount:
                data.wip_total_amount = data.qty * data.wip_amount
            else:
                data.wip_total_amount = 0


    
    @api.depends('state','is_vendor_bill')
    def _compute_hide_vendor_bill_button(self):
        for data in self:
            if data.state:
                if data.state == 'draft':
                    data.hide_vendor_bill_button = True
                    
                if data.state == 'posted' and not data.is_vendor_bill:
                    data.hide_vendor_bill_button = False
                
                if data.state == 'posted' and data.is_vendor_bill:
                    data.hide_vendor_bill_button = True
                
            else:
                data.hide_vendor_bill_button = True
        
    
    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
                wizard.journal_id = self.env['account.journal'].search([
                    ('code', '=', 'WIP'),
                    ('company_id', '=', wizard.company_id.id),
                ], limit=1)
                
                
    def create_vendor_bill(self):
        bill_line = []
        origin_list = []
        account_jrnl_obj = self.env['account.journal'].search(
            [('type', '=', 'purchase')])
        for data in self:
            origin_list.append(data.name)
            bill_line.append((0,0,{
                'name': f'{data.name}' or "",
                # 'origin': f'{data._name}' or "",
                'quantity': data.qty,
                'account_id': data.do_category_id.accrue_account_id.id,
                'price_unit': data.wip_amount,
            }
                             ))
        inv_values = {
        # 'origin': ','.join(origin_list),
        'move_type': 'in_invoice',
        'partner_id': self.vendor_id.id,
        'invoice_line_ids': bill_line,
        'invoice_date': datetime.now(),
        'ref':  ','.join(origin_list),
        'journal_id': account_jrnl_obj and
        account_jrnl_obj.ids[0] or False,
    }

        vendor_bill_id = self.env['account.move'].create(inv_values)
        self.bill_id = vendor_bill_id.id
        self.is_vendor_bill =  True
        view_ids = self.env['ir.ui.view'].search([('name', '=', 'account.move.form'), ('mode', '=', 'primary')]).id
        return {
            'name': _('Vendor Bill'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': view_ids,
            'res_model': 'account.move',
            'res_id': vendor_bill_id.id,
            'context': {},
            'domain': [],
            'target': 'current'
        }
    
    def has_only_one_vendor(self,list):
        return len(set(list)) == 1
            
    def create_vendor_bill_bulk(self):
        bill_line = []
        origin_list = []
        account_jrnl_obj = self.env['account.journal'].search(
            [('type', '=', 'purchase')])
        active_ids = self.env.context.get('active_ids')
        to_create = self.browse(active_ids)
        check_wip_bill =  to_create.filtered(lambda line:line.is_vendor_bill)
        
        vendor_ids = [line.vendor_id.id for line in to_create]
        if not self.has_only_one_vendor(vendor_ids):
            raise ValidationError("Vendor harus sama!")
        
        if check_wip_bill:
            raise ValidationError("Ada WIP yang sudah di buatkan vendor bill !")
        for data in to_create:
            origin_list.append(data.name)
            bill_line.append((0,0,{
                'name': f'{data.name}' or "",
                # 'origin': f'{data._name}' or "",
                'quantity': data.qty,
                'account_id': data.do_category_id.accrue_account_id.id,
                'price_unit': data.wip_amount,
            }
                             ))
        inv_values = {
        # 'origin': ','.join(origin_list),
        'move_type': 'in_invoice',
        'partner_id': to_create[0].vendor_id.id,
        'invoice_line_ids': bill_line,
        'invoice_date': datetime.now(),
        'ref':  ','.join(origin_list),
        'journal_id': account_jrnl_obj and
        account_jrnl_obj.ids[0] or False,
    }

        vendor_bill_id = self.env['account.move'].create(inv_values)

        for result in to_create:
            result.bill_id = vendor_bill_id.id
            result.is_vendor_bill = True
        
        

    def action_post(self):
        self.ensure_one()
        line_ids = []
        line_ids.append((0, 0, {
                        # 'product_id': alldata.product_id.id,
                        'account_id': self.do_category_id.wip_account_id.id,
                        'quantity': 1,
                        'credit': 0.0,
                        'debit': self.wip_amount * self.qty,
                        'amount_currency': self.wip_amount * self.qty,
                        'currency_id':self.currency_id.id,
                        'partner_id': self.vendor_id.id,
                    }))
        line_ids.append((0, 0, {
                        # 'product_id': alldata.product_id.id,
                        'account_id': self.do_category_id.accrue_account_id.id,
                        'quantity': 1,
                        'credit': self.wip_amount * self.qty, 
                        'debit': 0.0,
                        'amount_currency': self.wip_amount,
                        'currency_id':self.currency_id.id,
                        'partner_id': self.vendor_id.id,
                    }))

        if self.do_category_id.name == 'DO Coal':
            line_ids = []
            company_id = self.company_id.id
            product_id = self.product_id.split('-')
            wip_account = self.env['account.account'].sudo().search([('name', 'like', product_id[-1]), ('name', 'like', 'WIP'), ('company_id', '=', company_id)]).id
            accrue_account = self.env['account.account'].sudo().search([('code', '=', '2104119'), ('company_id', '=', company_id)]).id
            if 'EHP' in self.product_id:
                wip_account = self.env['account.account'].sudo().search([('code', '=', '110411'), ('company_id', '=', company_id)]).id
            line_ids.append((0, 0, {
                # 'product_id': alldata.product_id.id,
                'account_id': wip_account,
                'quantity': 1,
                'credit': 0.0,
                'debit': self.wip_amount * self.qty,
                'amount_currency': self.wip_amount * self.qty,
                'currency_id': self.currency_id.id,
                'partner_id': self.vendor_id.id,
            }))
            line_ids.append((0, 0, {
                # 'product_id': alldata.product_id.id,
                'account_id': accrue_account,
                'quantity': 1,
                'credit': self.wip_amount * self.qty,
                'debit': 0.0,
                'amount_currency': self.wip_amount,
                'currency_id': self.currency_id.id,
                'partner_id': self.vendor_id.id,
            }))

        move_vals = {
            'ref': self.name,
            'date': fields.Datetime.now(),
            'journal_id': self.journal_id.id,
            'line_ids': line_ids,
            'name': '/',
            'move_type': 'entry',
            'partner_id': self.vendor_id.id,
            'invoice_date': fields.Datetime.now(),
            'currency_id': self.currency_id.id,
        }
        entry_id = self.env['account.move'].create(move_vals)
        entry_id.action_post()
        self.account_move_id = entry_id.id
        self.write({'state':'posted'})
        self.env.cr.commit()
        cogs_data =  self.env['cogs.management'].sudo().search([('project_code_id','=',self.project_code.id)],limit=1)
        if cogs_data:
            for line in cogs_data.wip_detail_ids:
                line._compute_amount()
            cogs_data._compute_wip_total()
        inventory = self.env['stock.inventory'].create({
            'name': 'Inventory adjustment'
        })

        product = self.env['product.product'].search([('name','=',self.product_id)],limit=1)
        if self.do_category_id.name in ('DO Hauling', 'DO Coal'):
            if product:
                location = self.env['stock.location'].sudo().search([('name','=','Stock'),('usage','=','internal'),('company_id','=',self.company_id.id)],limit=1)
                # self.env['stock.inventory.line'].create({
                #         'product_id': product.id,
                #         'product_uom_id': product.uom_po_id.id,
                #         'inventory_id': inventory.id,
                #         'product_qty': product.qty_available + self.qty,
                #         'location_id': location.id,
                #     })
                # inventory._action_start()
                # inventory.action_validate()
                in_moves = self.env['stock.move'].create({
                    'name': 'IN move',
                    'product_id': product.id,
                    'location_id': self.env.ref('stock.stock_location_suppliers').id,
                    'location_dest_id': location.id,
                    'product_uom': product.uom_po_id.id,
                    'product_uom_qty': self.qty,
                    'price_unit': self.wip_amount,
                })
                in_moves._action_confirm()
                in_moves.quantity_done = self.qty
                in_moves._action_done()
                # in_moves.cogs_price = product.standard_price
        
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('wip.management')
        res = super(wipManagement, self).create(vals)
        return res
    
    


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    wip_id = fields.Many2one('wip.management',index=True,ondelete='restrict')
    project_code = fields.Char()
    
    
    
class AccountMove(models.Model):
    _inherit = 'account.move'

    wip_id = fields.Many2one('wip.management',string='Cash Advance',index=True,ondelete='restrict')