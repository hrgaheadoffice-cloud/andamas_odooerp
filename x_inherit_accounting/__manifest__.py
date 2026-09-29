{
	'name': "X Inherit Accounting",
	'summary': """Custom accounting for approval matrix""",
	'description': """Custom accounting for approval matrix""",
	'category': 'Accounting',
	'version': '14.1.1',
	'depends': ['base', 'account','bisa_matrix_auth'],
	
	'data': [
		'views/bills.xml',
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
