# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

# ===========================
# Company inheritance
# ===========================

class Company(models.Model):
    _inherit = 'res.company'

    interco_account_ids = fields.One2many('ia.inter.company.accounts', 'company_id')

class IntercoAccounts(models.Model):
    _name = 'ia.inter.company.accounts'

    company_id = fields.Many2one('res.company', 'Company')
    tenement_company_id = fields.Many2one('res.company', 'Tenement Company')
    main_account_id = fields.Many2one('account.account', 'Main Interco Account')
    tenement_account_id = fields.Many2one('account.account', 'Tenement Interco Account')
    main_journal_id = fields.Many2one('account.journal', 'Main Interco Journal')
    tenement_journal_id = fields.Many2one('account.journal', 'Tenement Interco Journal')
