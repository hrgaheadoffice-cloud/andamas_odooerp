# -*- coding : utf-8 -*-
#######################################################################################################################
#      Author    => Albertus Restiyanto Pramayudha                                                                    #
#      email     => xabre0010@gmail.com                                                                               #
#      linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/                              #
#      youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA                                          #
#######################################################################################################################

from odoo import models, fields, api, _

class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    def _compute_sum(self, options_list, calling_financial_report=None):
        self.ensure_one()
        params = []
        queries = []
        AccountFinancialReportHtml = self.financial_report_id
        groupby_list = AccountFinancialReportHtml._get_options_groupby_fields(options_list[0])
        all_groupby_list = groupby_list.copy()
        groupby_in_formula = any(x in (self.formulas or '') for x in ('sum_if_pos_groupby', 'sum_if_neg_groupby'))
        if groupby_in_formula and self.groupby and self.groupby not in all_groupby_list:
            all_groupby_list.append(self.groupby)
        groupby_clause = ','.join('account_move_line.%s' % gb for gb in all_groupby_list)

        parent_financial_report = self._get_financial_report()

        # Prepare a query by period as the date is different for each comparison.

        for i, options in enumerate(options_list):
            new_options = self._get_options_financial_line(options, calling_financial_report, parent_financial_report)
            line_domain = self._get_domain(new_options, parent_financial_report)

            ct_query = self.env['res.currency']._get_query_currency_table(options)
            tables, where_clause, where_params = AccountFinancialReportHtml._query_get(new_options, domain=line_domain)

            queries.append('''
                SELECT
                    ''' + (groupby_clause and '%s,' % groupby_clause) + ''' %s AS period_index,
                    COUNT(DISTINCT account_move_line.''' + (self.groupby or 'id') + ''') AS count_rows,
                    COALESCE(SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS balance
                FROM ''' + tables + '''
                JOIN ''' + ct_query + ''' ON currency_table.company_id = account_move_line.company_id
                WHERE ''' + where_clause + '''
                ''' + (groupby_clause and 'GROUP BY %s' % groupby_clause) + '''
            ''')
            params.append(i)
            params += where_params

        # Fetch the results.

        results = {
            'sum': {},
            'sum_if_pos': {},
            'sum_if_pos_groupby': {},
            'sum_if_neg': {},
            'sum_if_neg_groupby': {},
            'count_rows': {},
        }
        parent_financial_report._cr_execute(options_list[0], ' UNION ALL '.join(queries), params)
        for res in self._cr.dictfetchall():
            # Build the key.
            key = [res['period_index']]
            for gb in groupby_list:
                key.append(res[gb])
            key = tuple(key)
            # print('ini sum ', float(str(res['balance']).replace('-','')))
            # Compute values.
            results['count_rows'].setdefault(res['period_index'], 0)
            results['count_rows'][res['period_index']] += res['count_rows']
            results['sum'][key] = res['balance']
            if results['sum'][key] > 0:
                results['sum_if_pos'][key] = results['sum'][key]
                results['sum_if_pos_groupby'].setdefault(key, 0.0)
                results['sum_if_pos_groupby'][key] += res['balance']
            if results['sum'][key] < 0:
                results['sum_if_neg'][key] = results['sum'][key]
                results['sum_if_neg_groupby'].setdefault(key, 0.0)
                results['sum_if_neg_groupby'][key] +=  res['balance']

        return results
