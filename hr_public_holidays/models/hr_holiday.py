import logging
# import warning
import math
from datetime import timedelta, datetime, date

from odoo import api, fields, models, tools
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import float_compare
from odoo.tools.translate import _

HOURS_PER_DAY = 8

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def change_to_user_tz(self, date):
        """
        Take date and return it in the user timezone
        :param date:
        :return:
        """
        if not date:
            return False
        date_object = datetime.strptime(date,
                                        tools.DEFAULT_SERVER_DATETIME_FORMAT)
        date_user_tz = fields.Datetime.context_timestamp(self.sudo(self._uid),
                                                         date_object)
        date_user_tz_string = date_user_tz.strftime(DTF)
        return date_user_tz_string

    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.change_to_user_tz(self.date_from)
        date_to = self.change_to_user_tz(self.date_to)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            # self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
            num_days_raw = self._get_number_of_days(date_from, date_to, self.employee_id.id)

            self.compute_days(num_days_raw, date_from, date_to)
        else:
            self.number_of_days_temp = 0

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.change_to_user_tz(self.date_from)
        date_to = self.change_to_user_tz(self.date_to)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            num_days_raw = self._get_number_of_days(date_from, date_to, self.employee_id.id)

            self.compute_days(num_days_raw, date_from, date_to)
        else:
            self.number_of_days_temp = 0

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

    # def daterange(start_date, end_date):
    #     for n in range(int ((end_date - start_date).days)):
    #         yield start_date + timedelta(n)
    #
    # start_date = date(2013, 1, 1)
    # end_date = date(2015, 6, 2)
    # for single_date in daterange(start_date, end_date):
    #     print single_date.strftime("%Y-%m-%d")

    def daterange(self, date_from, date_to):
        """
        Take range of two dates and return all affected dates
        """
        date_from = datetime.strptime(date_from, DTF)
        date_to = datetime.strptime(date_to, DTF)

        for n in range(int((date_to - date_from).days) + 1):
            yield date_from + timedelta(n)

    def compute_days(self, number_of_days, date_from, date_to):
        """
        From a range of dates, compute the number of days that should be
        deducted from the leave (not counting weekends and public holidays)
        """
        if self.employee_id:
            self.number_of_days_temp = self.deduct_special_days(number_of_days)
        else:
            self.number_of_days_temp = number_of_days


    def deduct_special_days(self, number_of_days=0):
        """
        Remove the number of special days from the days count
        """
        days_to_deduct = 0

        date_from = self.change_to_user_tz(self.date_from)
        date_to = self.change_to_user_tz(self.date_to)

        special_days = self.get_special_days(date_from, date_to,
                                             self.employee_id)

        for date in special_days:
            days_to_deduct += 1

        days_without_special_days = number_of_days - days_to_deduct
        return days_without_special_days

    def get_special_days(self, date_from, date_to, employee):
        """
        Return dict of special days (Date: Name)

        Partly Deprecated: Since we now generate actual leave entries for
        public holidays they do no longer need to be deducted from the number
        of days (overlapping leaves cannot be created anyway). We should
        keep removing Sat/Sun and probably make it possible to remove other
        weekdays as well for countries with other work schedules
        """
        public_leave_ids = self.env['hr.public.holiday.holidays'].search([])

        special_days = {}

        for date in self.daterange(date_from, date_to):
            date_str = str(date.date())
            public_leave = public_leave_ids.filtered(
                lambda r: r.date == date_str)

            if public_leave:
                # raise ValidationError(public_leave.name)
                special_days[date.date()] = 'Public Holiday: %s' \
                                            % public_leave.name
                # return {
                #     'warning': {
                #         'title': "Something bad happened",
                #         'message': public_leave.name,
                #     }
                # }
            elif date.weekday() == 5:
                special_days[date.date()] = 'Saturday'
            elif date.weekday() == 6:
                special_days[date.date()] = 'Sunday'

        return special_days