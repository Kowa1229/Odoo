from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HrInsurance(models.Model):
    _name = 'hr.insurance'
    _description = 'Insurance'
    _inherit = ['mail.thread']

    # name = fields.Char('')
    name = fields.Many2one('hr.insurance.type', string='Insurance Type', required=True)
    ref_no = fields.Char('Ref No.', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee Name')
    insurance_start_date = fields.Date('Start Date', default=lambda self:fields.Date.today())
    insurance_expired_date = fields.Date('Expired Date', default=lambda self:fields.Date.today())
    insurance_amount = fields.Float('Insurance Amount', digits=(5,2), default=0.00, required=True)
    insurance_company = fields.Many2one('res.partner', string='Company Name')
    insurance_agent = fields.Many2one('res.partner', string='Agent Name')
    insurance_agent_hp_num = fields.Char('H.P Number')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('renew', 'To Renew'),
        ('expired', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, default='pending', group_expand='_expand_states')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.model
    def create(self,vals):
        vals['ref_no'] = self.env['ir.sequence'].next_by_code('hr.insurance.sequence')
        return super(HrInsurance,self).create(vals)

    @api.onchange('insurance_agent')
    def _onchange_insurance_agent(self):
        if self.insurance_agent:
            self.insurance_agent_hp_num = self.insurance_agent.phone

    @api.onchange('insurance_company')
    def _onchange_insurance_company(self):
        if self.insurance_agent:
            self.insurance_agent = False
            self.insurance_agent_hp_num = ''

    @api.multi
    def action_draft(self):
        if self.state not in ['pending', 'cancel']:
            raise ValidationError('Insurance state must be "Pending" or "Cancel" in order to reset to Draft.')

        return self.write({'state': 'draft'})

    @api.multi
    def action_pending(self):
        if self.state != 'draft':
            raise ValidationError('Insurance state must be "Draft" state in order to make it to Pending.')

        return self.write({'state': 'pending'})

    @api.multi
    def action_cancel(self):
        if self.state != 'pending':
            raise ValidationError('Insurance state must be "Pending" in order to Cancel.')

        return self.write({'state': 'cancel'})

    @api.multi
    def action_approve(self):
        if self.state != 'pending':
            raise ValidationError('Insurance state must be "Pending" in order to Approve.')

        return self.write({'state': 'approve'})

    @api.multi
    def action_expired(self):
        if self.state != 'approve':
            raise ValidationError('Insurance state must be "Approve" in order to make it Expired.')

        return self.write({'state': 'expired'})

    @api.multi
    def action_renew(self):
        if self.state != 'approve':
            raise ValidationError('Insurance state must be "Approve" in order to Renew state.')

        return self.write({'state': 'renew'})

class HrInsuranceType(models.Model):
    _name = 'hr.insurance.type'
    _description = 'Insurance Type'

    name = fields.Char('Insurance Type', required=True)
    insurance_id = fields.One2many('hr.employee', 'name', string='Insurance Ids')

    _sql_constraints = [
        ('insurance_type_name_unique',
         'UNIQUE (name)',
         'Insurance Type Name Must be Unique')
    ]

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    insurance_ids = fields.One2many('hr.insurance', 'employee_id', string='Insurance')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    insurance_company_ids = fields.One2many('hr.insurance', 'insurance_company',string='Insurance Company')
    insurance_agent_ids = fields.One2many('hr.insurance', 'insurance_agent',string='Insurance Company')