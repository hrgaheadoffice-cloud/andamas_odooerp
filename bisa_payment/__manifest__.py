# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'BISA Sundry Payment',
    'summary': 'Bisa Sundry Payment',
    'sequence': 1,
    'images': [''],
    'depends': [
        'base', 
        'account', 

    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/report.xml',
        'views/bisa_payment.xml',
    ],
    "application": True,
    'installable': True,

}
