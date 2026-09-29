# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from datetime import datetime, timedelta, date
import logging
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from collections import OrderedDict
_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    last_month = fields.Integer("last", default=1)
    reset_seq = fields.Boolean('Reset Every Month')

    def write_roman(self, num):
        roman = OrderedDict()
        roman[1000] = "M"
        roman[900] = "CM"
        roman[500] = "D"
        roman[400] = "CD"
        roman[100] = "C"
        roman[90] = "XC"
        roman[50] = "L"
        roman[40] = "XL"
        roman[10] = "X"
        roman[9] = "IX"
        roman[5] = "V"
        roman[4] = "IV"
        roman[1] = "I"

        def roman_num(num):
            for r in roman.keys():
                x, y = divmod(num, r)
                yield roman[r] * x
                num -= (r * x)
                if num > 0:
                    roman_num(num)
                else:
                    break

        return "".join([a for a in roman_num(num)])

    def _get_prefix_suffix(self, date=None, date_range=None):
        def _interpolate(s, d):
            return (s % d) if s else ''

        def _interpolation_dict():
            now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
            if date or self._context.get('ir_sequence_date'):
                effective_date = fields.Datetime.from_string(date or self._context.get('ir_sequence_date'))
            if date_range or self._context.get('ir_sequence_date_range'):
                range_date = fields.Datetime.from_string(date_range or self._context.get('ir_sequence_date_range'))

            sequences = {
                'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S',
                # Additional dict for roman
                'rom_year': '%Y', 'rom_month': '%m', 'rom_y': '%y', 'rom_day': '%d'
            }
            res = {}
            for key, format in sequences.items():
                if "rom_" in key:
                    # Convert to Roman
                    res[key] = self.write_roman(int(effective_date.strftime(format)))
                    res['range_' + key] = self.write_roman(int(range_date.strftime(format)))
                    res['current_' + key] = self.write_roman(int(now.strftime(format)))
                else:
                    res[key] = effective_date.strftime(format)
                    res['range_' + key] = range_date.strftime(format)
                    res['current_' + key] = now.strftime(format)
            return res

        d = _interpolation_dict()
        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(_('Invalid prefix or suffix for sequence \'%s\'') % self.name)
        return interpolated_prefix, interpolated_suffix

    def _next(self, sequence_date=None):
        this_month = int(date.today().month)
        if self.reset_seq:
            if this_month != self.last_month:
                self.last_month = this_month
                self.sudo().number_next_actual = 1
        return super(IrSequence, self)._next()

