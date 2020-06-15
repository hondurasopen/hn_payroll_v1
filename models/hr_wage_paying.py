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
        if self.employee_detail_ids:
        	self.employee_detail_ids.unlink()
        employee_obj = self.env["hr.employee"].search([('active','=', True)])
        for l in employee_obj:
        	line_obj = self.env["hr.wage.paying.line"]
        	vals = {
        		'employee_id': l.id,
        		'parent_id': self.id,
        	}
        	contract_obj = self.env["hr.contract"].search([('employee_id', '=', l.id)], limit=1)
        	if self.payroll_type == 'bi-weekly':
        		vals["wage"] = contract_obj.wage / 2
        	if self.payroll_type == 'monthly':
        		vals["wage"] = contract_obj.wage

        	line_obj.create(vals)


class HrPrePayroll(models.Model):
    _name = 'hr.wage.paying.line'

    @api.one
    @api.depends("gross_wage", "loan_fee", "saving_fee", "amount_isr", "amount_ipv", "other_incomes", "other_deductions")
    def _compute_amount(self):
    	self.gross_wage = self.wage + self.other_incomes 
    	self.amount_deduction = self.loan_fee + self.saving_fee + self.amount_isr + self.amount_ipv + self.other_deduction
    	self.amount_net = self.gross_wage - self.amount_deduction

    parent_id = fields.Many2one("hr.wage.paying", "Pago")
    employee_id = fields.Many2one("hr.employee", "Empleado")
    wage = fields.Float("Salario")
    loan_fee = fields.Float("Cuota de préstamo")
    saving_fee = fields.Float("Aporte Cooperativa")
    amount_isr = fields.Float("ISR")
    amount_ipv = fields.Float("Impuesto Vecinal")
    other_deductions = fields.Float("Otra deducción")
    other_incomes = fields.Float("Otros ingresos")
    gross_wage = fields.Float("Salario bruto", compute='_compute_amount')
    amount_deduction = fields.Float("Total de deducciones", compute='_compute_amount')
    amount_net = fields.Float("Neto a pagar", compute='_compute_amount')

    

