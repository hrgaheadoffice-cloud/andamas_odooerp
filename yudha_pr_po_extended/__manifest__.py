# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


{
	'name': "Yudha PR PO Extend",
	'summary': """Yudha Switch Company Confirm""",
	'description': """Yudha Switch Company Confirm""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Purchase',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'purchase_request','hr'],
	'support': 'xabre0010@gmail.com',
	'data': [
		# 'data/purchase_request_data.xml',
		'views/purchase_request.xml',
		'views/purchase_order.xml',
	],
	'images': [
		'static/src/img/main_screenshot.png'
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
