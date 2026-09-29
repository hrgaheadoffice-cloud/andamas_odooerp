from odoo import api, fields, models, _
from odoo.exceptions import UserError
import html_to_json
import gspread

class XDocumentType(models.Model):
    _name = "x.document.type"
    _description = "Document Type Query Deluxe"

    name = fields.Char('Name')

class QueryDeluxe(models.Model):
    _name = "querydeluxe"
    _description = "Postgres queries from Odoo interface"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    tips = fields.Many2one('tipsqueries', string="Examples")
    tips_description = fields.Text(related='tips.description')

    rowcount = fields.Text(string='Rowcount')
    html = fields.Html(string='HTML')

    name = fields.Text(string='Type a query : ')
    valid_query_name = fields.Text()
    x_document_type_id = fields.Many2one('x.document.type', string="Document Type")

    show_raw_output = fields.Boolean(string='Show the raw output of the query')
    raw_output = fields.Text(string='Raw output')

    def print_result(self):
        return {
            'name': _("Select orientation of the PDF's result"),
            'view_mode': 'form',
            'res_model': 'pdforientation',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_query_name': self.valid_query_name
            },
        }

    @api.model
    def cron_send_data_google_sheets(self):
        for rec in self.search([('x_document_type_id.name','ilike','Sale Order')], limit = 1):
            rec.convert_html_to_json()
            
    def convert_html_to_json(self):
        for rec in self:
            if rec.x_document_type_id:
                gs_type = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet1_type')
                gs_project_id = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet2_project_id')
                gs_private_key_id = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet3_private_key_id')
                gs_private_key = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet4_private_key')
                gs_client_email = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet5_client_email')
                gs_client_id = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet6_client_id')
                gs_auth_uri = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet7_auth_uri')
                gs_token_uri = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet8_token_uri')
                gs_auth_provider_x509_cert_url = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet9_auth_provider_x509_cert_url')
                gs_client_x509_cert_url = self.env['ir.config_parameter'].sudo().get_param('x_google_sheet91_client_x509_cert_url')
                gs_env = str(self.env['ir.config_parameter'].sudo().get_param('x_google_sheet_env'))
                
                
                querydeluxe_obj = self.env['querydeluxe'].sudo()
                sale_order_type = querydeluxe_obj.search([('x_document_type_id.name','ilike','Sale Order')])#rec.filtered(lambda i: i.x_document_type_id.name == 'Sales Order')
                invoice_type = querydeluxe_obj.search([('x_document_type_id.name','ilike','Invoice')]) #rec.filtered(lambda i: i.x_document_type_id.name == 'Invoice')
                order_trx_type = querydeluxe_obj.search([('x_document_type_id.name','ilike','Order Transaction')]) #rec.filtered(lambda i: i.x_document_type_id.name == 'Order Transaction')
                pre_order_type = querydeluxe_obj.search([('x_document_type_id.name','ilike','Pre Order')])

                if gs_env == "PROD":
                    credentials = {
                        "type": "%s" %(str(gs_type)),
                        "project_id": "%s" %(str(gs_project_id)),
                        "private_key_id": "%s" %(str(gs_private_key_id)),
                        'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDOzoAn7uIzQy2u\n2hWyScWgcvlM+mGyEDjN92R+VE7asN7Ow5/WqrqvRh/G+30czviyl7sxsBgxGFUR\nu+/tvt8lx0hrIps/VvGCqWDefPuUk3sZM4GtN7prrZ1wv6f0AcIDmLScs8uXczR5\nqAg+Oli9MgC1Kvw2xv8E56/FjkuUnRnEu4jft/1sfq8BxrU3Y1SyyrBEE5C35GY8\naz0cpWNKmYGPQAHgJonE/mnJqyNDV9y/ZlRirn9K2C/74I8Rr0CRCJNQguImzlqF\noZ8kkyUmu19YNjILCsiYQcGiLdIn3e6bQtfAOP+hjKFbqqVwW5Ben6KsGBFXj2FD\nLCOLnv1jAgMBAAECggEAO0IqsMafpGa8gVzWWLcQ3O/1BZy9P8OsM0CPWC+aRMnn\nnkGp3F4hjjW+x0qqyAV6d9pIdm1qES9SuPksP+iwkmevFZvd9mFYZMNaEYaopCM6\nY7dBkjvkvBQMiBEy9BVI3bT1E+3lCammQLHoYsRfRx872q3NhXix/FrTH/2tJJD3\nv9sQKOAQZpK46UK4OKmofE3IstKIulJyEjd7Hmwc8jZoOhfA+8eItJ/vLe+ddyjY\nt0tKjqfCAkmR2IxdoQ4S3EP+1c5ezPFN4734GGzLRfalF5CNuAx+fEmj2z5j11i8\n7hacTaStnQVJ5EXmg5PvyREG9aHKhCa904CrsXZ6KQKBgQDpXZ5jYfqR92/kyg0h\nkPFkyB1i6dxrSWTeVh4ZaOnf0iytHkrmtNEp8tfa0BfOIlXIxVovLW5Z5QEvmt+b\nqVrYAWBFdqNjG2jLvV6q5kLPuwrsLdPHByZL9yiLq8PFgaSyb/L8iNG/7CfOoirO\nOtUOIdtMa3IyN31KO+wzqMwANwKBgQDi3W5CFC6vtIqeYGiYObPHZvVgNg88tC8R\nZioPIeC8+v1vS/kx3BUJf9STqondxJ48tT7RhTaKOKeZr4JKigThCdFnagt+LnGc\nZnc46tTX3vb0gWdnUAoTyWFL0Q78HfKdwE4XqImgOp+GWV4ajzutJtJSwPHGH+BV\nIi4obkeeNQKBgEkzKXSJDjzs/XcpfbbyrRVsw/L74jzw96faIXTc+MdRONxQrTPy\nsc1TtCuZrG3nTTs91E0KFhwyfg29qbg9BhbNT7JaRWPX/CY0T1aSBZD9Xa65rT03\n2+ZmL5yoEy+Hu+6QuQpHrGtkGxRwv7aSs7PMIOq2pUplJ3K6mxuVLfA/AoGAd7QG\nvW8Qwz0r9y0/gzLPHWPCDSX5HDqmqzOQ9bMWdiCpINShhCFwKDb+33uYix93ruij\nYMI9aOlD5d+pi9MPh/46M6rMraOr5q5aMfoWnGDVRWYSPX0KFC6p2+tPUNAsd/hE\nPE99bsH/8k+tS65P+qkFSQzthXDEWadTW5n0yBECgYEAySoot2Q66qHbZLUH7EJ4\nL9Dmgm340JCfLW7qY0QBH3rHYCqz3G0RwuftV/DEbR4eLNJb5ZUo35Rrfq0RKqN0\nX7xNPQUpisTayMaDMBu98ESAidFTrilJAAyFeFFp7Bwqi9MgvJAfFcTG/rWhbhhj\nW4495eBTwasQ4tRi1tqj/ag=\n-----END PRIVATE KEY-----\n',
                        "client_email": "%s" %(str(gs_client_email)),
                        "client_id": "%s" %(str(gs_client_id)),
                        "auth_uri": "%s" %(str(gs_auth_uri)),
                        "token_uri": "%s" %(str(gs_token_uri)),
                        "auth_provider_x509_cert_url": "%s" %(str(gs_auth_provider_x509_cert_url)),
                        "client_x509_cert_url": "%s" %(str(gs_client_x509_cert_url)),
                    }

                    gc = gspread.service_account_from_dict(credentials)
                    sh = gc.open("Dashboard Data EMICA")
                    wkso = sh.worksheet("Sale Order")
                    wkinv = sh.worksheet("Invoice")
                    wkot = sh.worksheet("Order Transaction")
                    wkpreorder = sh.worksheet("Pre Order")
                    if sale_order_type:
                        sale_order_type.execute()
                        if sale_order_type.html != '<br>':
                            sale_order = html_to_json.convert_tables(sale_order_type.html)
                            json_so = sale_order[0]
                            data_so = []
                            if json_so:
                                data_so.append(list(json_so[0].keys()))
                                for so in json_so:
                                    data_so.append(list(so.values()))
                            
                            wkso.clear()
                            wkso.update('A1', data_so)
                    if invoice_type:
                        invoice_type.execute()
                        if invoice_type.html != '<br>':
                            invoice = html_to_json.convert_tables(invoice_type.html)
                            json_inv = invoice[0]
                            data_inv = []
                            if json_inv:
                                data_inv.append(list(json_inv[0].keys()))
                                for inv in json_inv:
                                    data_inv.append(list(inv.values()))
                            
                            wkinv.clear()
                            wkinv.update('A1', data_inv)
                    if order_trx_type:
                        order_trx_type.execute()
                        if order_trx_type.html != '<br>':
                            order_trx = html_to_json.convert_tables(order_trx_type.html)
                            json_ot = order_trx[0]
                            data_ot = []
                            if json_ot:
                                data_ot.append(list(json_ot[0].keys()))
                                for ot in json_ot:
                                    data_ot.append(list(ot.values()))
                            
                            wkot.clear()
                            wkot.update('A1', data_ot)

                    if pre_order_type:
                        pre_order_type.execute()
                        if pre_order_type.html != '<br>':
                            pre_order = html_to_json.convert_tables(pre_order_type.html)
                            json_pre_order = pre_order[0]
                            data_pre_order = []
                            if json_pre_order:
                                data_pre_order.append(list(json_pre_order[0].keys()))
                                for po in json_pre_order:
                                    data_pre_order.append(list(po.values()))
                            
                            wkpreorder.clear()
                            wkpreorder.update('A1', data_pre_order)
                            
                elif gs_env == "UAT":
                    credentialsuat = {
                        "type": "%s" %(str(gs_type)),
                        "project_id": "%s" %(str(gs_project_id)),
                        "private_key_id": "%s" %(str(gs_private_key_id)),
                        'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDkwiUEdEYMxu12\n6N7uNVmIgAiltRpUIg1BPBJnAeiP4eRm6gIJmijowYA+pZPOonVMI/PZPfElaOLe\n7/ck6JEbJcvsBxMQB60uI6l+sGAkcrRlGZbcmxQjHskYMyEVKVvV7yhm85Mcmh16\nJc479rNj1nf4m+rTHGhyRQJGr0KvwcS5L/Qx05MIgEUBePqj0mGjYwwiwC3P8Q7s\ngRszTvDWNhLqrNv12L2lxmBUkDiCU1UTfJMv0C5qo80lKXdAwqIAGhdpzgORZuKA\nWUKSvYuT6GNYR0u/YLpUs0omxL3hEvPlniTso553z6XDQgQXrGZzgMakfvolUuky\nzDkK5QgBAgMBAAECggEAISjzbL3eGaQMcBw5lJYvMFY+6qZh9qgo+7fVgxEHwTOh\nhDmPqgyquXKzQGGIF3/9ONhNVMRh3GZj3KU0UilUP3cvJDuyS7SRKgsJWs/+X8ow\n1Cbtc3UXai/gPp3KweKI6W4NkT7lqFO+yiIIzzBnuKUyJtuTIp8PlODj/5MQO6G4\nzSlSsNUqfygdMrjTlR4P/ty+P7w6EkK1Rf6hUVhGdYBFuaUijQFjy0mt0sT+wHoQ\nrowNzu7qLXksBoukv/vE/P7QeB2omp/eKcrI0WjkuiUVCopQtGiZTIrvEXdb40/t\nKM2wBRLQV2AOJrEyQirfBTwrh5rCFzQioJARoHNzcQKBgQD5qrix3PiszxE9+VT4\nxExpn24dwKqyhCh2fRzbxhmWqeh9HVrvBhB6R8hj13QRHXdXgPcvYhXZl31i+sdS\nH5svurpR7c3ApRGz34xWwxjNXVV0F5ql36Rbzs4S/MapG4Gz3SkA3trEWIFNuO2N\nSX7xmVwZ/wWR/z4DFbD857zbNwKBgQDqj6XvmU4k8voQ+tP3JkvytXdTlaX6h0Mq\nJcYjnhoWN8NP5xzHsQznS/Obyhp+/LZy1K8YRT80sW3yT6/87yAywyt0PW0AaNEe\najvEI6xWp0XjFSURsqUKap5M7T3bI+NffOa6j7PLgwAnyM+/516vKdJNeW86m9Xm\nhqrb+aEChwKBgApNEPHFvDzlDkEQWIErGDwDZ/eyS1iyOzkoUFiBA+1DdWQ0Idxa\n07M34vy7lv5dyN7DY2+BDIW9yl6bGj45L534hld7CFI6fVB+mLu7sPpIL45qqubN\nI2rmTXpbE5dGm0NgjKCMkVoojK04RBTgQ2yUd0hbTU+IyHY4HuVQamphAoGBAI/8\nWho4e3XHCaZ+srtWcOyuZG+Uv2yIt7wZsAWROeZFmMllz47tqkQZpZMOfzFQpBbd\nZBZ7+463FAzYyel0SMmgcP5L7qt/rE8FW2bNly8iQ45gHn88sH8yb7Y9M+lfoGWv\nYFtJd08IPYIujQj6WG8iNwyD7LmHi8iVBjE+jY3lAoGBAKwwKGF5OZN4wpVNp4cI\nY091wSFFVRHMbI2QslKHbHe41Y2Ey+DkG72UH2KUFnDPmBTVjTmrbVlKYOPaQcev\ncDKD3LWAtpgtGvceR6o7ANGrUJDD/+ftNWDnnX6Qnrm7dZH7yrdVhd/pB3c+hxkb\n0s/3lQWmhEbBevTeCEITGKP6\n-----END PRIVATE KEY-----\n',
                        "client_email": "%s" %(str(gs_client_email)),
                        "client_id": "%s" %(str(gs_client_id)),
                        "auth_uri": "%s" %(str(gs_auth_uri)),
                        "token_uri": "%s" %(str(gs_token_uri)),
                        "auth_provider_x509_cert_url": "%s" %(str(gs_auth_provider_x509_cert_url)),
                        "client_x509_cert_url": "%s" %(str(gs_client_x509_cert_url)),
                    }

                    gcuat = gspread.service_account_from_dict(credentialsuat)
                    shuat = gcuat.open("Transaction Dashboard UAT")
                    wksouat = shuat.worksheet("Sale Order")
                    wkinvuat = shuat.worksheet("Invoice")
                    wkotuat = shuat.worksheet("Order Transaction")
                    wkpreorderuat = shuat.worksheet("Pre Order")
                    if sale_order_type:
                        sale_order_type.execute()
                        if sale_order_type.html != '<br>':
                            sale_order_uat = html_to_json.convert_tables(sale_order_type.html)
                            json_so_uat = sale_order_uat[0]
                            data_so_uat = []
                            if json_so_uat:
                                data_so_uat.append(list(json_so_uat[0].keys()))
                                for so_uat in json_so_uat:
                                    data_so_uat.append(list(so_uat.values()))
                            
                            wksouat.clear()
                            wksouat.update('A1', data_so_uat)
                    if invoice_type:
                        invoice_type.execute()
                        if invoice_type.html != '<br>':
                            invoice_uat = html_to_json.convert_tables(invoice_type.html)
                            json_inv_uat = invoice_uat[0]
                            data_inv_uat = []
                            if json_inv_uat:
                                data_inv_uat.append(list(json_inv_uat[0].keys()))
                                for inv_uat in json_inv_uat:
                                    data_inv_uat.append(list(inv_uat.values()))
                            
                            wkinvuat.clear()
                            wkinvuat.update('A1', data_inv_uat)
                    if order_trx_type:
                        order_trx_type.execute()
                        if order_trx_type.html != '<br>':
                            order_trx_uat = html_to_json.convert_tables(order_trx_type.html)
                            json_ot_uat = order_trx_uat[0]
                            data_ot_uat = []
                            if json_ot_uat:
                                data_ot_uat.append(list(json_ot_uat[0].keys()))
                                for ot_uat in json_ot_uat:
                                    data_ot_uat.append(list(ot_uat.values()))
                            
                            wkotuat.clear()
                            wkotuat.update('A1', data_ot_uat)

                    if pre_order_type:
                        pre_order_type.execute()
                        if pre_order_type.html != '<br>':
                            pre_order_uat = html_to_json.convert_tables(pre_order_type.html)
                            json_pre_order_uat = pre_order_uat[0]
                            data_pre_order_uat = []
                            if json_pre_order_uat:
                                data_pre_order_uat.append(list(json_pre_order_uat[0].keys()))
                                for po_uat in json_pre_order_uat:
                                    data_pre_order_uat.append(list(po_uat.values()))
                            
                            wkpreorderuat.clear()
                            wkpreorderuat.update('A1', data_pre_order_uat)
                # function send to xlsx local
                # if invoice_type:
                #     invoice = html_to_json.convert_tables(invoice_type.html)
                #     json_invoice = invoice[0]
                #     json_invoice_string = json.dumps(json_invoice)
                #     print("JSON INVOICE=====", json_invoice_string)
                #     df_inv = pd.read_json(json_invoice_string).to_excel("D:\orders1.xlsx", sheet_name="Invoice", index=False)
    def copy_query(self):
        if self.tips:
            self.name = self.tips.name

    def execute_origin(self):
        self = self.sudo()
        self.ensure_one()

        self.show_raw_output = False
        self.raw_output = ''

        self.rowcount = ''
        self.html = '<br></br>'

        self.valid_query_name = ''

        if self.name:
            self.tips = False
            self.message_post(body=str(self.name))

            headers = []
            datas = []

            try:
                self.env.cr.execute(self.name)
            except Exception as e:
                raise UserError(e)

            try:
                if self.env.cr.description:
                    headers = [d[0] for d in self.env.cr.description]
                    datas = self.env.cr.fetchall()
            except Exception as e:
                raise UserError(e)

            rowcount = self.env.cr.rowcount
            self.rowcount = _("{0} row{1} processed").format(rowcount, 's' if 1 < rowcount else '')

            if headers and datas:
                self.valid_query_name = self.name
                self.raw_output = datas

                header_html = "<tr style='background-color: lightgrey'> <th style='background-color:white'/>"
                header_html += "".join(["<th style='border: 1px solid black'>" + str(header) + "</th>" for header in headers])
                header_html += "</tr>"

                body_html = ""
                i = 0
                for data in datas:
                    i += 1
                    body_line = "<tr style='background-color: {0}'> <td style='border-right: 3px double; border-bottom: 1px solid black; background-color: yellow'>{1}</td>".format('cyan' if i%2 == 0 else 'white', i)
                    for value in data:
                        display_value = ''
                        if value is not None:
                            display_value = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        body_line += "<td style='border: 1px solid black'>{0}</td>".format(display_value)
                    body_line += "</tr>"
                    body_html += body_line

                self.html = """
<table style="text-align: center">
  <thead>
    {0}
  </thead>

  <tbody>
    {1}
  </tbody>
</table>
""".format(header_html, body_html)


    def execute(self):
        self.show_raw_output = False
        self.raw_output = ''

        self.rowcount = ''
        self.html = '<br></br>'

        self.valid_query_name = ''

        if self.name:
            self.tips = False
            self.message_post(body=str(self.name))

            headers = []
            datas = []

            try:
                self.env.cr.execute(self.name)
            except Exception as e:
                raise UserError(e)

            try:
                no_fetching = ['update', 'delete', 'create', 'insert', 'alter', 'drop']
                max_n = len(max(no_fetching))

                is_insides = [(o in self.name.lower().strip()[:max_n]) for o in no_fetching]
                if True not in is_insides:
                    headers = [d[0] for d in self.env.cr.description]
                    datas = self.env.cr.fetchall()
            except Exception as e:
                raise UserError(e)

            rowcount = self.env.cr.rowcount
            self.rowcount = "{0} row{1} processed".format(rowcount, 's' if 1 < rowcount else '')

            if headers and datas:
                self.valid_query_name = self.name
                self.raw_output = datas
                header_no = "<th style='border: 1px solid'>no</th>"
                header_html = "".join(["<th style='border: 1px solid'>"+str(header)+"</th>" for header in headers])
                # header_html = "<tr>"+"<th style='background-color:white !important'/>"+header_html+"</tr>"
                header_html = "<tr>"+header_no+header_html+"</tr>"

                body_html = ""
                i = 0
                for data in datas:
                    i += 1
                    body_line = "<tr>"+"<td style='border-right: 3px double; border-bottom: 1px solid; background-color: yellow'>{0}</td>".format(i)
                    for value in data:
                        body_line += "<td style='border: 1px solid; background-color: {0}'>{1}</td>".format('cyan' if i%2 == 0 else 'white', str(value) if (value is not None) else '')
                    body_line += "</tr>"
                    body_html += body_line

                self.html = """
<table style="text-align: center">
  <thead style="background-color: lightgrey">
    {0}
  </thead>

  <tbody>
    {1}
  </tbody>
</table>
""".format(header_html, body_html)


class TipsQueries(models.Model):
    _name = 'tipsqueries'
    _description = "Tips for queries"
    _order = 'create_date desc, id'

    name = fields.Char(string='Query', required=True)
    description = fields.Text(string="Description")
