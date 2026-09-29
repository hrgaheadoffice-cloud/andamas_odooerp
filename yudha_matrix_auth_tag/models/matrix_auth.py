# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import api, fields, models, _


class tbl_matrix_auth(models.Model):
    _inherit = "tbl_matrix_auth"

    tag_warehouse = fields.Many2many('stock.warehouse','rel_tbl_matrix_auth',string='Location',index=True)
    department_id  = fields.Many2one('hr.department',string='Department',index=True)
    company_id = fields.Many2one('res.company',string='Company', default=lambda self: self.env.company)
    level  =fields.Selection(selection_add=[
        ('6', 'Level 6'),
        ('7', 'Level 7'),
        ('8', 'Level 8'),], ondelete={"6": "cascade",
                                      "7": "cascade",
                                      "8": "cascade"})
