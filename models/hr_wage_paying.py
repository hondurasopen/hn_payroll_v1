# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class HrPrePayroll(models.Model):
    _name = 'hr.wage.paying'


    name = fields.Text("Descripción")
    start_date = fields.Date("Fecha inicial")
    end_date = fields.Date("Fecha final")
    state = fields.Selection( [('draft', 'Borrador'), ('validated', 'Validada'),  ('done', 'Hecho')], string="Estado", default='draft')
    payroll_type = fields.Selection( [('bi-weekly', 'Quincenal'), ('monthly', 'Mensual')], string="Tipo", default='bi-weekly')
    employee_detail_ids = fields.One2many("hr.wage.paying.line", "parent_id", "Detalle de empleados")
    journal_id = fields.Many2one("account.journal", "Diarios")
    move_id = fields.Many2one("account.move", "Asiento", readonly=True)
    structure_id = fields.Many2one("hr.special.structure", "Estructura")

    gross_total = fields.Float("Salario Bruto", readonly=True)
    net_total = fields.Float("Neto salarios", readonly=True)
    total_isr = fields.Float("Total ISR", readonly=True)
    total_ipv = fields.Float("Total IPV", readonly=True)
    total_saving_fee = fields.Float("Total aportes cooperativa", readonly=True)
    total_loan = fields.Float("Total préstamos", readonly=True)
    total_other_deducction = fields.Float("Total otras deducciones", readonly=True)


    @api.multi
    def set_amounts(self):
        if self.employee_detail_ids:
            self.gross_total = 0
            self.net_total = 0
            self.total_loan = 0
            self.total_isr = 0
            self.total_ipv = 0
            self.total_saving_fee = 0
            self.total_other_deducction += l.other_deductions
            for l in self.employee_detail_ids:
                self.gross_total += l.gross_wage
                self.net_total += l.amount_net
                self.total_loan += l.loan_fee
                self.total_isr += l.amount_isr
                self.total_ipv += l.amount_ipv
                self.total_saving_fee += l.saving_fee
                self.total_other_deducction += l.other_deductions
            self.write({'state': 'validated'})


    @api.multi
    def create_journal_entrie(self):
        if self.employee_detail_ids:
            period_id = self.env["account.period"].with_context(self._context).find(self.end_date)[:1]
            obj_move = self.env["account.move"]
            lineas = []
            vals_debit = {
                'debit': 0.0,
                'credit': self.net_total,
                'amount_currency': 0.0,
                'name': 'Sueldos y Salarios',
                'account_id': self.journal_id.default_debit_account_id.id,
                'date': self.end_date,
            }
            vals_credit = {
                'debit': self.gross_total,
                'credit': 0.0,
                'amount_currency': 0.0,
                'name': 'Sueldos y Salarios',
                'account_id': self.journal_id.default_credit_account_id.id,
                'date': self.end_date,
            }
            lineas.append((0, 0, vals_debit))
            lineas.append((0, 0, vals_credit))
            vals = {
                'journal_id': self.journal_id.id,
                'date': self.end_date,
                'ref': 'Sueldos y Salarios',
                'period_id': period_id.id,
                'line_id': lineas,
            }
            id_move = obj_move.create(vals)
            if id_move :
                self.write({'state': 'done'})
                self.move_id = id_move.id
            self.write({'state': 'done'})

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



class HrPrePayrollLine(models.Model):
    _name = 'hr.wage.paying.line'

    @api.one
    @api.depends("gross_wage", "loan_fee", "saving_fee", "amount_isr", "amount_ipv", "other_incomes", "other_deductions")
    def _compute_amount(self):
    	self.gross_wage = self.wage + self.other_incomes 
    	self.amount_deduction = self.loan_fee + self.saving_fee + self.amount_isr + self.amount_ipv + self.other_deductions + self.amount_ihss
    	self.amount_net = self.gross_wage - self.amount_deduction

    parent_id = fields.Many2one("hr.wage.paying", "Pago")
    employee_id = fields.Many2one("hr.employee", "Empleado")
    wage = fields.Float("Salario")
    amount_ihss = fields.Float("IHSS")
    loan_fee = fields.Float("Cuota de préstamo")
    saving_fee = fields.Float("Aporte Cooperativa")
    amount_isr = fields.Float("ISR")
    amount_ipv = fields.Float("Impuesto Vecinal")
    other_deductions = fields.Float("Otra deducción")
    other_incomes = fields.Float("Otros ingresos")
    gross_wage = fields.Float("Salario bruto", compute='_compute_amount')
    amount_deduction = fields.Float("Total de deducciones", compute='_compute_amount')
    amount_net = fields.Float("Neto a pagar", compute='_compute_amount')

    