{
    'name': 'BISA Maintenance Print',
    'version': '14.0.0.1',
    'summary': 'Provide feature print doc from module bisa maintenance',
    'description': 'Provide feature print doc from module bisa maintenance',
    'depends': [
        'bisa_maintenance',


    ],
    'data': [
        'report/report_template.xml',
        # 'report/report_purchase_request.xml',
        # 'report/report_request_for_quotation.xml',
        # 'report/report_purchase_order.xml',
        'report/report_work_order.xml',
        'report/tyre_print_out.xml'
        # 'report/report_cargo_manifest.xml',
        # 'report/report_fleet_rent.xml',
        # 'report/report_invoice_and_bill.xml',
        # 'report/report_proforma_invoice.xml',
        # 'report/report_transporter_task.xml',
        # 'report/custom_report_picking_operation.xml',
        # 'report/report_good_issue.xml',
    ],
    'installable': True,
}