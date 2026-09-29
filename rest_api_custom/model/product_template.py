from odoo import api, fields, models, _
import requests
from odoo.http import request
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def inventory_calculation(self):

        inv_calc = self.env['inventory.calculation']
        if inv_calc.search_count([('date', '<=', datetime.now()), ('date', '>=', datetime.now().replace(day=1))]):
            raise ValidationError(_('There is already inventory calculation for this month'))

        prod = "http://103.15.226.220:85/api/integrasicogs"
        dev = "https://bombacogs.smartmining.cloud/api/integrasicogs"
        url = dev
        response = requests.request("GET", url, params=None)
        json = response.json()

        data = list(filter(lambda x: x['business_unit_code'] == self.env.cr.dbname, json))
        if data:
            data = data[0]
        else:
            raise ValidationError('No data')

        location_id = self.env['stock.location'].search([('complete_name', '=', 'WH/Stock')]).id
        stock = self.env['stock.quant'].search([('product_id', '=', self.id), ('location_id', '=', location_id)]).with_context({'inventory_mode': True})
        begin_stock = stock.quantity
        begin_avg_val = self.standard_price
        qty_stock = data['quantity_mining']
        prod_stock = begin_stock + qty_stock
        qty_sale = data['quantity_sales']
        date = ((datetime.now() + timedelta(hours=7)).replace(day=1) - timedelta(days=1))

        # total cos di 1 bulan exclude cos inventory calc sama cos royalti
        query = """
                select sum(debit) cos_value from account_move_line aml
                join account_account aa on aml.account_id = aa.id
                where aa.name like 'COS%' and aa.name not in ('COS Royalty', 'COS Inventory Calculation') and aml.parent_state = 'posted'
                and extract(month from aml.date) = '{}' and extract(year from aml.date) = '{}'
        """.format(date.month, date.year)
        self.env.cr.execute(query)
        fetched = self.env.cr.dictfetchall()
        cos_value = fetched[0].get('cos_value')

        journal_id = self.env['account.journal'].search([('name', '=', 'Inventory Valuation')]).id
        account_coal_id = self.env['account.account'].search([('code', '=', '10130000310001')]).id
        account_calc_id = self.env['account.account'].search([('code', '=', '52800000310002')]).id
        move = self.env['account.move']

        avg_value = round((cos_value + (begin_avg_val * begin_stock)) / prod_stock)
        sale_value = avg_value * qty_sale

        last_stock = prod_stock - qty_sale

        stock.write({
            'inventory_quantity': prod_stock
        })
        self.update({
            'standard_price': avg_value
        })

        generate_data_line = [
            (0, 0, {
                'account_id': account_coal_id,
                'debit': cos_value,
            }),
            (0, 0, {
                'account_id': account_calc_id,
                'credit': cos_value,
            }),
        ]
        generate_data = {
            'ref': 'Inventory Calculation',
            'journal_id': journal_id,
            'line_ids': generate_data_line,
        }
        move.create(generate_data)

        stock.update({
            'inventory_quantity': last_stock
        })

        cogs_calc_line = [
            (0, 0, {
                'account_id': account_calc_id,
                'debit': sale_value,
            }),
            (0, 0, {
                'account_id': account_coal_id,
                'credit': sale_value,
            }),
        ]
        cogs_calc = {
            'ref': 'Inventory Calculation',
            'journal_id': journal_id,
            'line_ids': cogs_calc_line,
        }
        move.create(cogs_calc)

        inv_calc.create({
            'date': datetime.now(),
            'begin_qty': begin_stock,
            'begin_val': begin_stock * begin_avg_val,
            'begin_avg_val': begin_avg_val,
            'quantity': qty_stock,
            'value': cos_value,
            'average_value': avg_value,
            'sales_val': sale_value,
            'sales_qty': qty_sale
        })

        return


