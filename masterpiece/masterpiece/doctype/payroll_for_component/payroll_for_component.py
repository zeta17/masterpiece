# -*- coding: utf-8 -*-
# Copyright (c) 2019, hendrik and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, dateutil
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import flt, nowdate

class PayrollforComponent(Document):
	def on_update(self):
		title = "Payroll for {0}".format(self.employee)
		self.db_set("title", title)

	def on_submit(self):
		self.update_receipt_componen("submit")
		self.update_other_payroll("submit")
		self.create_journal_entry()

	def update_receipt_componen(self, action):
		for row in self.details:
			if row.receipt_component:
				if action == "submit":
					if frappe.db.exists("Receipt Component", {"name":row.receipt_component, "is_paid":1}):
						frappe.throw(_("Detail no.<b>{0}</b> untuk Receipt Component <b>{1}</b> sudah dibayar").format(row.idx, row.receipt_component))
					else:
						rc = frappe.get_doc("Receipt Component", row.receipt_component)
						rc.is_paid = 1
						rc.status = "Paid"
						rc.flags.ignore_permissions = True
						rc.save()
				else:
					rc = frappe.get_doc("Receipt Component", row.receipt_component)
					rc.is_paid = 0
					rc.status = "Unpaid"
					rc.flags.ignore_permissions = True
					rc.save()

	def update_other_payroll(self, action):
		for row in self.others:
			if action == "submit":
				frappe.db.set_value("Payroll for Component", row.payroll_for_component, "is_paid_for_held", 1)
			else:
				frappe.db.set_value("Payroll for Component", row.payroll_for_component, "is_paid_for_held", 0)

	def create_journal_entry(self):
		je = frappe.new_doc("Journal Entry")
		je.company = self.company
		je.posting_date = self.posting_date
		if flt(self.total_held_others) > 0:
			je.append("accounts", {
				"account": self.payable_account,
				"party_type": "Employee",
				"party": self.employee,
				"debit_in_account_currency": self.total_held_others
			})
		je.append("accounts", {
			"account": "5210.005 - Biaya Gaji Lain Lain - MPC",
			"party_type": "Employee",
			"party": self.employee,
			"debit_in_account_currency": self.total
		})
		je.append("accounts", {
			"account": self.paid_from_account,
			"credit_in_account_currency": self.total_payment
		})
		if flt(self.held_amount) > 0:
			je.append("accounts", {
				"account": self.payable_account,
				"party_type": "Employee",
				"party": self.employee,
				"credit_in_account_currency": self.held_amount
			})
		je.payroll_for_component = self.name
		je.flags.ignore_permissions = True
		je.submit()

	def on_cancel(self):
		self.update_receipt_componen("cancel")
		self.update_other_payroll("cancel")
		self.cancel_journal_entry()

	def cancel_journal_entry(self):
		if frappe.db.exists("Journal Entry", {"payroll_for_component":self.name, "docstatus":1}):
			je = frappe.get_doc("Journal Entry", {"payroll_for_component":self.name, "docstatus":1})
			je.flags.ignore_permissions = True
			je.cancel()

@frappe.whitelist()
def get_receipt_component(employee, from_date, to_date):
	list = []
	count = frappe.db.sql("""select count(*) from `tabReceipt Component` where docstatus = '1' and is_paid = '0' and employee = '{0}' and posting_date between '{1}' and '{2}'""".format(employee, from_date, to_date))[0][0]
	if flt(count) != 0:
		for row in frappe.db.sql("""select * from `tabReceipt Component` where docstatus = '1' and is_paid = '0' and employee = '{0}' and posting_date between '{1}' and '{2}'""".format(employee, from_date, to_date), as_dict=1):
			list.append(frappe._dict({
				'posting_date': row.posting_date,
				'patrun_code': row.patrun_code,
				'item_code': row.item_code,
				'item_name': row.item_name,
				'received_qty': row.received_qty,
				'uom': row.uom,
				'rate': row.rate,
				'amount': row.amount,
				'receipt_component': row.name,
				'cost_component': row.cost_component
		    }))

	else:
		list.append(frappe._dict({
			'posting_date': None,
			'patrun_code': None,
			'item_code': None,
			'item_name': None,
			'received_qty': 0,
			'uom': None,
			'rate': 0,
			'amount': 0,
			'receipt_component': None
	    }))
		fromdate = dateutil.parser.parse(from_date).strftime("%d-%m-%Y")
		todate = dateutil.parser.parse(to_date).strftime("%d-%m-%Y")
		frappe.msgprint(_("Tidak ada transaksi untuk tukang potong <b>{0}</b> tanggal <b>{1}</b> sampai <b>{2}</b>").format(employee, fromdate, todate))

	return list

@frappe.whitelist()
def get_other_payroll(employee):
	list = []
	for row in frappe.get_all("Payroll for Component", filters={"employee":employee, "docstatus":1, "is_paid_for_held":0, "held_amount":[">", 0]}, fields=["*"]):
		list.append(frappe._dict({
			'payroll_for_component': row.name,
			'date': row.posting_date,
			'held_amount': row.held_amount
	    }))
	return list
