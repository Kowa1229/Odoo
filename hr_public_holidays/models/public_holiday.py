from datetime import date, datetime, timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import base64
import codecs

class PublicHoliday(models.Model):
    _name = 'hr.public.holiday'
    _description = 'Public Holidays'
    
    name = fields.Char(string='Holiday Name', compute="_compute_name", required=True)
    year = fields.Integer(
        "Calendar Year",
        required=True,
        default=datetime.now().year
    )
    holiday_ids = fields.One2many('hr.public.holiday.holidays', 'year_id', 'Holidays')
    # company_id = fields.Many2one('res.company', 'Company')

    # Email fields
    public_holiday_email_filter_by = fields.Selection(
        [('department', 'Department'),
         ('employee', 'Employee')],
        string='Send Email By',
        # default='department',
        # required=True,
    )
    public_holiday_email_department_ids = fields.One2many(
        'hr.department',
        'department_email_for_holiday',
        string='Departments'
    )
    public_holiday_email_employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees'
    )

    @api.multi
    @api.depends('year')
    def _compute_name(self):
        self.name = 'Public Holidays (%s)' % (self.year)

    @api.multi
    def send_email(self):
        self.ensure_one()
        view_id = self.env.ref('hr_public_holidays.public_holiday_send_email_form').id
        return {
            'name':'public_holiday_send_email_form',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'hr.public.holiday',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new',
        }

    @api.multi
    def send_mail_action(self):
        """ This function would send the emails """
        if self.public_holiday_email_filter_by:
            if self.public_holiday_email_filter_by == 'department':
                total_department_ids = self.public_holiday_email_department_ids

                for department_ids in total_department_ids:
                    dep_emp_ids = self.env['hr.employee'].search([('department_id', '=', department_ids.id)])

                    for emp_ids in dep_emp_ids:
                        self.action_mail_content(emp_ids.id)
            else:
                total_employee_ids = self.public_holiday_email_employee_ids

                for emp_ids in total_employee_ids:
                    self.action_mail_content(emp_ids.id)

        else:
            raise ValidationError('Please select filter by which category')


    # Send Public Holiday by Email Functions
    def action_mail_content(self, emp_id):
        employee_details = self.env['hr.employee'].search([('id', '=', emp_id)], limit=1)

        mail_content = "Dear " + employee_details.name + "," + "<br><br>This Year Public Holiday list attached in this mail " \
                       "<br><br>You can reply to this email if you have any question." \
                       "<br><br>Thank you." + \
                       "<br><br>" + self.env.user.name

        # attachment_obj = self.pool.get('ir.attachment')
        # ir_actions_report = self.pool.get('ir.actions.reports.xml')
        # matching_report = ir_actions_report.search([('name', '=', 'hr_public_holidays.report_public_holidays')])
        #
        # if matching_report:
        #     report = ir_actions_report.browse(matching_report[0])
        #     report_service = 'report.' + report.report_name
        #     service = netsvc.LocalService

        # raise ValidationError(att);
        #
        values = {'model': 'hr.public.holiday',
                  'res_id': self.ids[0],
                  'subject': self.name,
                  'body_html': mail_content,
                  'parent_id': None,
                  'email_from': self.env.user.email or None,
                  }
        # Define receiver email address
        values['email_to'] = employee_details.work_email

        # attachment = self.env.ref('hr_public_holidays.action_hr_public_holidays_report').report_action(self, data=None)
        #
        # # raise ValidationError(attachment)
        #
        # attachment_binary = self.env['ir.attachment'].create({
        #     'name': 'Public Holiday Lists',
        #     'type': 'binary',
        #     'datas': base64.b64encode(bytes(attachment, "utf-8")),
        #     # 'datas': codecs.encode(bytes(attachment, 'utf8'), 'base64'),
        #     # 'datas': base64.b64encode(attachment),
        #     'datas_fname': 'PublicHolidayLists.pdf',
        #     'res_model': 'hr.public.holiday',
        #     'res_id': self.id,
        #     'mimetype': 'application/x-pdf',
        # })

        # attachment = self.env.ref('hr_public_holidays.action_hr_public_holidays_report').report_action(self, data=None)
        #
        # # raise ValidationError(attachment)
        #
        # attachment_ids = []
        # attachment_binary = self.env['ir.attachment'].create({
        #     'name': 'Public Holiday Lists',
        #     'type': 'binary',
        #     # 'datas': base64.encodestring(attachment),
        #     # 'datas': codecs.encode(bytes(attachment, 'utf8'), 'base64'),
        #     'datas': base64.b64encode(attachment),
        #     'datas_fname': 'PublicHolidayLists.pdf',
        #     'res_model': 'hr.public.holiday',
        #     'res_id': self.id,
        #     'mimetype': 'application/x-pdf',
        # })
        #
        # attachment_ids.append(attachment_binary)
        # values['attachment_ids'] = [(6, 0, attachment_ids)]

        # raise ValidationError(values)

        # Send email
        result = self.env['mail.mail'].create(values)._send()
        # mail_obj = self.env['mail.mail'].create(values)

        # att_obj = self.env['ir.attachment'].create({
        #     'name': 'Public Holiday Lists',
        #     'type': 'binary',
        #     'datas': base64.encodestring(data),
        #     'datas_fname': 'PublicHolidayLists.pdf',
        #     'res_model': 'hr.public.holiday',
        #     'res_id': mail_obj.id,
        #     'mimetype': 'application/x-pdf',
        # })
        #
        # report = self.env.ref('hr_public_holidays.report_public_holidays').report_action(self, data=data)
        # attachment_ids = ir_attachment.create
        # mail_obj.write({'attachment_ids': [(6,0,0)]})
        # #
        # mail_obj._send()

        if result:
            return True