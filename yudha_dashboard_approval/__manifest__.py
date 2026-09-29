# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


{
	'name': "Yudha Dashboard Approval",
	'summary': """Yudha Dashboard Approval""",
	'description': """Yudha Dashboard Approval""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Expense',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'account_reports'],
	'support': 'xabre0010@gmail.com',
	'data': [
		'views/yudha_dashboard_asset.xml',
		'views/yudha_dashboard_approval.xml',
	],
	'images': [
		'static/description/icon.png'
	],
    'qweb': [
        'static/src/xml/yudha_dashboard_approval.xml',
    ],
	'installable': True,
	'application': True,
	'auto_install': False,
}
