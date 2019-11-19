from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months, fmt_money
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

def submit_stock_entry(doc, method):
    for row in doc.items:
        if row.production:
            received_qty = frappe.db.get_value("Production Item", row.production_item, "received_qty")
            qty_stock_entry = flt(row.qty) * flt(row.conversion_factor)
            new_received_qty = flt(received_qty) + qty_stock_entry
            frappe.db.set_value("Production Item", row.production_item, "received_qty", new_received_qty)
            production = frappe.get_doc("Production", row.production)
            production.flags.ignore_permissions = True
            production.save()

def cancel_stock_entry(doc, method):
    for row in doc.items:
        if row.production:
            received_qty = frappe.db.get_value("Production Item", row.production_item, "received_qty")
            qty_stock_entry = flt(row.qty) * flt(row.conversion_factor)
            new_received_qty = flt(received_qty) - qty_stock_entry
            frappe.db.set_value("Production Item", row.production_item, "received_qty", new_received_qty)
            production = frappe.get_doc("Production", row.production)
            production.flags.ignore_permissions = True
            production.save()

def submit_sales_invoice(doc, method):
    if doc.payment_method in ["Cash", "Transfer/EDC"]:
        account = frappe.db.get_value("Mode of Payment Account", {"parent":doc.mode_of_payment, "company":doc.company}, "default_account")
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.mode_of_payment = doc.mode_of_payment
        pe.party_type = "Customer"
        pe.party = doc.customer
        pe.party_balance = doc.outstanding_amount
        pe.paid_from = doc.debit_to
        pe.paid_from_account_currency = doc.currency
        pe.paid_to = account
        pe.paid_to_account_currency = doc.currency
        pe.paid_amount = doc.outstanding_amount
        pe.received_amount = doc.outstanding_amount
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
        pe = frappe.db.get_value("Payment Entry Reference", {"reference_name":doc.name}, "parent")
        payment_entry = frappe.get_doc("Payment Entry", pe)
        payment_entry.flags.ignore_permissions = True
        payment_entry.cancel()
