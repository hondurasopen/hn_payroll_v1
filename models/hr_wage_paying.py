# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class HrPrePayroll(models.Model):
    _name = 'hr.wage.paying'

    start_date = fields.Date("Fecha inicial")
    end_date = fields.Date("Fecha final")
    name = fields.Text("Descripción")
    state = fields.Selection( [('draft', 'Borrador'), ('done', 'Hecho')], string="Estado", default='draft')
    payroll_type = fields.Selection( [('bi-weekly', 'Quincenal'), ('monthly', 'Mensual')], string="Tipo", default='bi-weekly')
    employee_detail_ids = fields.One2many("hr.wage.paying.line", "parent_id", "Detalle de empleados")

    @api.multi
    def get_employee(self):
    	if self.start_date > self.end_date:
            raise Warning(_('La fecha de inicio es mayor fecha final'))
        employee_obj = self.env["hr.employee"].search([('active','=', True)])
        for l in employee_obj:
        	line_obj = self.env["hr.wage.paying.line"]
        	vals = {
        		'employee_id': l.id,
        	}
        	contract_obj = self.env["hr.contract"].search([('employee_id', '=', l.id)], limit=1)
        	if self.payroll_type == 'bi-weekly':
        		vals["wage"] = contract_obj.wage / 2
        	if self.payroll_type == 'monthly':
        		vals["wage"] = contract_obj.wage

        	line_obj.create(vals)





class HrPrePayroll(models.Model):
    _name = 'hr.wage.paying.line'

    parent_id = fields.Many2one("hr.wage.paying", "Pago")
    employee_id = fields.Many2one("hr.employee", "empleado")
    wage = fields.Float("Salario")
    gross_wage = fields.Float("Salario bruto")
    loan_fee = fields.Float("Cuota de préstamo")
    saving_fee = fields.Float("Aporte Cooperativa")
    amount_isr = fields.Float("ISR")
    amount_ipv = fields.Float("Impuesto Vecinal")
    another_deduction = fields.Float("Otra deducción")
    another_incomes = fields.Float("Otros ingresos")
    amount_deduction = fields.Float("Total de deducciones")
    amount_net = fields.Float("Neto a pagar")
