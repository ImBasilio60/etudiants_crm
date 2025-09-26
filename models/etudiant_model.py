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

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    etudiant_id = fields.Many2one('etudiants.etudiant', string="Etudiant", copy=False)
    numero_etudiant = fields.Char(string="Numéro d'Étudiant", required=True, copy=False)
    projet_pfe = fields.Char(string="Titre du Projet PFE")
    tuteur_id = fields.Many2one('res.partner', string="Tuteur")

    def action_convertir_en_etudiant(self):
        self.ensure_one()
        if self.etudiant_id:
            etudiant = self.etudiant_id
        else:
            etudiant = self.env['etudiants.etudiant'].create({
                'name': self.contact_name,
                'numero_etudiant': self.numero_etudiant,
                'projet_pfe': self.projet_pfe,
                'tuteur_id': self.tuteur_id.id,
            })
            self.etudiant_id = etudiant.id

        return {
            'type':'ir.actions.act_window',
            'res_model': 'etudiants.etudiant',
            'res_id': etudiant.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
        }

    def _mettre_a_jour_projets_sans_tuteur(self):

        leads_a_mettre_a_jour = self.search([
            ('tuteur_id', '=', False),
            ('stage_id.sequence', '<', 2)
        ])
        for lead in leads_a_mettre_a_jour:
            qualification_stage = self.env['crm.stage'].search([('name', '=', 'Qualification')], limit=1)
            if qualification_stage:
                lead.stage_id = qualification_stage.id

    _sql_constraints = [
        ('numero_etudiant_unique',
         'UNIQUE (numero_etudiant)',
         "Le numéro d'Étudiant doit être unique.")
    ]

    @api.constrains('numero_etudiant', 'stage_id')
    def _check_unique_in_progress_opportunity(self):
        for lead in self:
            if lead.stage_id.is_won == False and lead.active == True:
                domain = [
                    ('id', '!=', lead.id),
                    ('numero_etudiant', '=', lead.numero_etudiant),
                    ('active', '=', True),
                    ('type', '=', 'opportunity')
                ]

                if self.search_count(domain) > 0:
                    raise ValidationError(
                        "Cet Étudiant a déjà un Projet/Stage 'En cours' actif. "
                        "Vous devez d'abord fermer l'opportunité existante pour en créer une nouvelle."
                    )

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

