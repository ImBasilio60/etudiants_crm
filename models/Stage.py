# code ecrit par BASILIO
from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Stage(models.Model):
    _name = 'etudiants.stage'
    _description = 'Stage Stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Titre du stage", required=True)
    etudiant_id = fields.Many2one('etudiants.etudiant', string="Étudiant", required=True)
    entreprise_id = fields.Many2one('res.partner', string="Entreprise d'accueil", required=True)
    date_debut = fields.Date(string="Date de début")
    date_fin = fields.Date(string="Date de fin")
    description = fields.Text(string="Description du stage")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminé'),
        ('annule', 'Annulé'),
    ], string="Statut", default="draft")
    attachment_ids = fields.Many2many(
        comodel_name = 'ir.attachment',
        relation = 'stage_attachment_rel',
        column1 = 'stage_id',
        column2 = 'attachment_id',
        string='Attachments'
    )

    @api.constrains('etudiant_id', 'state')
    def _check_unique_active_stage(self):
        for stage in self:
            if stage.state == 'en_cours':
                active_stages = self.env['etudiants.stage'].search([
                    ('etudiant_id', '=', stage.etudiant_id.id),
                    ('state', '=', 'en_cours'),
                    ('id', '!=', stage.id)
                ])

                if active_stages:
                    raise ValidationError(
                        "L'étudiant '%s' a déjà un autre stage en cours (Stages trouvés : %s). Veuillez le passer à l'état 'Terminé' ou 'Brouillon' avant d'en commencer un nouveau."
                        % (stage.etudiant_id.name, ", ".join(active_stages.mapped('name')))
                    )

