# coding: utf-8
#
{
    "name": "Bisa Maintenance",
    'version': '1.5.1',
    'author': 'Bisa Indonesia',
    'category': 'Sales',
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'view/menu.xml',
        # 'view/maintenance.xml',
        'view/timesheet.xml',
        'view/task.xml',
        'view/config.xml',
        # 'view/matrial.xml',
        # ASSET MAINTENANCE
        'view/master_data/asset_maintenance/asset_mt_list_view.xml',

        # MASTER SERVICE
        'view/master_data/service/service_view.xml',
        'view/master_data/service/sparepart_view.xml',
        'view/master_data/service/sparepart_line_view.xml',
        'view/master_data/service/jasa_line_view.xml',
        # 'view/master_data/service/menu.xml',

        # MAINTENANCE REQUEST
        'view/maintenance/request_view.xml',
        'view/maintenance/requisition.xml',

        'view/work_request.xml',
        # 'view/work_summary.xml',
        'view/work_order.xml',
        'view/maintenance/requisition.xml',
        'view/maintenance_activity.xml',
        'view/delay_factor.xml',
        'view/schedule_activity.xml',
        'view/detail_task.xml',
        'view/mrp_menu.xml',
        'view/tire_service.xml',
        'view/tyre_problem.xml',
        'view/tyre_remarks.xml',
        'view/tyre_removal.xml',
        'view/tyre_fitment.xml',
        'view/component.xml',
        'view/res_config_settings.xml',
        'view/aset_ga.xml',
        'view/mrp_production.xml',
        'view/matrial.xml',
        'view/brand_model.xml',
        'view/periodic_service.xml',
        'view/periodic_service_record.xml',
        'view/maintenance_report.xml',
        'view/tyre_report.xml',
        'view/tyre_rotation.xml',
        'report/requisition.xml',
        'report/report_template.xml',
        'view/timesheet_period_plan.xml',
        'view/budget_plan_asset.xml'

    ],
    'qweb': [
        "static/src/xml/maintenance_dashboard.xml",
    ],
    'depends': [
        'base',
        'account',
        'product',
        'account_asset',
        'hr',
        'purchase',
        'stock',
        'purchase_request',
        'mrp',
        'multiple_reference_per_product'
    ],
    "test": [],
    "js": [],
    "css": [],
    "installable": True,
    "auto_install": False,
}
