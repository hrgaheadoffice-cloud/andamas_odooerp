from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests
import json

class cogsManagement(models.Model):
    _name = 'cogs.management'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
                wizard.journal_id = self.env['account.journal'].search([
                    ('code', '=', 'COGS'),
                    ('company_id', '=', wizard.company_id.id),
                ], limit=1)
    
    name = fields.Char()
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    main_currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.company.currency_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.company.currency_id.id)
    account_move_id = fields.Many2one('account.move',copy=False)
    journal_id = fields.Many2one('account.journal',string='Journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain="[('company_id', '=', company_id), ('code', '=', 'COGS')]")
    project_code_id = fields.Many2one('wip.project')
    document_date = fields.Date()
    vessel_code = fields.Char(related='project_code_id.cargo_nomination',store=True)
    term_shipment = fields.Char(related='project_code_id.term',store=True)
    customer_code = fields.Many2one('res.partner',related='project_code_id.partner_id',store=True)
    contract_number = fields.Char(related='project_code_id.contract_number',store=True)
    qty = fields.Float()
    revenue = fields.Monetary(currency_field='currency_id')
    revenue_idr = fields.Monetary(currency_field='main_currency_id',compute='_compute_revenue_idr')
    exchange_rate = fields.Monetary(currency_field='main_currency_id',compute='_compute_exchange_rate',store=True)
    state = fields.Selection([('draft','Draft'),('close','Closed')],default='draft')
    wip_detail_ids = fields.One2many('wip.detail','cogs_id')
    wip_total = fields.Monetary(compute='_compute_wip_total',store=True,currency_field='main_currency_id')
    journal_ids =  fields.One2many("account.move.line",'cogs_id',string='Journal Items', copy=False,auto_join=True,related='account_move_id.line_ids',store=True)
    price_mt = fields.Monetary(currency_field='main_currency_id')
    cos_total = fields.Monetary(currency_field='main_currency_id')
    cogs_amount = fields.Monetary(currency_field='main_currency_id')
    hauling_stockpille = fields.Monetary(currency_field='main_currency_id')
    terminal_handling = fields.Monetary(currency_field='main_currency_id')
    haulling_36_port = fields.Monetary(currency_field='main_currency_id')
    barging = fields.Monetary(currency_field='main_currency_id')
    floating_crane = fields.Monetary(currency_field='main_currency_id')
    coal_purchase = fields.Monetary(currency_field='main_currency_id')
    surveyor = fields.Monetary(currency_field='main_currency_id')
    coal_lcv = fields.Monetary(currency_field='main_currency_id')
    coal_mcv = fields.Monetary(currency_field='main_currency_id')
    coal_hcv = fields.Monetary(currency_field='main_currency_id')
    consultant = fields.Monetary(currency_field='main_currency_id')
    stevedooring = fields.Monetary(currency_field='main_currency_id')
    cos_mt = fields.Monetary(currency_field='main_currency_id')
    gross_margin =fields.Monetary(currency_field='main_currency_id')
    percent = fields.Char()
    margin_mt = fields.Float()
    
    
    @api.depends('revenue','currency_id')
    def _compute_revenue_idr(self):
        for data in self:
            if data.revenue and data.currency_id:
                if data.currency_id.name != 'IDR':
                    data.revenue_idr =  data.revenue * data.exchange_rate
                else:
                    data.revenue_idr = data.revenue
            else:
                data.revenue_idr = 0
    
    @api.depends('currency_id','document_date')
    def _compute_exchange_rate(self):
        for data in self:
            if data.currency_id and data.document_date:
                if data.currency_id.name != 'IDR':
                    data.exchange_rate = data.currency_id._convert(
                    from_amount=1,
                    to_currency = data.company_id.currency_id,
                    company=data.company_id,
                    date=data.document_date,
                    round = True
                     )
                    
                else:
                    data.exchange_rate =1
            else:
                data.exchange_rate = 0
    
    
    @api.depends('wip_detail_ids')
    def _compute_wip_total(self):
        for data in self:
            if data.wip_detail_ids:
                data.wip_total =  (sum(data.amount for data in self.wip_detail_ids))
            else:
                data.wip_total = 0 
                

    
    
    def action_post(self):
        self.ensure_one()
        self.document_date = fields.Date.today()
        location = self.env['stock.location'].sudo().search([('name','=','Stock'),('usage','=','internal'),('company_id','=',self.company_id.id)],limit=1)
        # mcv = self.env['product.line'].sudo().search([('product_id.name','=','COAL-MCV'),('invoice_id.project_code','=',self.project_code_id.id),('invoice_id.journal_id.name','=','AR Commercial')],limit=1)
        # if mcv:
        #     out_moves_mcv = self.env['stock.move'].create({
        #             'name': 'OUT move',
        #             'product_id': mcv.product_id.id,
        #             'location_id':location.id,
        #             'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        #             'product_uom': mcv.product_id.uom_po_id.id,
        #             'product_uom_qty': mcv.quantity,
        #             'price_unit':mcv.product_id.standard_price,
        #         })
        #     out_moves_mcv._action_confirm()
        #     out_moves_mcv.quantity_done = self.qty
        #     out_moves_mcv._action_done()
        #
        # lcv = self.env['product.line'].sudo().search([('product_id.name','=','COAL-LCV'),('invoice_id.project_code','=',self.project_code_id.id),('invoice_id.journal_id.name','=','AR Commercial')],limit=1)
        # if lcv:
        #     out_moves_lcv = self.env['stock.move'].create({
        #             'name': 'OUT move',
        #             'product_id': lcv.product_id.id,
        #             'location_id':location.id,
        #             'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        #             'product_uom': lcv.product_id.uom_po_id.id,
        #             'product_uom_qty': lcv.quantity,
        #             'price_unit':lcv.product_id.standard_price,
        #         })
        #     out_moves_lcv._action_confirm()
        #     out_moves_lcv.quantity_done = self.qty
        #     out_moves_lcv._action_done()

        line_ids = []
        hauling_amount = 0

        move_id = self.env['account.move'].sudo().search([('project_code', '=', self.project_code_id.id), ('journal_id.name', '=', 'AR Commercial')], limit=1)

        for product in move_id.product_line_ids:
            out_moves = self.env['stock.move'].create({
                    'name': 'OUT move',
                    'product_id': product.product_id.id,
                    'location_id': location.id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                    'product_uom': product.product_id.uom_po_id.id,
                    'product_uom_qty': product.quantity,
                    'price_unit': product.product_id.standard_price,
                })
            out_moves._action_confirm()
            out_moves.quantity_done = self.qty
            out_moves._action_done()

            h_product_name = 'H' + product.product_id.name
            h_product_id = self.env['product.product'].search([('name', '=', h_product_name)])
            h_out_moves = self.env['stock.move'].create({
                    'name': 'OUT move',
                    'product_id': h_product_id.id,
                    'location_id': location.id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                    'product_uom': h_product_id.uom_po_id.id,
                    'product_uom_qty': product.quantity,
                    'price_unit': h_product_id.standard_price,
                })
            h_out_moves._action_confirm()
            h_out_moves.quantity_done = self.qty
            h_out_moves._action_done()
            hauling_amount += product.quantity * h_product_id.standard_price

        cos_coal_mcv  = self.env['account.account'].sudo().search([('code','=','51001101'),('company_id','=',self.env.company.id)],limit=1)
        wip_detail_mcv = self.env['wip.detail'].sudo().search([('account_id.code','=','110408'),('cogs_id','=',self.id)])

        mcv_ar = self.env['product.line'].sudo().search([('product_id.name','like','MCV'),('invoice_id.project_code','=',self.project_code_id.id),('invoice_id.journal_id.name','=','AR Commercial')])

        if cos_coal_mcv and wip_detail_mcv:
            mcv_amount = 0
            if mcv_ar:
                for me in mcv_ar:
                    if 'EHP' not in me.product_id.name:
                        mcv_amount += me.quantity * me.product_id.standard_price
            self.coal_mcv = -mcv_amount
            
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': cos_coal_mcv.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': mcv_amount,
                            'amount_currency': mcv_amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_detail_mcv.account_id.id,
                            'quantity': 1,
                            'credit':  mcv_amount, 
                            'debit': 0.0,
                            'amount_currency':mcv_amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))

        cos_coal_ehp  = self.env['account.account'].sudo().search([('code','=','51002313'),('company_id','=',self.env.company.id)],limit=1)
        wip_detail_ehp = self.env['wip.detail'].sudo().search([('account_id.code','=','110411'),('cogs_id','=',self.id)])

        ehp_ar = self.env['product.line'].sudo().search([('product_id.name','like','EHP'),('invoice_id.project_code','=',self.project_code_id.id),('invoice_id.journal_id.name','=','AR Commercial')])

        if cos_coal_ehp and wip_detail_ehp:
            ehp_amount = 0
            if ehp_ar:
                for me in ehp_ar:
                    ehp_amount += me.quantity * me.product_id.standard_price
            self.consultant = -ehp_amount
            
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': cos_coal_ehp.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': ehp_amount,
                            'amount_currency': ehp_amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_detail_ehp.account_id.id,
                            'quantity': 1,
                            'credit':  ehp_amount, 
                            'debit': 0.0,
                            'amount_currency':ehp_amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
            
        cos_coal_lcv  = self.env['account.account'].sudo().search([('code','=','51001102'),('company_id','=',self.env.company.id)],limit=1)
        wip_detail_lcv = self.env['wip.detail'].sudo().search([('account_id.code','=','110409'),('cogs_id','=',self.id)])
        
        lcv_ar = self.env['product.line'].sudo().search([('product_id.name','like','LCV'),('invoice_id.project_code','=',self.project_code_id.id),('invoice_id.journal_id.name','=','AR Commercial')],limit=1)
        if cos_coal_lcv and wip_detail_lcv:
            lcv_amount = 0
            if lcv_ar:
                for me in lcv_ar:
                    lcv_amount += me.quantity * me.product_id.standard_price
            self.coal_lcv = -lcv_amount
                
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': cos_coal_lcv.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': lcv_amount,
                            'amount_currency': lcv_amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_detail_lcv.account_id.id,
                            'quantity': 1,
                            'credit':  lcv_amount, 
                            'debit': 0.0,
                            'amount_currency':  lcv_amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))

        cos_coal_hcv = self.env['account.account'].sudo().search(
            [('code', '=', '51001111'), ('company_id', '=', self.env.company.id)], limit=1)
        wip_detail_hcv = self.env['wip.detail'].sudo().search(
            [('account_id.code', '=', '110410'), ('cogs_id', '=', self.id)])

        hcv_ar = self.env['product.line'].sudo().search(
            [('product_id.name', 'like', 'HCV'), ('invoice_id.project_code', '=', self.project_code_id.id),
             ('invoice_id.journal_id.name', '=', 'AR Commercial')])
        if cos_coal_hcv and wip_detail_hcv:
            hcv_amount = 0
            if hcv_ar:
                for me in hcv_ar:
                    hcv_amount += me.quantity * me.product_id.standard_price
            self.coal_hcv = -hcv_amount

            line_ids.append((0, 0, {
                # 'product_id': alldata.product_id.id,
                'account_id': cos_coal_hcv.id,
                'quantity': 1,
                'credit': 0.0,
                'debit': hcv_amount,
                'amount_currency': hcv_amount,
                'currency_id': self.main_currency_id.id,
                'partner_id': self.customer_code.id,
            }))

            line_ids.append((0, 0, {
                # 'product_id': alldata.product_id.id,
                'account_id': wip_detail_hcv.account_id.id,
                'quantity': 1,
                'credit': hcv_amount,
                'debit': 0.0,
                'amount_currency': hcv_amount,
                'currency_id': self.main_currency_id.id,
                'partner_id': self.customer_code.id,
            }))
            
        hauling_stockpile  = self.env['account.account'].sudo().search([('code','=','51001103'),('company_id','=',self.env.company.id)],limit=1)
        wip_detail_hauling_stockpile = self.env['wip.detail'].sudo().search([('account_id.code','=','110401'),('cogs_id','=',self.id)])
        if hauling_stockpile and wip_detail_hauling_stockpile:
            # self.hauling_stockpille = -wip_detail_hauling_stockpile.amount
            self.hauling_stockpille = -hauling_amount
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': hauling_stockpile.id,
                            'quantity': 1,
                            'credit': 0.0,
                            # 'debit': wip_detail_hauling_stockpile.amount,
                            # 'amount_currency': wip_detail_hauling_stockpile.amount,
                            'debit': hauling_amount,
                            'amount_currency': hauling_amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_detail_hauling_stockpile.account_id.id,
                            'quantity': 1,
                            # 'credit':  wip_detail_hauling_stockpile.amount,
                            'credit':  hauling_amount,
                            'debit': 0.0,
                            # 'amount_currency':  wip_detail_hauling_stockpile.amount,
                            'amount_currency':  hauling_amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
            
            
        handling_terminal  = self.env['account.account'].sudo().search([('code','=','51001104'),('company_id','=',self.env.company.id)],limit=1)
        wip_handling_terminal = self.env['wip.detail'].sudo().search([('account_id.code','=','110402'),('cogs_id','=',self.id)])
        if handling_terminal and wip_handling_terminal:
            self.terminal_handling = -wip_handling_terminal.amount
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': handling_terminal.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': wip_handling_terminal.amount,
                            'amount_currency': wip_handling_terminal.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_handling_terminal.account_id.id,
                            'quantity': 1,
                            'credit':  wip_handling_terminal.amount, 
                            'debit': 0.0,
                            'amount_currency':  wip_handling_terminal.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
            
        hauling_coal_transfer  = self.env['account.account'].sudo().search([('code','=','51001105'),('company_id','=',self.env.company.id)],limit=1)
        wip_hauling_coal_transfer = self.env['wip.detail'].sudo().search([('account_id.code','=','110403'),('cogs_id','=',self.id)])
        if hauling_coal_transfer and wip_hauling_coal_transfer:
            self.haulling_36_port = -wip_hauling_coal_transfer.amount
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': hauling_coal_transfer.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': wip_hauling_coal_transfer.amount,
                            'amount_currency': wip_hauling_coal_transfer.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_hauling_coal_transfer.account_id.id,
                            'quantity': 1,
                            'credit':  wip_hauling_coal_transfer.amount, 
                            'debit': 0.0,
                            'amount_currency':  wip_hauling_coal_transfer.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
            
        barging  = self.env['account.account'].sudo().search([('code','=','51001106'),('company_id','=',self.env.company.id)],limit=1)
        wip_barging = self.env['wip.detail'].sudo().search([('account_id.code','=','110404'),('cogs_id','=',self.id)])
        if barging and wip_barging:
            self.barging = -wip_barging.amount
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': barging.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': wip_barging.amount,
                            'amount_currency': wip_barging.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_barging.account_id.id,
                            'quantity': 1,
                            'credit':  wip_barging.amount, 
                            'debit': 0.0,
                            'amount_currency':  wip_barging.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
            
        crane  = self.env['account.account'].sudo().search([('code','=','51001107'),('company_id','=',self.env.company.id)],limit=1)
        wip_crane = self.env['wip.detail'].sudo().search([('account_id.code','=','110405'),('cogs_id','=',self.id)])
        if crane and wip_crane:
            self.floating_crane =  -wip_crane.amount
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': crane.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': wip_crane.amount,
                            'amount_currency': wip_crane.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_crane.account_id.id,
                            'quantity': 1,
                            'credit':  wip_crane.amount, 
                            'debit': 0.0,
                            'amount_currency':  wip_crane.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
            
        surveyor  = self.env['account.account'].sudo().search([('code','=','51001108'),('company_id','=',self.env.company.id)],limit=1)
        wip_surveyor = self.env['wip.detail'].sudo().search([('account_id.code','=','110406'),('cogs_id','=',self.id)])
        if surveyor and wip_crane:
            self.surveyor = -wip_surveyor.amount
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': surveyor.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': wip_surveyor.amount,
                            'amount_currency': wip_surveyor.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_surveyor.account_id.id,
                            'quantity': 1,
                            'credit':  wip_surveyor.amount, 
                            'debit': 0.0,
                            'amount_currency':  wip_surveyor.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
            
        stevedooring  = self.env['account.account'].sudo().search([('code','=','51001109'),('company_id','=',self.env.company.id)],limit=1)
        wip_stevedooring = self.env['wip.detail'].sudo().search([('account_id.code','=','110407'),('cogs_id','=',self.id)])
        if stevedooring and wip_stevedooring:
            self.stevedooring = wip_stevedooring.amount
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': stevedooring.id,
                            'quantity': 1,
                            'credit': 0.0,
                            'debit': wip_stevedooring.amount,
                            'amount_currency': wip_stevedooring.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
        
            line_ids.append((0, 0, {
                            # 'product_id': alldata.product_id.id,
                            'account_id': wip_stevedooring.account_id.id,
                            'quantity': 1,
                            'credit':  wip_stevedooring.amount, 
                            'debit': 0.0,
                            'amount_currency':  wip_stevedooring.amount,
                            'currency_id':self.main_currency_id.id,
                            'partner_id': self.customer_code.id,
                        }))
            

        move_vals = {
            'ref': self.name,
            'date': fields.Datetime.now(),
            'journal_id': self.journal_id.id,
            'line_ids': line_ids,
            'name': '/',
            'move_type': 'entry',
            'partner_id': self.customer_code.id,
            'invoice_date': fields.Datetime.now(),
            'currency_id': self.main_currency_id.id,
        }
        entry_id = self.env['account.move'].create(move_vals)
        entry_id.action_post()
        self.account_move_id = entry_id.id
        self.wip_total = 0
        self.cos_total =  -abs(self.hauling_stockpille + self.terminal_handling + self.haulling_36_port + self.barging + self.floating_crane + self.surveyor + self.stevedooring + self.coal_lcv + self.coal_mcv + self.coal_hcv + self.consultant)
        self.cogs_amount =  abs(self.cos_total)
        self.cos_mt = -(abs(self.cos_total)/self.qty) if self.qty > 0 else 0
        self.gross_margin = self.revenue_idr - abs(self.cos_total)
        self.percent = f"{((self.gross_margin/self.revenue_idr) * 100 ):.2f}%"
        self.margin_mt =  self.gross_margin/self.qty if self.qty > 0 else 0
        self.state = 'close'

        data = json.dumps({
            "project_code": self.project_code_id.name,
        })

        headers = {
            'Content-Type': 'application/json'
        }
        # url = "http://103.174.114.79:85/api/DespatchOrder" #dev
        url = "http://103.174.114.79:83/api/DespatchOrder" #prod
        response = requests.request("PUT", url, headers=headers, data=data)
        if response.status_code == 200:
            return
        elif response.status_code == 400:
            raise ValidationError("Integration with smartmining error \n%s" % (response.text))
        else:
            raise ValidationError("Integration with smartmining error")

        
        
    @api.model
    def default_get(self, fields):
        result = super(cogsManagement, self).default_get(fields)
        account_ids = []
        account_haulling_stockpille  = self.env['account.account'].sudo().search([('code','=','110401'),('company_id','=',2)],limit=1)
        if account_haulling_stockpille:
            account_ids.append((0,0,{'account_id':account_haulling_stockpille.id}))
            
        account_terminal_handling  = self.env['account.account'].sudo().search([('code','=','110402'),('company_id','=',2)],limit=1)
        if account_terminal_handling:
            account_ids.append((0,0,{'account_id':account_terminal_handling.id}))
            
        account_hauling_coal_transfer  = self.env['account.account'].sudo().search([('code','=','110403'),('company_id','=',2)],limit=1)
        if account_hauling_coal_transfer:
            account_ids.append((0,0,{'account_id':account_hauling_coal_transfer.id}))
            
        account_barging  = self.env['account.account'].sudo().search([('code','=','110404'),('company_id','=',2)],limit=1)
        if account_barging:
            account_ids.append((0,0,{'account_id':account_barging.id}))
            
        floating_crane  = self.env['account.account'].sudo().search([('code','=','110405'),('company_id','=',2)],limit=1)
        if floating_crane:
            account_ids.append((0,0,{'account_id':floating_crane.id}))
            
        surveyor  = self.env['account.account'].sudo().search([('code','=','110406'),('company_id','=',2)],limit=1)
        if surveyor:
            account_ids.append((0,0,{'account_id':surveyor.id}))
            
        steve  = self.env['account.account'].sudo().search([('code','=','110407'),('company_id','=',2)],limit=1)
        if steve:
            account_ids.append((0,0,{'account_id':steve.id}))
            
        mcv  = self.env['account.account'].sudo().search([('code','=','110408'),('company_id','=',2)],limit=1)
        if mcv:
            account_ids.append((0,0,{'account_id':mcv.id}))
            
        lcv  = self.env['account.account'].sudo().search([('code','=','110409'),('company_id','=',2)],limit=1)
        if lcv:
            account_ids.append((0,0,{'account_id':lcv.id}))

        hcv  = self.env['account.account'].sudo().search([('code','=','110410'),('company_id','=',2)],limit=1)
        if hcv:
            account_ids.append((0,0,{'account_id':hcv.id}))

        consul  = self.env['account.account'].sudo().search([('code','=','110411'),('company_id','=',2)],limit=1)
        if consul:
            account_ids.append((0,0,{'account_id':consul.id}))
            
        # if cash_advance:
        result.update({
            'wip_detail_ids': account_ids,
            'company_id': 2
        })
        return result
    
    
        
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cogs.management')
        res = super(cogsManagement, self).create(vals)
        for line in res.wip_detail_ids:
            line._compute_amount()
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cogs_id = fields.Many2one('cogs.management',index=True,ondelete='restrict')
    
    
class wipDetail(models.Model):
    _name = 'wip.detail'
    
    
    cogs_id = fields.Many2one('cogs.management')
    account_id = fields.Many2one('account.account',string="WIP Category")
    amount =  fields.Float(compute='_compute_amount',store=True)
    
    
    @api.depends('cogs_id')
    def _compute_amount(self):
        # cos_coal_amount = self.env['product.line'].sudo().search([('product_id.name','=','COAL-LCV'),('invoice_id.project_code','=',self.project_code_id.id),('invoice_id.journal_id.name','=','AR Commercial')])
        # for data in self.filtered(lambda line:line.account_id.code not in ('110409','110408')):
        for data in self:
            if data.cogs_id:
                if data.cogs_id.project_code_id:
                    move_line = self.env['account.move.line'].sudo().search([('wip_id.project_code','=',data.cogs_id.project_code_id.id),
                                                                             ('account_id','=',data.account_id.id),
                                                                             ('wip_id.state','=','posted')])
                    if move_line:
                        total = sum([line.debit for line in move_line])
                        data.amount = total
                    else:
                        data.amount = 0
            else:
                data.amount = 0
    
    
        