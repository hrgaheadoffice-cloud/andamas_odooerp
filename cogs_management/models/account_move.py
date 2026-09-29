from odoo import models, fields, api

class accountMove(models.Model):
    _inherit = 'account.move'
    
    
    def action_post(self):
        res = super(accountMove,self).action_post()
        
        if self.project_code and self.journal_id.name == 'AR Commercial':
            cogs = self.env['cogs.management'].search([('project_code_id','=',self.project_code.id)],limit=1)
            if cogs:
                cogs.revenue = (self.product_line_ids[0].price_unit) * (sum([data.quantity for data in self.product_line_ids]))
                cogs.qty = sum([data.quantity for data in self.product_line_ids])
                cogs.currency_id = self.currency_id.id
                if self.currency_id.name != 'IDR':
                    cogs.price_mt = self.currency_id._convert(
                    from_amount=self.product_line_ids[0].price_unit,
                    to_currency = self.company_id.currency_id,
                    company=self.company_id,
                    date=self.invoice_date,
                    round = True
                     )
                else:
                    cogs.price_mt = self.product_line_ids[0].price_unit
            if cogs.wip_detail_ids:
                for line in cogs.wip_detail_ids:
                    line._compute_amount()
        return res