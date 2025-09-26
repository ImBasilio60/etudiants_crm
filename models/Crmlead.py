# code ecrit par BASILIO
from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import ValidationError

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