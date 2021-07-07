
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.date_utils import get_month, get_fiscal_year
from odoo.tools.misc import format_date

class IaChartAccountCreate(models.TransientModel):
    _name = 'ia.chart.account.create'
    _description = 'Create chart account for diffrent companies'  
    company_ids = fields.Many2many('res.company', string = 'Company')

    def create_account(self):
        account_ids = []
        for account in  self.env['account.account'].browse(self.env.context['active_ids']):            
            for company in self.company_ids:  
                acc_code = self.env['account.account'].search([('code','=', account.code),('company_id','=',company.id)]) 
                if acc_code:
                    raise UserError(_("The Account %s already exists in %s")% (account.code, company.name))
                account_id = self.env['account.account'].create({'code':account.code,'name':account.name,'user_type_id':account.user_type_id.id,'company_id':company.id}) 
                account_ids.append(account_id.id)
        return {
            'name': "Chart of Accounts",
            'type': 'ir.actions.act_window',          
            'view_mode': 'tree',
            'res_model': 'account.account',
            'view_id': self.env.ref('account.view_account_list').id,
            'target': 'current',
            'domain': [('id', 'in', account_ids)],
           
        }
  
        