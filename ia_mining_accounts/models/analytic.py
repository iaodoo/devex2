# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

# ===========================
# Analytic Account inheritance
# ===========================

class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    tenement_company_id = fields.Many2one('res.company', string='Tenement Company')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id', '=?', country_id)]")
    company_id = fields.Many2one('res.company', string='Company', default=False)

# ===========================
# Analytic Group inheritance
# ===========================

class AnalyticGroup(models.Model):
    _inherit = 'account.analytic.group'

    tenement_company_id = fields.Many2one('res.company', string='Tenement Company')
    account_id = fields.Many2one('account.account', string='Default Account')
    company_id = fields.Many2one('res.company', string='Company', default=False)