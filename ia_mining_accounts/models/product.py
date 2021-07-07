# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

# ===========================
# Product inheritance
# ===========================

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allowed_company_ids = fields.Many2many('res.company', relation='product_template_company_relation', string="Allowed Companies")
    allowed_country_ids = fields.Many2many('res.country', relation='product_template_country_relation', string="Allowed Countries")
    allowed_state_ids = fields.Many2many('res.country.state', relation='product_template_state_relation', string="Allowed States")

    # Populate States based on the selected Countries
    @api.onchange('allowed_country_ids')
    def onchange_countries(self):
        selected_lines = []
        if self.allowed_country_ids:
            for rec in self:
                selected_lines = rec.env['res.country.state'].search([('country_id', 'in', rec.allowed_country_ids.ids)])
                domain = {'allowed_state_ids': [('id', 'in', selected_lines.ids)]}
            return {'domain': domain, 'value': {'selected_lines': []}}
