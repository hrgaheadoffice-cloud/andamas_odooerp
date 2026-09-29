{
    'name': 'Fleet Custom',
    'version': '14.0.0.1',
    'summary': 'Fleet',
    'description': 'Fleet',
    'author': 'Adiraja Integrasi',
    'depends': [
        'fleet',
        'fleet_rent',
        'bisa_maintenance'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/reset_menu.xml',
        'views/fleet_rent.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}