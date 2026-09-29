# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


{
	'name': "Yudha Reimbursement Site",
	'summary': """Yudha Reimbursement Site""",
	'description': """Yudha Reimbursement Site""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Expense',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'account_accountant','account_asset','bisa_matrix_auth'],
	'support': 'xabre0010@gmail.com',
	'data': [
		'security/ir.model.access.csv',
		'security/ir.rule.xml',
		'data/seq_reimbursement.xml',
		'views/reimbursement_reason.xml',
		'views/register_payment.xml',
		'views/reimbursement.xml',
		'views/reimbursement_config.xml',
		'views/menu.xml',
		'reports/rpt_reimburesement.xml',
	],
	'images': [
		'static/description/icon.png'
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
