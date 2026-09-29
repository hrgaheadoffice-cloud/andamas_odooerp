from odoo import models,fields


class insertCaWizard(models.TransientModel):
    _name = 'insert.ca.wizard'

    ca_ids = fields.Many2many('cash.advance.ho')
    payment_plant_id = fields.Many2one('payment.plan')
    verdor_bill_ids = fields.Many2many('account.move')
    settlement_ids = fields.Many2many('settelment.ho')
    cash_request_ids = fields.Many2many('cash.request')
    reimbursement_ho_ids = fields.Many2many('reimbursement.ho')
    # noi_ho_ids = fields.Many2many('account.move','noi_move_id','noi_id','insert_doc_id')
    noi_ho_ids = fields.Many2many('noi')

    def insert_ca(self):
        for data in self:
            document_to_insert = []
            if data.ca_ids:
                for line in data.ca_ids:
                    document_to_insert.append((0,0,{'ca_id':line.id,'document_number':line.name,'document_type':'ca_ho',
                                              'amount':line.amount_ca,
                                              'create_document_date':line.create_date
                                              }))
                    # line.is_insert_plant = True
                    # line.state = 'waiting_on_payment'
            
            if data.verdor_bill_ids:
                for vb in data.verdor_bill_ids:
                    document_to_insert.append((0,0,{'vendor_bill_id':vb.id,
                                                    'document_number':vb.name,
                                                    'document_type':'vendor_bill',
                                                      'create_document_date':vb.create_date,
                                                      'amount':vb.amount_total,
                                                    
                                                    }))
            if data.noi_ho_ids:
                for noi in data.noi_ho_ids:
                    document_to_insert.append((0,0,{'noi_id':noi.id,
                                                    'document_number':noi.name,
                                                    'document_type':'noi_ho',
                                                    'amount':noi.request_amount,
                                                      'create_document_date':noi.create_date
                                                    
                                                    }))
                    # noi.is_insert_plant = True
                    # noi.noi_state_new = 'waiting_on_payment'

            if data.settlement_ids:
                for set in data.settlement_ids:
                    document_to_insert.append((0,0,{'settlement_id':set.id,
                                                    'document_number':set.name,
                                                    'document_type':'settlement_ho',
                                                    'amount':set.amount_settel,
                                                      'create_document_date':set.create_date
                                                    
                                                    }))
                    # set.is_insert_plant = True
                    # set.state = 'waiting_on_payment'

            if data.cash_request_ids:
                for ca in data.cash_request_ids:
                    document_to_insert.append((0,0,{'cash_request_id':ca.id,
                                                    'document_number':ca.name,
                                                    'document_type':'cash_request',
                                                    'amount':ca.request_amount,
                                                      'create_document_date':ca.create_date
                                                    
                                                    }))
                    # ca.is_insert_plant = True
                    # ca.state = 'waiting_on_payment'


            if data.reimbursement_ho_ids:
                for rei in data.reimbursement_ho_ids:
                    document_to_insert.append((0,0,{'reimbursement_id':rei.id,
                                                    'document_number':rei.name,
                                                    'document_type':'reimbursement_ho',
                                                    'amount':rei.request_amount,
                                                      'create_document_date':rei.create_date
                                                    
                                                    }))
                    # rei.is_insert_plant = True
                    # rei.state = 'waiting_on_payment'
                

            data.payment_plant_id.ca_payment_ids = document_to_insert

