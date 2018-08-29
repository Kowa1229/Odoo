from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HrInsuranceHrEmployeeRel(models.Model):
    _name = 'hr.insurance.hr.employee.rel'
    _description = 'Relations between Insurance and Employee'

    name = fields.Many2one('hr.insurance', string='Insurance', required=True)
    insurance_variance_id = fields.Many2one('hr.insurance.variance', string='Variance')
    employee_id = fields.Many2one('hr.employee', string='Employee ID')
    variance_type = fields.Char('Variance Type', compute='_compute_variance_type', store=False)
    variance_value = fields.Char('Variance Value', compute='_compute_variance_value', store=False)

    @api.onchange('insurance_variance_id')
    def _onchange_variance(self):
        if self.insurance_variance_id:
            self.variance_type = self.insurance_variance_id.variance_by.title()
            self.variance_value = self.insurance_variance_id.value

    def _compute_variance_type(self):
        for vt in self:
            if vt.insurance_variance_id:
                vt.variance_type = vt.insurance_variance_id.variance_by.title()
            else:
                vt.variance_type = 'N/A'

    def _compute_variance_value(self):
        for va in self:
            if va.insurance_variance_id:
                va.variance_value = va.insurance_variance_id.value
            else:
                va.variance_value = 'N/A'

class HrInsurance(models.Model):
    _name = 'hr.insurance'
    _description = 'Insurance'
    _inherit = ['mail.thread']

    # name = fields.Char('Descriptions', required=True, help="The descriptions of this insurance.")
    name = fields.Many2one('hr.insurance.type', string='Type', required=True, help="The type of the insurance.")
    ref_no = fields.Char('Ref No.', readonly=True)
    # employee_id = fields.Many2one('hr.employee', string='Employee Name')
    insurance_start_date = fields.Date('Start Date', default=lambda self:fields.Date.today())
    insurance_expired_date = fields.Date('Expired Date', default=lambda self:fields.Date.today())
    insurance_amount = fields.Float('Amount', digits=(5,2), default=0.00, required=True)
    broker_company = fields.Many2one('res.partner', string='Broker Company Name', default=False)
    broker_agent = fields.Many2one('res.partner', string='Broker Contact Agent')
    broker_agent_hp_num = fields.Char('Agent Number')
    company_id = fields.Many2one('res.company', string='Company Name')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'hr.insurance')], string='Attachments')
    variance_ids = fields.One2many('hr.insurance.variance', 'parent_id', string='Insurance Company')
    employee_ids = fields.One2many('hr.insurance.hr.employee.rel', 'name', string='Employees under this insurance')
    stage = fields.Selection([
        ('draft', 'To Submit'),
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('renew', 'To Renew'),
        ('expired', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, default='pending', group_expand='_expand_stages')

    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'hr.insurance'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    @api.multi
    def action_get_attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
        action['search_view_id'] = (self.env.ref('HR.ir_attachment_view_search_inherit_hr_insurance').id, )
        return action

    def _expand_stages(self, stages, domain, order):
        return [key for key, val in type(self).stage.selection]

    @api.model
    def create(self,vals):
        vals['ref_no'] = self.env['ir.sequence'].next_by_code('hr.insurance.sequence')
        return super(HrInsurance,self).create(vals)

    @api.onchange('broker_agent')
    def _onchange_broker_agent(self):
        if self.broker_agent:
            self.broker_agent_hp_num = self.broker_agent.phone

    @api.onchange('broker_company')
    def _onchange_broker_company(self):
        if self.broker_agent:
            self.broker_agent = False
            self.broker_agent_hp_num = ''

    @api.multi
    def action_draft(self):
        if self.stage not in ['pending', 'cancel', 'renew', 'expired']:
            raise ValidationError('Insurance stage must be "Pending" or "Cancel" or "Renew" or "Expired" in order to reset to Draft.')

        return self.write({'stage': 'draft'})

    @api.multi
    def action_pending(self):
        if self.stage != 'draft':
            raise ValidationError('Insurance stage must be "Draft" stage in order to make it to Pending.')

        return self.write({'stage': 'pending'})

    @api.multi
    def action_cancel(self):
        if self.stage != 'pending':
            raise ValidationError('Insurance stage must be "Pending" in order to Cancel.')

        return self.write({'stage': 'cancel'})

    @api.multi
    def action_running(self):
        if self.stage not in ['pending', 'renew']:
            raise ValidationError('Insurance stage must be "Pending" or "Renew" in order to Set to Running.')

        return self.write({'stage': 'running'})

    @api.multi
    def action_expired(self):
        if self.stage != 'running':
            raise ValidationError('Insurance stage must be "Approve" in order to make it Expired.')

        return self.write({'stage': 'expired'})

    @api.multi
    def action_renew(self):
        if self.stage not in ['running', 'expired']:
            raise ValidationError('Insurance stage must be "Running" or "Expired" in order to Renew stage.')

        return self.write({'stage': 'renew'})

class HrInsuranceType(models.Model):
    _name = 'hr.insurance.type'
    _description = 'Insurance Type'

    name = fields.Char('Insurance Type', required=True)
    # insurance_id = fields.One2many('hr.employee', 'name', string='Insurance Ids')
    cover_ids = fields.Many2many('hr.insurance.coverage', string='Insurance Coverage')

    _sql_constraints = [
        ('insurance_type_name_unique',
         'UNIQUE (name)',
         'Insurance Type Name Must be Unique')
    ]

class HrInsuranceCoverage(models.Model):
    _name = 'hr.insurance.coverage'
    _description = 'Insurance Coverage'

    name = fields.Char('Description', required=True, help="Insert the description of the Insurance Coverage.")
    parent_type_ids = fields.Many2many('hr.insurance.type', string='Parent Type')
    ref_code = fields.Char('Reference Code')

    _sql_constraints = [
        ('insurance_cover_type_name_unique',
         'UNIQUE (name)',
         'Description Must be Unique')
    ]

class HrInsuranceVariance(models.Model):
    _name = 'hr.insurance.variance'
    _description = 'Insurance Variance'

    name = fields.Char('Description', required=True)
    variance_by = fields.Selection([
        ('percentage', 'Percentage'),
        ('amount', 'Fixed Max Amount')
    ], string='Variance Type', default='percentage', required=True)
    value = fields.Float('Value', digits=(5,2), default=0.00, required=True)
    parent_id = fields.Many2one('hr.insurance', string='Parent ID')
    employee_variance = fields.One2many('hr.insurance.hr.employee.rel', 'insurance_variance_id', string='Employees')

    # insurance_variance_id = fields.One2many('hr.insurance.variance', 'employee_variance', string='Variance')

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    insurance_ids = fields.One2many('hr.insurance.hr.employee.rel', 'employee_id', string='Insurance', required=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    insurance_company_ids = fields.One2many('hr.insurance', 'broker_company',string='Insurance Company')
    insurance_agent_ids = fields.One2many('hr.insurance', 'broker_agent',string='Insurance Company')