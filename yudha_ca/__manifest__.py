# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
{
	'name': "Yudha Cash Advance",
	'summary': """Yudha Cash Advance""",
	'description': """Yudha Cash Advance""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Expense',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'hr_expense','contacts','bisa_matrix_auth'],
	'support': 'xabre0010@gmail.com',
	'data': [
		# 'views/assets.xml',
		'security/ir.model.access.csv',
		'views/ca_config.xml',
		'views/ca_assets.xml',
		'views/res_partner.xml',
		'views/settelment_reason.xml',
		'views/register_payment.xml',
		'views/cash_advance.xml',
		'views/settelment.xml',
		'views/settelment.xml',
		'views/menu.xml',
		'views/product_template.xml',
		'data/seq_cash_advance.xml',
		'data/seq_settelement.xml',
		'reports/rpt_ca.xml',
		'reports/rpt_settelment.xml',
	],
	'images': [
		'static/description/icon.png'
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
