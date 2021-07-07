# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

# ===========================
# Activity
# ===========================

class AccountActivity(models.Model):
    _name = 'ia.account.activity'

    name = fields.Char('Activity')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id', '=?', country_id)]")

# ===========================
# Tags
# ===========================

class AccountTags(models.Model):
    _name = 'ia.account.tags'

    name = fields.Char('Tag')

# ===========================
# Invoice Line inheritance
# ===========================

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tenement_company_id = fields.Many2one('res.company', string='Company')
    analytic_group_id = fields.Many2one('account.analytic.group', string='Project')
    activity_id = fields.Many2one('ia.account.activity', string='Activity')
    tag_id = fields.Many2one('ia.account.tags', string='Tag')
    tenement_state_id = fields.Many2one(related='analytic_account_id.state_id', string="Tenement State")

    # Populate Account from Analytic Account Group
    @api.onchange('analytic_account_id', 'product_id')
    def onchange_account(self):
        for data in self:
            if data.analytic_account_id:
                if data.analytic_account_id.group_id:
                    if data.analytic_account_id.group_id.account_id:
                        if data.move_id.company_id == data.analytic_account_id.group_id.account_id:
                            data.account_id = data.analytic_account_id.group_id.account_id
                        else:
                            #Block if the account in group does not exist in the parent company, else find the account code and set it
                            gl_id = self.env['account.account'].search([
                                ('company_id', '=', data.move_id.company_id.id),
                                ('code', '=', data.analytic_account_id.group_id.account_id.code),
                            ])
                            if gl_id:
                                data.account_id = gl_id[0]
                            else:
                                raise UserError(_("The Account %s belonging to the tenemant %s does not exist in %s") 
                                % (data.analytic_account_id.group_id.account_id.code, data.analytic_account_id.name, data.move_id.company_id.name))

    # Populate Analytic Tag based on tenement company
    @api.onchange('tenement_company_id')
    def onchange_tenement_company(self):
        for data in self:
            if data.tenement_company_id:
                if data.move_id.company_id == data.tenement_company_id:
                    analytic_tag_id = self.env['account.analytic.tag'].search([('name','=','Unhide')])
                    if analytic_tag_id:
                        analytic_tag_id = analytic_tag_id[0]
                else:
                    analytic_tag_id = self.env['account.analytic.tag'].search([('name','=','Hide')])
                    if analytic_tag_id:
                        analytic_tag_id = analytic_tag_id[0]
                
                data.analytic_tag_ids = [(6, 0, [analytic_tag_id.id])]

    #=====================================================
    #Classs : AccountMoveLine
    #Method :_prepare_analytic_line
    #=====================================================
    def _prepare_analytic_line(self):
        result = super(AccountMoveLine, self)._prepare_analytic_line()
        if result:
            for move_line in self:
                for res in result:
                    res['company_id'] = move_line.analytic_account_id.company_id.id or  move_line.company_id.id,
        return result

# ===========================
# Account Move inheritance
# ===========================

