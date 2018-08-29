from odoo import models, fields, api


class Employees(models.Model):
    _inherit = 'hr.employee'

    visa_type = fields.Selection(
        list(zip(('business', 'travel'), ('Business Visa', 'Travel Visa'))),
        'Type of Visa'
    )

    upload_file = fields.Binary(string='Upload File')
    file_name = fields.Char(string='File name')

    attachment_ids = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                      'Attachments')
