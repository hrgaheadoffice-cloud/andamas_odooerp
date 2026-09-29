# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero, float_round

class SettelmentReason(models.TransientModel):
    _name = 'settelment.reason.wiz'
    _description = 'Settelment Reason Wizard'

    alasan = fields.Text('Reason',index=True,required=True)
    settelment_ids = fields.Many2one('settelment.line',string='Settelment ID')

    @api.model
    def default_get(self, default_fields):
        res = super(SettelmentReason, self).default_get(default_fields)
        activeid =  self._context.get('active_ids')
        if activeid:
            res['settelment_ids'] = activeid
        return res

    def action_apply(self):
        myaction = self._context.get('tindakan')
        if myaction == 'approved':
            self.settelment_ids.write({'alasan': self.alasan,'is_approved': True, 'is_rejected': False, 'state': 'approved'})
        else:
            self.settelment_ids.write({'alasan': self.alasan, 'is_approved': False, 'is_rejected': True, 'state': 'rejected'})
        return True