class AccountMove(models.Model):
    _inherit = 'account.move'
    inter_move_ids = fields.One2many('account.move','tenament_move_id', string="Intercompany Moves")
    tenament_move_id = fields.Many2one('account.move', string="Intercompany Moves Ref")
    def action_post(self, inter_company = False):
        for lines in self.invoice_line_ids:
            # Block if account does not exist in the tenement company
            if lines.tenement_company_id and lines.tenement_company_id != self.company_id:
                gl_id = self.env['account.account'].search([
                                ('company_id', '=', lines.tenement_company_id.id),
                                ('code', '=', lines.account_id.code),
                            ])
                if not gl_id:
                    raise UserError(_("The Account %s belonging to the tenemant %s does not exist in %s") 
                    % (lines.account_id.code, lines.analytic_account_id.name, lines.tenement_company_id.name))

        res = super(AccountMove, self).action_post()
        if inter_company == False:
            self.inter_company_post() 
        return res  


    #=====================================================
    #Classs : Account Move
    #Method :get_main_account
    #=====================================================
    def  get_main_account(self, company_id):
         main_account = self.env['ia.inter.company.accounts'].search([('tenement_company_id','=',company_id)], limit =1)
         return main_account.main_account_id.id
    #=====================================================
    #Classs : Account Move
    #Method :get_tenement_account
    #=====================================================
    def  get_tenement_account(self, company_id):
        tenement_account = self.env['ia.inter.company.accounts'].search([('tenement_company_id','=',company_id)], limit =1)
        return tenement_account.tenement_account_id.id
    #=====================================================
    #Classs : Account Move
    #Method :get_other_company_account
    #=====================================================
    def  get_other_company_account(self, code, company_id):
        account = self.env['account.account'].sudo().search([('code','=', code),('company_id','=',company_id)], limit =1)
        return account.id
    #=====================================================
    #Classs : Account Move
    #Method :get_main_journal
    #=====================================================
    def  get_main_journal(self, company_id):
         main_journal = self.env['ia.inter.company.accounts'].search([('tenement_company_id','=',company_id)], limit =1)
         return main_journal.main_journal_id.id
    
    #=====================================================
    #Classs : Account Move
    #Method :get_tenement_account
    #=====================================================
    def  get_tenement_journal(self, company_id):
        tenement_journal = self.env['ia.inter.company.accounts'].search([('tenement_company_id','=',company_id)], limit =1)
        return tenement_journal.tenement_journal_id.id
    #=====================================================
    #Classs : Account Move
    #Method :inter_company_post
    #=====================================================
    def inter_company_post(self):       
        for move in self:
            tenement_company_id = False
            move_line_vals_list = []
            move_line_vals_list2 = []
            for inter_move_id in move.inter_move_ids:
                if inter_move_id.state == 'draft':
                    inter_move_id.button_cancel()
            for line in move.line_ids.filtered(lambda line: line.tenement_company_id  and line.analytic_account_id and line.tenement_company_id.id != move.company_id.id).sorted(lambda line: line.tenement_company_id.id):
                if tenement_company_id != line.tenement_company_id.id:                    
                    if move_line_vals_list:
                        move_vals['line_ids'] = [(0,0,vals_list) for vals_list in move_line_vals_list]
                        move_id = self.env['account.move'].create(move_vals)
                        move_id.action_post(inter_company = True)                        
                    if move_line_vals_list2:
                        move_vals2['line_ids'] = [(0,0,vals_list) for vals_list in move_line_vals_list2]
                        move_id = self.env['account.move'].create(move_vals2)
                        move_id.action_post(inter_company = True)
                    move_vals = {
                        'date': line.move_id.date,
                        'journal_id': self.get_main_journal(line.tenement_company_id.id),
                        'company_id' : line.company_id.id,
                        'move_type' : 'entry',
                        'ref':move.name,
                        'tenament_move_id':move.id,
                    }
                    move_vals2 = {
                        'date': line.move_id.date,
                        'journal_id': self.get_tenement_journal(line.tenement_company_id.id),
                        'company_id' : line.tenement_company_id.id,
                        'move_type' : 'entry',
                        'ref':move.name,
                        'tenament_move_id':move.id,
                    }
                    tenement_company_id = line.tenement_company_id.id
                    move_line_vals_list = []
                    move_line_vals_list2 = []

                #====================================================================================    
                move_line_vals = {                           
                    'account_id': line.account_id.id,
                    'name': move.name,
                    'tenement_company_id': line.tenement_company_id.id,
                    'analytic_group_id': line.analytic_group_id.id,
                    'activity_id': line.activity_id.id,
                    'tag_id': line.tag_id.id,  
                    'product_id': line.product_id.id, 
                    'analytic_account_id': line.analytic_account_id.id,                 
                }
                if line.credit > 0.0:
                    move_line_vals['credit'] = 0.0
                    move_line_vals['debit'] = line.credit
                else:
                    move_line_vals['credit'] = line.debit
                    move_line_vals['debit'] = 0.0
                

                move_line_vals2 = {                           
                    'account_id': self.get_main_account(line.tenement_company_id.id),
                    'name':move.name,
                    'partner_id': line.tenement_company_id.partner_id.id,   
                }                    
                if line.credit > 0.0:
                    move_line_vals2['credit'] = line.credit
                    move_line_vals2['debit'] = 0.0
                else:
                    move_line_vals2['credit'] = 0.0
                    move_line_vals2['debit'] = line.debit
                move_line_vals_list.append(move_line_vals)
                move_line_vals_list.append(move_line_vals2)
                    
                #===================================================================================
                #Inter company journal
                
                move_line_vals = {                           
                    'account_id':self.get_other_company_account(line.account_id.code, line.tenement_company_id.id),
                    'name':move.name,                    
                    'tenement_company_id': line.tenement_company_id.id,
                    'analytic_group_id': line.analytic_group_id.id,
                    'activity_id': line.activity_id.id,
                    'tag_id': line.tag_id.id, 
                    'product_id': line.product_id.id, 
                    'analytic_account_id': line.analytic_account_id.id,   
                }
                if line.credit > 0.0:
                    move_line_vals['credit'] = line.credit
                    move_line_vals['debit'] = 0.0
                else:
                    move_line_vals['credit'] = 0.0
                    move_line_vals['debit'] = line.debit
                move_line_vals2 = { 
                    'account_id':self.get_tenement_account(line.tenement_company_id.id),
                    'name':move.name,
                    'partner_id': move.company_id.partner_id.id                    
                    }
                if line.credit > 0.0:
                    move_line_vals2['credit'] = 0.0
                    move_line_vals2['debit'] = line.credit
                else:
                    move_line_vals2['credit'] = line.debit
                    move_line_vals2['debit'] = 0.0
                move_line_vals_list2.append(move_line_vals)
                move_line_vals_list2.append(move_line_vals2)
            #=============================================================================================
            #Final one post
            if move_line_vals_list:
                move_vals['line_ids'] = [(0,0,vals_list) for vals_list in move_line_vals_list]
                move_id = self.env['account.move'].create(move_vals)
                move_id.action_post(inter_company = True)
            if move_line_vals_list2:
                move_vals2['line_ids'] = [(0,0,vals_list) for vals_list in move_line_vals_list2]
                move_id = self.env['account.move'].create(move_vals2)
                move_id.action_post(inter_company = True)  

    #=====================================================
    #Classs : Account Move
    #Method :button_draft
    #=====================================================
    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for move in self:
            if move.tenament_move_id and self.env.context.get('from_form','') == 'yes':
                raise UserError(_("Cannot reset the entry  %s to draft since this is generated from %s belonging to  %s") % (move.name, move.tenament_move_id.name, move.company_id.name))
            for inter_move_id in move.inter_move_ids:
                inter_move_id.with_context(from_form='No').button_draft()
    #=====================================================
    #Classs : Account Move
    #Method :button_cancel
    #=====================================================
    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        for move in self:
            if move.tenament_move_id and self.env.context.get('from_form','') == 'yes':
                raise UserError(_("Cannot cancel the entry  %s to draft since this is generated from %s belonging to  %s") % (move.name, move.tenament_move_id.name, move.company_id.name))
            for inter_move_id in move.inter_move_ids:
                if inter_move_id.state != 'draft':
                    inter_move_id.with_context(from_form='No').button_draft()
                inter_move_id.with_context(from_form='No').button_cancel()