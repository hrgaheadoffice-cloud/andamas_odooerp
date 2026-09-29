# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


{
	'name': "Yudha Product Comodity",
	'summary': """Yudha Product Comodity""",
	'description': """Yudha Product Comodity""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Inventory',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'stock'],
	'support': 'xabre0010@gmail.com',
	'data': [
		'views/product_comodity.xml',
		'views/product_template.xml',
		'security/ir.model.access.csv',
		'security/ir.rule.xml',
	],
	'images': [
		'static/src/img/main_screenshot.png'
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
