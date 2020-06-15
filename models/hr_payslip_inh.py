# -*- coding: utf-8 -*-
from openerp import models, fields, api 

class HrPayslipRunInh(models.Model):
    _inherit = 'hr.payslip.run'

    structure_id = fields.Many2one("hr.payroll.structure", "Estructura")


    @api.multi
    def close_payslip_run(self):
        res = super(HrPayslipRunInh, self).close_payslip_run()
        if self.slip_ids:
            concept_obj = self.env["hr.contract.concepts.deductions"].search([('id', '>', 0)])
            concept_array = []
            for concept in concept_obj:
                concept_array.append(concept.name)
            for payslip in self.slip_ids:
                historical_obj = self.env["hr.historial.contract"]
                allowances_obj = self.env["hr.contract.deduction.allowance"].search([('contract_id', '=', payslip.contract_id.id), ('state', '=', 'progress')])
                for allowance in allowances_obj:
                    if allowance.name.name in tuple(concept_array):
                        vals = {
                            'name': allowance.name.id,
                            'contract_id': payslip.contract_id.id,
                            'concept_type': allowance.concept_type,
                            'amount_fee': allowance.amount_fee,
                            'payment_date': self.date_end,
                        }
                        if allowance.periodicity == 'finita':
                            if (allowance.number_fee_pending -1 == 0):
                                allowance.write({'state': 'done' })
                            allowance.write({'number_fee_pending': allowance.number_fee_pending -1})
                            vals['number_fee'] = allowance.number_fee - allowance.number_fee_pending
                        else:
                            allowance.number_fee_record += 1
                            vals['number_fee'] = allowance.number_fee_record
                        record_id = historical_obj.create(vals)
        return res




