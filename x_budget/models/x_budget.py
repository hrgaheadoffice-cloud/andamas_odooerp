# -*- coding : utf-8 -*-

from odoo import api, fields, models, _

class XBudget(models.Model):
    _name = 'x.budget'

    name = fields.Char('Budget')
    JAN  = fields.Float('JAN')
    FEB  = fields.Float('FEB')
    MAR  = fields.Float('MAR')
    APR  = fields.Float('APR')
    MAY  = fields.Float('MAY')
    JUN  = fields.Float('JUN')
    JUL  = fields.Float('JUL')
    AUG  = fields.Float('AUG')
    SEP  = fields.Float('SEP')
    OCT  = fields.Float('OCT')
    NOV  = fields.Float('NOV')
    DEC  = fields.Float('DEC')