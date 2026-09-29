from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMVehicle(models.Model):
    _inherit = 'fsm.vehicle'

    @api.model
    def hide_menu(self):
        menu_to_hide = [
            "fieldservice.dashboard",
            "fieldservice.data",
            "fieldservice.reporting",
            "fieldservice.menu_fsm_operation_order",
            "fieldservice_route.menu_fsm_route_dayroute"
        ]
        for menu in menu_to_hide:
            try:
                menu_obj = self.env.ref(menu)
                menu_obj.update({
                    'active': False
                })
            except:
                pass
        return
