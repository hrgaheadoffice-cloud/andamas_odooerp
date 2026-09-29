{
    'name': 'Cargo Manifest',
    'version': '14.0.0.1',
    'summary': 'Cargo Manifest',
    'description': 'Cargo Manifest',
    'author': 'Adiraja Integrasi',
    'depends': [
        'base',
        'purchase',
        'purchase_request',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/cargo_manifest.xml',
        'views/cargo_manifest_line.xml',
        'data/cargo_manifest_sequence.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}