# coding: utf-8
#
{
    "name": "Leasing Management",
    'version': '1.0',
    'author': 'account',
    'category': 'account',
    "data": [
        'security/ir.model.access.csv',
        'data/leasing_management_sequence.xml',
        'view/menu.xml',
        'view/leasing_management.xml',
        'view/leasing_management_journal_voucher.xml',
        'view/config_leasing_management.xml',
        'view/register_payment.xml'
     ],
    'depends': ['base','account','yudha_payment_voucher'],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
