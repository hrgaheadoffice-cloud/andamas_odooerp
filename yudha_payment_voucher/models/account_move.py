# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    already_process = fields.Boolean('Already Process',default=False)
    @api.model
    def get_addto_plan(self,myids,ctx):
        print(' ctx 123',ctx.get('model_name'))
        myplan = self.env['payment.plan'].sudo().search([('state','=','draft')])
        if not myplan:
            arraydetail = []
            for alldata in myids:
                myacc = self.env['account.move'].sudo().browse(alldata)
                srcDoc = ''
                if ctx.get('model_name') == 'NOI':
                    srcDoc = myacc.name
                elif ctx.get('model_name') == 'CA HO':
                    srcDoc = myacc.ca_ho_id.name
                    print('source doc ', srcDoc)
                elif ctx.get('model_name') == 'Settlement HO':
                    srcDoc =myacc.settelment_ho_id.name
                elif ctx.get('model_name') == 'Cash Request':
                    srcDoc = myacc.cashrequest_id.name
                elif ctx.get('model_name') == 'Reimbursement HO':
                    srcDoc = myacc.reimbursement_ho_id.name
                else:
                    srcDoc = myacc.name
                arraydetail.append((0,0,{'moves_id': myacc.id,
                                    'date_maturity': myacc.date,
                                    'invoice_date': myacc.invoice_date,
                                    'source_doc': srcDoc,
                                    'contx': ctx.get('model_name'),
                                    'amount_currency': myacc.amount_total}))

            myplan = self.env['payment.plan'].sudo().create({'name': 'New',
                                                             'state': 'draft',
                                                             'company_id': self.env.company.id,
                                                             'payment_type': 'outbound',
                                                             'payment_plan_ids': arraydetail})
        else:
            for alldata in myids:
                myacc = self.env['account.move'].sudo().browse(alldata)
                srcDoc = ''
                if ctx == 'NOI':
                    srcDoc = myacc.name
                elif ctx == 'CA HO':
                    srcDoc = myacc.ca_ho_id.name
                elif ctx == 'Settlement HO':
                    srcDoc =myacc.settelment_ho_id.name
                elif ctx == 'Cash Request':
                    srcDoc = myacc.cashrequest_id.name
                elif ctx == 'Reimbursement HO':
                    srcDoc = myacc.reimbursement_ho_id.name
                else:
                    srcDoc = myacc.name
                self.env['payment.plan.details'].sudo().create({
                                    'plan_id': myplan.id,
                                    'moves_id': myacc.id,
                                    'date_maturity': myacc.date,
                                    'invoice_date': myacc.invoice_date,
                                    'source_doc': srcDoc,
                                    'contx': ctx.get('model_name'),
                                    'amount_currency': myacc.amount_total})
        for allids in myids:
            myaccs = self.env['account.move'].sudo().browse(allids)
            myaccs.write({'already_process': True})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

