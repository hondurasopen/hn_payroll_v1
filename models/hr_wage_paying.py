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
    concept_ids = fields.One2many("hr.wage.paying.concept", "parent_id", "Conceptos")

    journal_id = fields.Many2one("account.journal", "Diarios")
    move_id = fields.Many2one("account.move", "Asiento", readonly=True)
    structure_id = fields.Many2one("hr.special.structure", "Estructura")

    gross_total = fields.Float("Salario Bruto", readonly=True)
    net_total = fields.Float("Neto salarios", readonly=True)
    total_isr = fields.Float("Impuesto sobe renta", readonly=True)
    total_ihss = fields.Float("Total IHSS", readonly=True)
    total_ipv = fields.Float("Impuesto vecinal", readonly=True)
    total_saving_fee = fields.Float("Aportes cooperativa", readonly=True)
    total_loan = fields.Float("Total préstamos", readonly=True)
    total_other_deducction = fields.Float("Total otras deducciones", readonly=True)


    @api.multi
    def back_to_draft(self):
        self.gross_total = 0
        self.net_total = 0
        self.total_loan = 0
        self.total_isr = 0
        self.total_ipv = 0
        self.total_ihss = 0
        self.total_saving_fee = 0
        self.total_other_deducction = 0
        self.concept_ids.unlink()
        self.write({'state': 'draft'})


    @api.multi
    def return_to_validated(self):
        self.move_id.state = 'draft'
        self.move_id.unlink()
        self.write({'state': 'validated'})


    @api.multi
    def set_amounts(self):
        if self.employee_detail_ids:
            for l in self.employee_detail_ids:
                self.gross_total += l.gross_wage
                self.net_total += l.amount_net
                self.total_loan += l.loan_fee
                self.total_isr += l.amount_isr
                self.total_ihss += l.amount_ihss
                self.total_ipv += l.amount_ipv
                self.total_saving_fee += l.saving_fee
                self.total_other_deducction += l.other_deductions            
            for concept in self.structure_id.concept_ids:
                concept_obj = self.env["hr.wage.paying.concept"]
                vals = {
                    'parent_id': self.id,
                    'concept_id': concept.id,
                }
                if concept.concept == 'basic':
                    vals['amount'] = self.gross_total
                if concept.concept == 'gross':
                    vals['amount'] = self.gross_total
                if concept.concept == 'net':
                    vals['amount'] = self.net_total
                if concept.concept == 'loan':
                    vals['amount'] = self.total_loan
                if concept.concept == 'saving_fee':
                    vals['amount'] = self.total_saving_fee
                if concept.concept == 'ihss':
                    vals['amount'] = self.total_ihss
                if concept.concept == 'isr':
                    vals['amount'] = self.total_isr
                if concept.concept == 'other_deductions':
                    vals['amount'] = self.total_other_deducction
                if concept.concept == 'ipv':
                    vals['amount'] = self.total_ipv
                concept_obj.create(vals)
            self.write({'state': 'validated'})


    @api.multi
    def create_journal_entrie(self):
        if self.concept_ids:
            period_id = self.env["account.period"].with_context(self._context).find(self.end_date)[:1]
            obj_move = self.env["account.move"]
            lineas = []
            vals_bank = {
                'debit': 0.0,
                'credit': self.net_total,
                'amount_currency': 0.0,
                'name': 'Sueldos y Salarios',
                'account_id': self.journal_id.default_debit_account_id.id,
                'date': self.end_date,
            }
            lineas.append((0, 0, vals_bank))
            for l in self.concept_ids:
                if l.concept_id.concept == 'gross' and self.gross_total > 0:
                    vals_gross_wage = {
                        'debit': self.gross_total,
                        'credit': 0.0,
                        'amount_currency': 0.0,
                        'name': 'Sueldos y Salarios',
                        'account_id': l.concept_id.account_id.id,
                        'date': self.end_date,
                    }
                    lineas.append((0, 0, vals_gross_wage))
                if l.concept_id.concept == 'loan' and self.total_loan > 0:
                    vals_loan = {
                        'debit': 0.0,
                        'credit': self.total_loan,
                        'amount_currency': 0.0,
                        'name': 'Deduccción de Préstamos por planilla',
                        'account_id': l.concept_id.account_id.id,
                        'date': self.end_date,
                    }
                    lineas.append((0, 0, vals_loan))
                if l.concept_id.concept == 'saving_fee' and self.total_saving_fee > 0:
                    vals_saving_fee = {
                        'debit': 0.0,
                        'credit': self.total_saving_fee,
                        'amount_currency': 0.0,
                        'name': 'Planilla aportes cooperativa',
                        'account_id': l.concept_id.account_id.id,
                        'date': self.end_date,
                    }
                    lineas.append((0, 0, vals_saving_fee))
                if l.concept_id.concept == 'ihss' and self.total_ihss > 0:
                    vals_ihss = {
                        'debit': 0.0,
                        'credit': self.total_ihss,
                        'amount_currency': 0.0,
                        'name': 'Planilla seguro social',
                        'account_id': l.concept_id.account_id.id,
                        'date': self.end_date,
                    }
                    lineas.append((0, 0, vals_ihss))
                if l.concept_id.concept == 'isr' and self.total_isr > 0:
                    vals_isr = {
                        'debit': 0.0,
                        'credit': self.total_isr,
                        'amount_currency': 0.0,
                        'name': 'Impuesto sobre la renta planilla',
                        'account_id': l.concept_id.account_id.id,
                        'date': self.end_date,
                    }
                    lineas.append((0, 0, vals_isr))
                if l.concept_id.concept == 'other_deductions' and self.total_other_deducction > 0:
                    vals_other_deductions = {
                        'debit': 0.0,
                        'credit': self.total_other_deducction,
                        'amount_currency': 0.0,
                        'name': 'Otras deducciones por planilla',
                        'account_id': l.concept_id.account_id.id,
                        'date': self.end_date,
                    }
                    lineas.append((0, 0, vals_other_deductions))
                if l.concept_id.concept == 'ipv' and self.total_ipv > 0:
                    vals_other_deductions = {
                        'debit': 0.0,
                        'credit': self.total_ipv,
                        'amount_currency': 0.0,
                        'name': 'Impuesto vecinal planilla',
                        'account_id': l.concept_id.account_id.id,
                        'date': self.end_date,
                    }
                    lineas.append((0, 0, vals_other_deductions))
            vals = {
                'journal_id': self.journal_id.id,
                'date': self.end_date,
                'ref': 'Sueldos y Salarios planilla',
                'period_id': period_id.id,
                'line_id': lineas,
            }
            id_move = obj_move.create(vals)
            if id_move :
                self.write({'state': 'done'})
                self.move_id = id_move.id
            self.crate_historial_employee()
            self.write({'state': 'done'})
        else:
            raise Warning(_('No existen parametros para generar planilla, revise estructura salarial'))


    @api.multi
    def crate_historial_employee(self):
        for employee in self.employee_detail_ids:
            contract_obj = self.env["hr.contract"].search([('employee_id', '=', employee.employee_id.id)], limit=1)
            if employee.amount_ihss > 0:
                concept_obj = self.env["hr.contract.concepts.deductions"].search([('concept', '=', 'ihss'), ('structure_id', '=', self.structure_id.id)], limit=1)
                self.create_historical(contract_obj.id, concept_obj.concept_type, employee.amount_ihss, concept_obj.id)
            if employee.loan_fee > 0:
                concept_obj = self.env["hr.contract.concepts.deductions"].search([('concept', '=', 'loan'), ('structure_id', '=', self.structure_id.id)], limit=1)
                self.create_historical(contract_obj.id, concept_obj.concept_type, employee.loan_fee, concept_obj.id)
            if employee.saving_fee > 0:
                concept_obj = self.env["hr.contract.concepts.deductions"].search([('concept', '=', 'saving_fee'), ('structure_id', '=', self.structure_id.id)], limit=1)
                self.create_historical(contract_obj.id, concept_obj.concept_type, employee.saving_fee, concept_obj.id)
            if employee.amount_isr > 0:
                concept_obj = self.env["hr.contract.concepts.deductions"].search([('concept', '=', 'isr'), ('structure_id', '=', self.structure_id.id)], limit=1)
                self.create_historical(contract_obj.id, concept_obj.concept_type, employee.amount_isr, concept_obj.id)
            if employee.amount_ipv > 0:
                concept_obj = self.env["hr.contract.concepts.deductions"].search([('concept', '=', 'ipv'), ('structure_id', '=', self.structure_id.id)], limit=1)
                self.create_historical(contract_obj.id, concept_obj.concept_type, employee.amount_ipv, concept_obj.id)
            if employee.other_deductions > 0:
                concept_obj = self.env["hr.contract.concepts.deductions"].search([('concept', '=', 'other_deductions'), ('structure_id', '=', self.structure_id.id)], limit=1)
                self.create_historical(contract_obj.id, concept_obj.concept_type, employee.other_deductions, concept_obj.id)

    @api.multi
    def create_historical(self, contract_id, concept_type, amount_fee, concept_id):
        historical_object = self.env["hr.historial.contract"]
        vals = {
            'name': concept_id,
            'contract_id':contract_id,
            'concept_type': concept_type,
            'amount_fee': amount_fee,
            'payment_date': self.end_date,
            'payroll_id': self.id,
        }
        id_histo = historical_object.create(vals)


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

    @api.multi
    def unlink(self):
        for payroll in self:
            if (payroll.state == 'validado' or payroll.state == 'done'):
                raise Warning(('No puede borrar este registro se encuentra en estado validado'))
        return super(HrPrePayroll, self).unlink()


class HrPrePayrollLine(models.Model):
    _name = 'hr.wage.paying.line'
    _rec_name = "employee_id"

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


class HrPreConcept(models.Model):
    _name = 'hr.wage.paying.concept'

    parent_id = fields.Many2one("hr.wage.paying", "Planilla")
    concept_id = fields.Many2one("hr.contract.concepts.deductions", "Concepto")
    amount = fields.Float("Total")