# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.exceptions import UserError

class InheritAccountMove(models.Model):
    _inherit = 'account.move'

    is_proforma = fields.Boolean(default=False)
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ("to_approve_matrix", "Tobe Approved Matrix"),
            ('approved', 'Approved'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    todo_user_ids = fields.Many2many(comodel_name="res.users",string="Next Approval",readonly=True,copy=False)
    approval_matrix_ids = fields.One2many(
            comodel_name="approval.matrix",
            inverse_name="move_id",
            string="Approval Matrix",
            readonly=True,
            copy=False,
            track_visibility="onchange",
        )
    

    @api.onchange('move_type','partner_id')
    def onchange_x_partner_id(self):
        for rec in self:
            if rec.move_type=='in_invoice':
                return {
                        'domain' : {
                            'partner_id' : [('supplier_rank','>',0)]
                        }
                    }
            elif rec.move_type=='out_invoice':
                return {
                        'domain' : {
                            'partner_id' : [('customer_rank','>',0)]
                        }
                    }
            else:
                return {
                        'domain' : {
                            'partner_id' : []
                        }
                    }

    def create_approval_matrix(self):
        obj_app = self.env['config.approval.matrix'].search([('modul','=','Vendor Bills'),('company_id','=',self.company_id.id),('expected_amount', '<=', self.amount_total)],order="matrix_level_name asc")  
        for item in obj_app:
            vals = {
                "move_id":self.id,
                "user_ids": [(6, 0, item.approval_user_ids.ids)],
                "matrix_level_id":item.matrix_level_id.id,
                "config_approval_matrix_id":item.id,
                "state":"Tobe Approved Mtrx "+ item.matrix_level_name,
                "name":"Tobe Approved Mtrx "+ item.matrix_level_name,
            }
            obj_create = self.env['approval.matrix'].create(vals)

    def button_approved_matrix(self):
        emp_id = self.env['approval.matrix'].search([('move_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            if self.env.uid in (emp_id.config_approval_matrix_id.approval_user_ids.ids) or emp_id.config_approval_matrix_id.delegate_user.id == self.env.uid:
                emp_id.write({'realization_user_id':self.env.uid,"date": fields.Datetime.now()})
                emp_id = self.env['approval.matrix'].search([('move_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
                if not emp_id:
                    self.todo_user_ids = False
                    self._post(soft=False)
                    return False
                else:
                    self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
            else:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))

    def button_request_approval(self):
        self.approval_matrix_ids.unlink()
        self.create_approval_matrix()
        if not self.approval_matrix_ids:
            raise UserError(
                _("Approval Matrix not found, Please Check Config Approval Matrix"))
        emp_id = self.env['approval.matrix'].search([('move_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
        self.state = 'to_approve_matrix'

    def action_post(self):
        res = super(InheritAccountMove, self).action_post()
        if self.move_type=='in_invoice':
            print('====>>>  1')
            if not self.approval_matrix_ids and self.state=='draft':
                print('====>>>  2')
                self.button_request_approval()
            else:
            #     print('====>>>  3')
            #     self._post(soft=False)
                return res
        else:
            # print('====>>>  4')
            # self._post(soft=False)
            return res

class InheritApprovalMatrixMove(models.Model):
    _inherit = "approval.matrix"

    move_id = fields.Many2one('account.move','move')