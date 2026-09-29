from odoo import fields, models, api


class WIPProject(models.Model):
    _name = 'wip.project'

    name = fields.Char('Project Code')
    product_calory = fields.Char('Product')
    partner_id = fields.Many2one('res.partner', 'Customer', domain="[('customer_rank', '>', 0)]")
    term = fields.Char('Term of Shipment')
    cargo_nomination = fields.Char('Transport')
    contract_number = fields.Char()
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)


    @api.model
    def create(self,vals):
        res =  super(WIPProject,self).create(vals)
        cogs = self.env['cogs.management'].create({'project_code_id':res.id})

        return res


