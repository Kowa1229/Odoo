from odoo import api, fields, models
from datetime import date
from pprint import pprint

class HumanResource(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    # test = fields.Char('test')

    # Profiling Details
    food_ids = fields.One2many(
        'hr.employee.food',
        'employee_id',
        string='Food Cost'
    )
    # Accommodation
    board_ids = fields.One2many(
        'hr.employee.board',
        'employee_id',
        string='Board Cost'
    )
    # Transport = Land, Air, Sea
    transport_ids = fields.One2many(
        'hr.employee.transport',
        'employee_id',
        string='Transport Cost'
    )
    # Two type employee.
    employee_type = fields.Selection(
        [
            ('expat', 'Expat'),
            ('local', 'Local')
        ], string='Employee Type'
    )

    insurance_count = fields.Integer(compute='_compute_insurance_count', string='Insurance')

    def _compute_insurance_count(self):
        insurance_counts = self.env['hr.insurance'].read_group([('employee_id', 'in', self.ids)],
                                                               ['employee_id'], ['employee_id'])
        mapped_data = dict([(m['employee_id'][0], m['employee_id_count']) for m in insurance_counts])
        for insurance in self:
            insurance.insurance_count = mapped_data.get(insurance.id, 0)

    # Extra Work Permit Information
    permit_expire = fields.Date('WP Expire Date', groups="hr.group_hr_user")
    permit_duration = fields.Selection(
        [
            ('12', '12 Months'),
            ('24', '24 Months'),
            ('36', '36 Months'),
            ('48', '48 Months'),
            ('60', '60 Months')
        ], string='WP duration'
    )
    permit_cost = fields.Float('WP Cost', groups="hr.group_hr_user")
    permit_image = fields.Binary('WP Image', attachment=True, groups="hr.group_hr_user")

    # Extra Visa Information
    visa_duration = fields.Selection(
        [
            ('12', '12 Months'),
            ('24', '24 Months'),
            ('36', '36 Months'),
            ('48', '48 Months'),
            ('60', '60 Months')
        ], string='Visa duration'
    )
    visa_cost = fields.Float('Visa Cost', groups="hr.group_hr_user")
    visa_image = fields.Binary('Visa Image', attachment=True, groups="hr.group_hr_user")

    # All Cost
    total_wp_cost = fields.Float('Total WP', compute='_compute_wp_cost')
    total_visa_cost = fields.Float('Total Visa', compute='_compute_visa_cost')
    total_transport_cost = fields.Float('Total Transport', compute='_compute_transport_cost')
    total_board_cost = fields.Float('Total Board', compute='_compute_board_cost')
    total_food_cost = fields.Float('Total Food', compute='_compute_food_cost')
    total_cost = fields.Float('Net Total', compute='_compute_total_cost')

    def _compute_wp_cost(self):
        for wp in self:
            if(wp.permit_cost and int(wp.permit_duration)):
                wp.total_wp_cost = wp.permit_cost / int(wp.permit_duration)
            else:
                wp.total_wp_cost = 0.00

    def _compute_visa_cost(self):
        for visa in self:
            if(visa.visa_cost and visa.visa_duration):
                visa.total_visa_cost = visa.visa_cost / int(visa.visa_duration)
            else:
                visa.total_visa_cost = 0.00

    def _compute_transport_cost(self):
        for transport in self:
            transport.total_transport_cost = sum(t.transport_cost for t in transport.transport_ids)

    def _compute_board_cost(self):
        for board in self:
            board.total_board_cost = sum(b.board_cost for b in board.board_ids)

    def _compute_food_cost(self):
        for food in self:
            food.total_food_cost = sum(f.food_cost for f in food.food_ids)

    def _compute_total_cost(self):
        for total in self:
            if(total.permit_cost and int(total.permit_duration)):
                total.total_cost = total.total_cost + (total.permit_cost / int(total.permit_duration))
            else:
                total.total_cost = total.total_cost

            if(total.visa_cost and total.visa_duration):
                total.total_cost = total.total_cost + (total.visa_cost / int(total.visa_duration))
            else:
                total.total_cost = total.total_cost

            total.total_cost = total.total_cost + (sum(t.transport_cost for t in total.transport_ids))
            total.total_cost = total.total_cost + (sum(t.board_cost for t in total.board_ids))
            total.total_cost = total.total_cost + (sum(t.food_cost for t in total.food_ids))

class HrSalary(models.Model):
    _name = "hr.employee.salary"
    _description = "Salary"

class HrFood(models.Model):
    _name = "hr.employee.food"
    _description = "Employee Food"

    employee_id = fields.Many2one('hr.employee', string='Employee Name')

    name = fields.Char(
        string='Food Name',
        required=True,
        help='Please Enter the Food Name'
    )

    food_category = fields.Selection(
        [('breakfast', 'Breakfast'),
         ('lunch', 'Lunch'),
         ('teatime', 'Tea Time'),
         ('dinner', 'Dinner'),
         ('supper', 'Supper')],
        string='Category',
        required=True
    )
    food_cost = fields.Float(
        string='Food Amount',
        digits=(5, 2),
        required=True
    )



class HrBoard(models.Model):
    _name = "hr.employee.board"
    _description = "Board"

    employee_id = fields.Many2one('hr.employee', 'Board')
    name = fields.Char('Board Name', required=True)
    board_type = fields.Selection(
        [('weekly', 'Weekly'),
         ('monthly', 'Monthly'),
         ('yearly', 'Yearly')],
        string='Board Type',
        required=True
    )

    board_cost = fields.Float(
        string='Board Cost',
        digits=(5,2),
        required=True
    )

class HrTransport(models.Model):
    _name = "hr.employee.transport"
    _description = "Transport"

    employee_id = fields.Many2one('hr.employee', 'Transport')
    name = fields.Char('Transport Name',required=True)
    transport_type = fields.Selection(
        [('land', 'Land'),
         ('sea', 'Sea'),
         ('air', 'Air')],
        string='Transport Type',
        required=True,
    )

    transport_cost = fields.Float(
        string='Transport Cost',
        digits=(5,2),
        required=True,
    )

    transport_date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.today(),
        required=True,
    )