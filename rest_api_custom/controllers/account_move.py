import json
import logging
from xmlrpc import client

from odoo import http
from odoo.http import Response, request
from odoo.tools import config, date_utils

_logger = logging.getLogger(__name__)


class AccountMove(http.Controller):
    model_name = 'account.move'

    @http.route('/accountmove', auth='public', type='json', methods=['POST'], csrf=False)
    def create(self, **kwargs):
        # request.db = kwargs['db']
        logging.info(kwargs)
        company_id = request.env['res.company'].sudo().search([('inisial_pt', '=', kwargs['BusinessUnitCode'])]).id
        ref = kwargs['InvoiceNumber']
        partner_id = request.env['res.partner'].sudo().search(['|', ('customer_code', '=', kwargs['CustomerCode']), ('vendor_code', '=', kwargs['CustomerCode']), ('company_id', '=', company_id)], limit=1).id
        if kwargs['InvoiceType'] == 'Commercial':
            journal_id = request.env['account.journal'].sudo().search([('name', '=', 'AR Commercial'), ('company_id', '=', company_id)]).id
            price_unit = kwargs['TotalPrice']
        else:
            journal_id = request.env['account.journal'].sudo().search([('name', '=', 'AR Proforma'), ('company_id', '=', company_id)]).id
            price_unit = kwargs['Payment']
        invoice_payment_term_id = request.env['account.payment.term'].sudo().search([('name', '=', '30 Days')]).id
        currency_id = request.env['res.currency'].sudo().search([('name', '=', kwargs['CurrencyExchange'])]).id
        # product_id = request.env['product.template'].sudo().search([('default_code', '=', kwargs['ProductCode'])]).id
        product_tmpl_id = request.env['product.template'].sudo().search([('name', '=', 'COAL')]).id
        product_id = request.env['product.product'].sudo().search([('product_tmpl_id', '=', product_tmpl_id)]).id
        product_uom_id = request.env['uom.uom'].sudo().search([('name', '=', kwargs['Unit'])]).id
        project_code = request.env['wip.project'].sudo().search([('name', '=', kwargs['ProjectCode'])], limit=1).id
        tax_ids = []
        invoice_line_ids = []
        product_line_ids = []
        for tax in kwargs['Taxes']:
            tax_id = request.env['account.tax'].sudo().search([('name', '=', tax), ('type_tax_use', '=', 'sale'), ('company_id', '=', company_id)]).id
            tax_ids.append(tax_id)

        # invoice_line = {
        #     'product_id': product_id,
        #     'name': kwargs['DescriptionOfGoods'],
        #     'quantity': 1,
        #     'product_uom_id': product_uom_id,
        #     'price_unit': price_unit,
        #     'tax_ids': [(6, 0, tax_ids)]
        # }

        # if kwargs['ProductCode']:
        #     invoice_line['account_id'] = request.env['account.account'].sudo().search([('code', '=', kwargs['ProductCode']), ('company_id', '=', company_id)]).id

        data = {
            'move_type': 'out_invoice',
            'ref': ref,
            'partner_id': partner_id,
            'invoice_date': kwargs['InvoiceDate'],
            'journal_id': journal_id,
            'invoice_payment_term_id': invoice_payment_term_id,
            'currency_id': currency_id,
            'invoice_line_ids': [],
            'company_id': company_id,
            'sm_integration': True,
            'project_code': project_code,
            'sales_type': kwargs['SalesType'],
            'product_line_ids': [],
            'volume': kwargs['Volume'],
        }

        if kwargs.get('Komposisi'):
            for product_line in kwargs['Komposisi']:
                product_line_code = product_line.get('ProductCode')
                product_line_tmpl_id = request.env['product.template'].sudo().search([('name', '=', product_line_code)]).id
                product_line_id = request.env['product.product'].sudo().search([('product_tmpl_id', '=', product_line_tmpl_id)]).id
                product_line_ids.append((
                    0, 0, {
                        'product_id': product_line_id,
                        'quantity': product_line.get('Quantity'),
                        'price_unit': product_line.get('Price')
                    })
                )
            data['product_line_ids'] = product_line_ids

        line_account_id = request.env['account.account'].sudo().search([('name', '=', 'Pendapatan Diterima Dimuka IDR'), ('company_id', '=', company_id)]).id
        if kwargs['CurrencyExchange'] == 'USD':
            line_account_id = request.env['account.account'].sudo().search([('name', '=', 'Pendapatan Diterima Dimuka USD'), ('company_id', '=', company_id)]).id

        # invoice_line_ids.append((
        #     0, 0, {
        #         'account_id': line_account_id,
        #         'product_id': product_id,
        #         'name': kwargs['DescriptionOfGoods'],
        #         'quantity': 1,
        #         'product_uom_id': product_uom_id,
        #         'price_unit': price_unit,
        #         'tax_ids': [(6, 0, tax_ids)]
        #     })
        # )

        invoice_line = {
            'account_id': line_account_id,
            'product_id': product_id,
            'name': kwargs['DescriptionOfGoods'],
            'quantity': 1,
            'product_uom_id': product_uom_id,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, tax_ids)]
        }

        if kwargs['InvoiceType'] == 'Commercial':
            invoice_line['price_unit'] = kwargs['Payment'] - kwargs['TotalPrice']
            ar_account_id = request.env['account.account'].sudo().search([('code', '=', '4101001'), ('company_id', '=', company_id)]).id
            if kwargs['SalesType'] != 'Domestic':
                ar_account_id = request.env['account.account'].sudo().search([('code', '=', '4101002'), ('company_id', '=', company_id)]).id
            if kwargs['ProductCode']:
                ar_account_id = request.env['account.account'].sudo().search([('code', '=', kwargs['ProductCode']), ('company_id', '=', company_id)]).id
            com_line = {
                'account_id': ar_account_id,
                'product_id': product_id,
                'name': kwargs['DescriptionOfGoods'],
                'quantity': 1,
                'product_uom_id': product_uom_id,
                'price_unit': price_unit,
                'tax_ids': [(6, 0, tax_ids)]
            }

            # invoice_line_ids.append((
            #     0, 0, {
            #         'account_id': ar_account_id,
            #         'product_id': product_id,
            #         'name': kwargs['DescriptionOfGoods'],
            #         'quantity': 1,
            #         'product_uom_id': product_uom_id,
            #         'price_unit': price_unit,
            #         'tax_ids': [(6, 0, tax_ids)]
            #     })
            # )

            invoice_line_ids.append((0, 0, com_line))

        invoice_line_ids.append((0, 0, invoice_line))

        data['invoice_line_ids'] = invoice_line_ids

        resource = request.env[self.model_name].sudo().create(data)
        return resource.id

    @http.route('/accountmove/<int:resource_id>', auth='none', type='http', methods=['GET'], csrf=False)
    def get(self, resource_id):
        resource = request.env[self.model_name].sudo().browse(resource_id)
        headers = {'content-type': 'application/json'}
        try:
            data = resource.read()[0]
        except Exception as err:
            data = {}
        return Response(json.dumps(data, default=date_utils.json_default), headers=headers)

