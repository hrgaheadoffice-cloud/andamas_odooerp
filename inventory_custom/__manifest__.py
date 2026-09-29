{
    'name': 'Inventory Custom',
    'version': '14.0.0.1',
    'summary': 'Inventory',
    'description': 'Inventory',
    'author': 'Adiraja Integrasi',
    'depends': [
        'stock',
        'purchase_request'
    ],
    'data': [
        'views/stock_picking.xml',
        'report/report_deliveryslip.xml',
        'views/product.xml',
        'security/ir.rule.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}