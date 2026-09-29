# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "14.0.1.0.1",
    "summary": "Use this module to have notification of requirements of "
    "materials and/or external services and keep track of such "
    "requirements.",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["purchase", "product", "purchase_stock", 'account','hr', 'analytic', 'stock', 'yudha_matrix_auth_tag','bisa_matrix_auth'],
    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        'data/mail_data.xml',
        'data/cron_data.xml',
        "data/purchase_request_sequence.xml",
        "data/purchase_request_data.xml",
        "reports/report.xml",
        "reports/report_pr_qweb.xml",
        # "reports/report_purchase_request.xml",
        "reports/rpt_pr.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_request_line_view.xml",
        "views/purchase_request_report.xml",
        "views/product_template.xml",
        "views/purchase_order_view.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/quotation_selection_view.xml",
        # "views/report_view.xml",
        "views/notif_pr_view.xml",
        "wizard/notif_pr.xml",
        "views/stock_warehouse.xml",
        "views/res_users.xml",
    ],
    "demo": ["demo/purchase_request_demo.xml"],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
