#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
{
	'name': "Yudha Payment Voucher",
	'summary': """Yudha Payment Voucher""",
	'description': """Yudha Payment Voucher""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Expense',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'account','bisa_matrix_auth','web','yudha_reimbursement_ho'],
	'support': 'xabre0010@gmail.com',
	'data': [
		'views/payment_voucher_assets.xml',
		'views/payment_plann_queue.xml',
		'views/payment_voucher_menu.xml',
		'wizard/insert_ca_wizard.xml',
		'security/ir.model.access.csv',
		'security/ir.rule.xml',
	],
	'images': [
		'static/description/icon.png'
	],
	'qweb': [
		'static/src/xml/payment_voucher_awal.xml',
		# 'static/src/xml/list_view.xml',
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
