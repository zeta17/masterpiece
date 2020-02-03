from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months, fmt_money
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

def submit_stock_entry(doc, method):
    pass
    # for row in doc.items:
    #     if row.production:
    #         received_qty = frappe.db.get_value("Production Item", row.production_item, "received_qty")
    #         qty_stock_entry = flt(row.qty) * flt(row.conversion_factor)
    #         new_received_qty = flt(received_qty) + qty_stock_entry
    #         frappe.db.set_value("Production Item", row.production_item, "received_qty", new_received_qty)
    #         production = frappe.get_doc("Production", row.production)
    #         production.flags.ignore_permissions = True
    #         production.save()

def cancel_stock_entry(doc, method):
    if doc.production:
        qty = 0
        for row in doc.items:
            if row.idx == 1:
                qty += flt(row.qty)
        production = frappe.get_doc("Production", doc.production)
        received_qty = flt(production.received_qty) - qty
        production.received_qty = received_qty
        production.flags.ignore_permissions = True
        production.save()
    # for row in doc.items:
    #     if row.production:
    #         received_qty = frappe.db.get_value("Production Item", row.production_item, "received_qty")
    #         qty_stock_entry = flt(row.qty) * flt(row.conversion_factor)
    #         new_received_qty = flt(received_qty) - qty_stock_entry
    #         frappe.db.set_value("Production Item", row.production_item, "received_qty", new_received_qty)
    #         production = frappe.get_doc("Production", row.production)
    #         production.flags.ignore_permissions = True
    #         production.save()

def submit_sales_invoice(doc, method):
    if doc.payment_method in ["Cash", "Transfer/EDC"]:
        account = frappe.db.get_value("Mode of Payment Account", {"parent":doc.mode_of_payment, "company":doc.company}, "default_account")
        if doc.is_return:
            outstanding_amount = flt(doc.outstanding_amount) * -1
            payment_type = "Pay"
            paid_from = account
            paid_to = doc.debit_to
        else:
            outstanding_amount = flt(doc.outstanding_amount)
            payment_type = "Receive"
            paid_from = doc.debit_to
            paid_to = account
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = payment_type
        pe.mode_of_payment = doc.mode_of_payment
        pe.party_type = "Customer"
        pe.posting_date = doc.posting_date
        pe.party = doc.customer
        pe.party_balance = doc.outstanding_amount
        pe.paid_from = paid_from
        pe.paid_from_account_currency = doc.currency
        pe.paid_to = paid_to
        pe.paid_to_account_currency = doc.currency
        pe.paid_amount = outstanding_amount
        pe.received_amount = outstanding_amount
        pe.append("references", {
            "reference_doctype": "Sales Invoice",
            "reference_name": doc.name,
            "due_date": doc.due_date,
            "total_amount": doc.outstanding_amount,
            "outstanding": doc.outstanding_amount,
            "allocated_amount": doc.outstanding_amount
        })
        pe.reference_no = "-"
        pe.reference_date = nowdate()
        pe.flags.ignore_permissions = True
        pe.submit()

        doc.db_set("status", "Paid")

def cancel_sales_invoice(doc, method):
    check_approval_cancel_si(doc)
    cancel_pe_from_si(doc)

def check_approval_cancel_si(doc):
    if str(doc.posting_date) != str(nowdate()):
        if not doc.approved_by:
            frappe.throw(_("Nota ini hanya bisa cancel dengan persetujuan dari atasan"))

def cancel_pe_from_si(doc):
    if doc.payment_method in ["Cash", "Transfer/EDC"]:
        if frappe.db.exists("Payment Entry Reference", {"reference_name":doc.name}):
            pe = frappe.db.get_value("Payment Entry Reference", {"reference_name":doc.name}, "parent")
            payment_entry = frappe.get_doc("Payment Entry", pe)
            payment_entry.flags.ignore_permissions = True
            payment_entry.cancel()

def submit_journal_entry(doc, method):
    for row in doc.accounts:
        if row.store_cash_flow:
            scf = frappe.get_doc("Store Cash Flow", row.store_cash_flow)
            accumulate_withdraw = frappe.db.get_value("Journal Entry Account", {"docstatus":1, "store_cash_flow":row.store_cash_flow, "parent":["!=", doc.name]}, "sum(credit_in_account_currency)") or 0
            total = flt(accumulate_withdraw) + flt(row.credit_in_account_currency)
            if flt(total) > flt(scf.net_total):
                frappe.throw(_("Total uang di baris {0} sudah melebihi {1} untuk Store Cash Flow no {2}").format(row.idx, fmt_money(scf.net_total, currency=row.account_currency), row.store_cash_flow))
