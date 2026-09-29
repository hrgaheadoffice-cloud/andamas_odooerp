# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Accounting Addon',

    'author': 'Mutiara Sistem Integrasi',

    'description': """Tambahan Transaksi Finansial:
    1. Petty Cash
    2. Advance
    3. Bonds Management
    4. Loan Intercompany
    5. Loan Employee
    6. Sundries Payment
    """,
    'summary': 'Petty Cash, Advance, Bonds, Employee Loan, Intercompany Loan, Sundries Payment',

    'sequence': 32,
    'images': [''],
    'depends': ['base','sale','stock','account','sale_stock'],
    'data': [
        'data/sequence.xml',
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/msi_advance_settlement.xml',
        'views/msi_advance_permanent.xml',
        #'views/msi_sales_quotations.xml',
        'views/employee.xml',
        'views/bonds.xml',
        'views/ic_loan.xml',
        'views/employee_loan.xml',
        'views/sundries.xml',
        'views/report.xml',
    ],
    "application": True,

}
