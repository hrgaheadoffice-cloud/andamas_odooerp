{
    'name': "Yudha Account NOI",
    'version': '14.0.0.1',
    'summary': 'Accounting',
    'description': 'Accounting Non Invoice',
    'author': 'Albertus Restiyanto Pramayudha',
    'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
    'depends': [
        'account_accountant',
        'bisa_matrix_auth',
    ],
    'data': [
        'data/noi_sequence.xml',
        'views/account_noi.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
