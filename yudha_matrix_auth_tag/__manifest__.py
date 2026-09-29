# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


{
	'name': "Yudha MatrixAuth Tag",
	'summary': """Yudha MatrixAuth Tag""",
	'description': """Yudha MatrixAuth Tag""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Inventory',
	'version': '14.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'bisa_matrix_auth'],
	'support': 'xabre0010@gmail.com',
	'data': [
		'views/matrix_auth.xml',
		'data/department_all.xml',
		'security/matirx_multi_company.xml',
	],
	'images': [
		'static/src/img/main_screenshot.png'
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
