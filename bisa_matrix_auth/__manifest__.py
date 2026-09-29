# coding: utf-8
#
{
    "name": "Matrix Authorization",
    'version': '1.0',
    'author': 'Bisa Indonesia',
    'category': 'Sales',
    "data": [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'view/menu.xml',
        'view/matrix.xml',
        'view/matrix_level.xml',
        'view/config_approval_matrix.xml'
     ],
    'depends': ['base','account','product','account_asset','hr','account_cost_center','account_cost_center'],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
