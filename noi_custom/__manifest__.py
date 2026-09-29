{
	'name': "NOI Custom",
	'summary': """NOI Custom""",
	'description': """NOI Custom""",
	'author': "My Company",
	'website': 'http://www.yourcompany.com',
	'category': 'Uncategorized',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'account', 'bisa_matrix_auth'],
	'data': [
		'security/ir.model.access.csv',
		'security/ir.rule.xml',
		'data/seq_noi.xml',
		'views/noi.xml',
		'views/register_payment.xml',
		'views/menu.xml',
		'reports/rpt_noi.xml'
	],
	# 'images': [
	# 	'static/description/icon.png'
	# ],
	'installable': True,
	'application': True,
	'auto_install': False,
}
