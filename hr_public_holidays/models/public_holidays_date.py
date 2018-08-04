from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import calendar

class HrPublicHolidayHolidays(models.Model):
    _name = 'hr.public.holiday.holidays'
    _description = 'Public Holidays Dates'

    name = fields.Char('Holiday Name', required=True)
    date = fields.Date('Holiday Date', required=True)
    date_day = fields.Char('Day')
    year_id = fields.Many2one('hr.public.holiday', 'Calendar Year', required=True)
    variable = fields.Boolean('Date may change')

    @api.onchange('date')
    def _get_day_of_date(self):
        for r in self:
            if r.date:
                selected = fields.Datetime.from_string(r.date)
                r.date_day = calendar.day_name[selected.weekday()]

    @api.multi
    @api.constrains('date')
    def _check_date_state(self):
        for r in self:
            r._check_date_state_one()

    def _check_date_state_one(self):
        if fields.Date.from_string(self.date).year != self.year_id.year:
            raise ValidationError(_(
                'Dates of holidays should be the same year '
                'as the calendar year they are being assigned to'
            ))

        domain = [('date', '=', self.date),
                  ('year_id', '=', self.year_id.id)]
        if self.search_count(domain) > 1:
            raise ValidationError(_('You can\'t create duplicate public holiday '
                              'per date %s.') % self.date)
        return True
