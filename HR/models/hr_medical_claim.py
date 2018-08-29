from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError

class HrMedicalClaimStage(models.Model):
    _name = "hr.medical.claim.stage"
    _description = 'Stage of Medical Claim'
    _order = 'sequence'

    name = fields.Char("Stage name", required=True)
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order when displaying a list of stages.")
    fold = fields.Boolean("Folded in Medical Claim Page?", help="This stage is folded in the kanban view when there are no records in that stage to display")

class HrMedicalClaim(models.Model):
    _name = 'hr.medical.claim'
    _description = 'Medical Claim'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _default_stage_id(self):
        ids = self.env['hr.medical.claim.stage'].search([], order='sequence asc', limit=1).ids
        if ids:
            return ids[0]
        return False

    name = fields.Many2one('hr.employee', string='Employee Name', default=_default_employee, required=True)
    insurance_id = fields.Many2one('hr.insurance.hr.employee.rel', string='Insurance Policy', required=True, help="The insurance policy you wish to claim.")
    ref_no = fields.Char('Ref No.', readonly=True)
    file_number = fields.Char('File No.')
    total_claimed_amount = fields.Float('Total Claimed', digits=(5,2), default=0.00, required=True)
    date = fields.Date('Date', default=lambda self:fields.Date.today())
    stage_id = fields.Many2one('hr.medical.claim.stage', 'Status',
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids',
                               default=_default_stage_id)
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'hr.medical.claim')], string='Attachments')
    last_stage_id = fields.Many2one('hr.medical.claim.stage', string="Last Status", readonly=True, help="Stage of the medical claim before being in the current stage.")
    date_last_stage_update = fields.Datetime("Last Stage Update Time", index=True, readonly=True, default=fields.Datetime.now)

    # Compute Policy Information
    variance = fields.Char('Variance', compute='_compute_variance_name', store=False, readonly=True)
    variance_by = fields.Char('Type', compute='_compute_variance_by', store=False, readonly=True)
    variance_value = fields.Char('Amount', compute='_compute_variance_value', store=False, readonly=True)

    def _compute_variance_name(self):
        for vn in self:
            if vn.insurance_id:
                vn.variance = vn.insurance_id.insurance_variance_id.name
            else:
                raise ValidationError(vn.insurance_id.insurance_variance_id.name)
                vn.variance = 'N/A'

    def _compute_variance_by(self):
        for vb in self:
            if vb.insurance_id:
                vb.variance_by = vb.insurance_id.insurance_variance_id.variance_by
            else:
                vb.variance_by = 'N/A'

    def _compute_variance_value(self):
        for va in self:
            if va.insurance_id:
                va.variance_value = va.insurance_id.insurance_variance_id.value
            else:
                va.variance_value = 'N/A'

    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'hr.medical.claim'), ('res_id', 'in', self.ids)],
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
        action['search_view_id'] = (self.env.ref('HR.ir_attachment_view_search_inherit_hr_medical_insurance').id, )
        return action

    @api.onchange('insurance_id')
    def _onchange_insurance_id(self):
        if self.insurance_id:
            if self.insurance_id.insurance_variance_id:
                self.variance = self.insurance_id.insurance_variance_id.name
                self.variance_by = self.insurance_id.insurance_variance_id.variance_by
                self.variance_value = self.insurance_id.insurance_variance_id.value
            else:
                self.variance = self.variance_by = self.variance_value = 'N/A'
                # self.variance = 'N/A'
                # self.variance_by = 'N/A'
                # self.variance_value = 'N/A'

    def _onchange_stage_id_internal(self, stage_id):
        if not stage_id:
            return {'value': {}}

    @api.model
    def create(self, vals):
        vals['ref_no'] = self.env['ir.sequence'].next_by_code('hr.medical.claim.sequence')
        return super(HrMedicalClaim, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
            for medical_claim in self:
                vals['last_stage_id'] = medical_claim.stage_id.id
                res = super(HrMedicalClaim, self).write(vals)
        else:
            res = super(HrMedicalClaim, self).write(vals)
        return res

    @api.model
    def _read_group_stage_ids(self, stages, domain ,order):
        # Retrieve all stage
        search_domain = []

        stage_ids = stages._search(search_domain, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)