# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
{
	'name': "Yudha Asset Extended",
	'summary': """Yudha Asset Extended""",
	'description': """Yudha Asset Extended""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Expense',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'account_asset','bisa_maintenance'],
	'support': 'xabre0010@gmail.com',
	'data': [
		'views/account_asset.xml',
		'views/asset_maintenace.xml',
	],
	'images': [
		'static/description/icon.png'
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
