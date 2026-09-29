
import time
from odoo import models, fields, api
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class Dashboard(models.Model):
    _name = 'dashboard.dashboard'

    def has_active(self, model):
        for field in model.field_id:
            if field.name == 'active':
                return True
        return False

    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
           ir.rule domains."""
        return {'user': self.env.user, 'time': time}

    def _compute_field_list(self):
        dashboard = self.env['dashboard.settings'].search(
            [], limit=1, order='id desc'
        )
        lists = dashboard.line_ids
        last_slices_list = []
        for list in lists:
            if list.display:
                # Check is user or is group.
                check_usergroup = False
                check_user = False
                check_group = False
                if self.env.uid in list.user_ids.ids:
                    check_user = True

                if not list.user_ids and not list.group_ids:
                    check_usergroup = True

                for group in list.group_ids:
                    if self.env.uid in group.users.ids:
                        check_group = True

                if check_user or check_group or check_usergroup:
                    if list.action_id:
                        action = list.action_id
                    else:
                        print('====>1')
                        print('====>2',list.model_id.model)
                        action = self.env['ir.actions.act_window'].search(
                            [
                                ('res_model', '=', list.model_id.model),
                                ('view_mode', '=', 'tree,form')
                            ], limit=1)
                        print('====>3',action)
#                     requete_action = "Select id as id from " + list.model_id.model.replace('.', '_')
#                     if list.type == 'money':
#                         requete = "SELECT sum("+list.field_id.name+") as field FROM "+list.model_id.model.replace('.', '_')
#                     else:
#                         requete = "SELECT count("+list.field_id.name+") as field FROM "+list.model_id.model.replace('.', '_')
#
#                     if self.has_active(list.model_id) and list.filter:
#                         requete += " Where active=true And " + list.filter
#                         requete_action += " Where active=true And " + list.filter
#                     elif self.has_active(list.model_id):
#                         requete += " Where active=true "
#                         requete_action += " Where active=true "
#                     elif list.filter:
#                         requete += " Where " + list.filter
#                         requete_action += " Where " + list.filter
#                     self.env.cr.execute(requete.replace('"', "'"))
#                     result = self.env.cr.dictfetchall()[0]
#
#                     print ("#result--->>", result)
#
#                     field = result['field']
#                     self.env.cr.execute(requete_action.replace('"', "'"))
#                     result_ids = self.env.cr.dictfetchall()
#                     print ("#result_ids--->>", result_ids)
#                     res_ids = []

                    ###
                    eval_context = self._eval_context()
                    model   = str(list.model_id.model)
                    filter  = list.filter

                    # dom = safe_eval(list.filter, eval_context) if list.filter else []
                    # dom = expression.normalize_domain(dom)
                    if list.name=='Proforma Bills':
                        dom = [('todo_user_ids', 'in',self.env.uid),('company_id','=',self.env.company.id),('move_type', '=', 'in_invoice'),('is_proforma', '=', True)]
                    elif list.name=='Bills':
                        dom = [('todo_user_ids', 'in',self.env.uid),('company_id','=',self.env.company.id),('move_type', '=', 'in_invoice'),('is_proforma', '=', False)]
                    else:
                        dom = [('todo_user_ids', 'in',self.env.uid),('company_id','=',self.env.company.id)]
                    print('====>dom',dom)
                    if self.env.uid == 2:
                        if list.name=='Proforma Bills':
                            dom = [('company_id','=',self.env.company.id),('move_type', '=', 'in_invoice'),('is_proforma', '=', True)]
                        elif list.name=='Bills':
                            dom = [('company_id','=',self.env.company.id),('move_type', '=', 'in_invoice'),('is_proforma', '=', False)]
                        else:
                            dom = [('company_id','=',self.env.company.id)]
                    data = self.env[model].sudo().search(dom)
                    result = data
                    field = len(data)

                    result_ids = self.env.cr.dictfetchall()
                    res_ids = []
                    ###
                    for res in data:
                        print('=====>>>>MASUKKKKKK')
                        res_ids.append(res.id)
                    last_slices_list.append(
                        [
                            field,
                            list.name or list.field_id.field_description,
                            list.color, list.icon, action.id,
                            res_ids,list.custom_color
                        ])
        return last_slices_list

    def _get_default_chart(self):
        chart_list = []
        dashboard = self.env['dashboard.settings'].search([], limit=1, order='id desc')
        chart_ids = self.env['dashboard.settings.chart'].search([('dashboard_id', '=', dashboard.id)], order='sequence')
        for list in chart_ids:
            if list.display :
                if list.display_type=='area':
                    chart_list.append([list.id, list.name, 1])
                else:
                    chart_list.append([list.id, list.name, 2])
        return chart_list

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company',  string='Company',  required=True,  readonly=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency',  related='company_id.currency_id',  store=True,  string="Currency")
    field_list = fields.Selection('_compute_field_list', string='Slices names')
    chart_list=fields.Selection('_get_default_chart', string='Charts')

    
    def action_setting(self):
        action = self.env.ref('dashboard.action_dashboard_config').read()[0]
        setting = self.env['dashboard.settings'].search([], limit=1, order='id desc').id
        action['views'] = [(self.env.ref('dashboard.dashboard_config_settings').id,  'form')]
        action['res_id'] = setting
        return action

    
    def view_details(self):
        action = self.env['ir.actions.act_window'].search(
            [
                ('id', '=', self.env.context['action_id'])
            ], limit=1)
        print('===>1',self.env.context['action_id'])
        print('===>2',action)
        views = action.views
        for data in views:
            if data[1] == 'tree':
                tree_id = data[0]
            if data[1] == 'form':
                form_id = data[0]
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_mode': 'tree,form',
            # 'view_type': 'tree',
            'views': [[tree_id, 'list'], [form_id, 'form']],
            'target': action.target,
            'domain': [('id', 'in', self.env.context['active_ids'])],
            'context': {},
            'res_model': action.res_model,
        }
        return result
