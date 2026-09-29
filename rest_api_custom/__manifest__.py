{
    'name': 'Rest API Custom',
    'version': '14.0.0.1',
    'summary': 'Rest API Custom',
    'description': 'Rest API Custom',
    'author': 'Adiraja Integrasi',
    'depends': [
        'base',
        'account',
        'web',
        'fuel_management',
        'wip'
    ],
    'data': [
        'view/res_partner_views.xml',
        'view/product_template.xml',
        'view/inventory_calculation.xml',
        'view/res_company.xml',
        'view/account_move.xml',
        'security/ir.model.access.csv'
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
