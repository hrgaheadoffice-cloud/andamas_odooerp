from odoo import api, fields, models
from datetime import datetime
from requests import request
import json
import logging

_logger = logging.getLogger(__name__)


class SmartminingHyperlink(models.Model):
    _name = 'smartmining.hyperlink'

    name = fields.Char()

    def get_user_data(self):
        uid = self.env.user.id
        data = self.env['res.users'].browse(uid).data
        return data

    def get_link(self):
        link = self.env["ir.config_parameter"].sudo().get_param("smartmining_link")
        return link
