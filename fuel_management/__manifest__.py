{
    'name': 'Fuel Management',
    'version': '14.0.0.1',
    'summary': 'Fuel Management',
    'description': 'Fuel Management',
    'author': 'Adiraja Integrasi',
    'depends': [
        'bisa_maintenance',
        'hr',
        'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        # 'views/fuel_inventory.xml',
        'views/fuel_stock.xml',
        'views/fuel_consumption.xml',
        'views/fuel_source.xml',
        'data/sequence.xml',
        'views/asset_mt_list_view.xml',
        'security/security.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}