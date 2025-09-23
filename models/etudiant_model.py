# code ecrit par BASILIO

from odoo import models, fields

class Etudiant(models.Model):
    _name = 'etudiants.etudiant'
    _description = 'Informations Etudiant'

    name = fields.Char(string="Nom de l'Étudiant", required=True)
    numero_etudiant = fields.Char(string="Numéro d'Étudiant", required=True, copy=False)
    projet_pfe = fields.Char(string="Titre du Projet PFE")
    tuteur_id = fields.Many2one('res.partner', string="Tuteur")

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    etudiant_id = fields.Many2one('etudiants.etudiant', string="Etudiant", copy=False)
    numero_etudiant = fields.Char(string="Numéro d'Étudiant", required=True, copy=False)
    projet_pfe = fields.Char(string="Titre du Projet PFE")
    tuteur_id = fields.Many2one('res.partner', string="Tuteur")

    def action_convertir_en_etudiant(self):
        self.ensure_one()

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
