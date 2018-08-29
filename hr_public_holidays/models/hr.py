from odoo import api, fields, models

class HrEmployeePublicHoliday(models.Model):
    _inherit = 'hr.employee'

    employee_email_for_holiday = fields.Many2many('hr.public.holiday', string='Employee Public Holiday Email List')

class HrEmployeePublicHoliday(models.Model):
    _inherit = 'hr.department'

    department_email_for_holiday = fields.Many2one('hr.public.holiday', 'Department Public Holiday Email List')