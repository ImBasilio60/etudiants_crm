# code ecrit par BASILIO

from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Etudiant(models.Model):
    _name = 'etudiants.etudiant'
    _description = 'Informations Etudiant'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom de l'Étudiant", required=True)
    numero_etudiant = fields.Char(string="Numéro d'Étudiant", required=True, copy=False)
    projet_pfe = fields.Char(string="Titre du Projet PFE")
    tuteur_id = fields.Many2one('res.partner', string="Tuteur")

    attachment_ids = fields.Many2many(
        comodel_name = 'ir.attachment',
        relation = 'etudiant_attachment_rel',
        column1 = 'etudiant_id',
        column2 = 'attachment_id',
        string="Attachments"
    )

    stage_ids = fields.One2many('etudiants.stage', 'etudiant_id', string="Stages")
    stage_count = fields.Integer(compute='_compute_stage_count', string="Nombre de stages")

    @api.depends('stage_ids')
    def _compute_stage_count(self):
        for etudiant in self:
            etudiant.stage_count = len(etudiant.stage_ids)

    def action_view_stages(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stages de %s' % (self.name,),
            'res_model': 'etudiants.stage',
            'view_mode': 'tree,form,kanban',
            'domain': [('etudiant_id', '=', self.id)],
            'context': {'default_etudiant_id': self.id},
        }
