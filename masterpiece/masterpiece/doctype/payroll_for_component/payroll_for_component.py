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
		for row in self.details:
			if row.receipt_component:
				if frappe.db.exists("Receipt Component", {"name":row.receipt_component, "is_paid":1}):
					frappe.throw(_("Detail no.<b>{0}</b> untuk Receipt Component <b>{1}</b> sudah dibayar").format(row.idx, row.receipt_component))
				else:
					rc = frappe.get_doc("Receipt Component", row.receipt_component)
					rc.is_paid = 1
					rc.status = "Paid"
					rc.flags.ignore_permissions = True
					rc.save()

	def on_cancel(self):
		for row in self.details:
			if row.receipt_component:
				rc = frappe.get_doc("Receipt Component", row.receipt_component)
				rc.is_paid = 0
				rc.status = "Unpaid"
				rc.flags.ignore_permissions = True
				rc.save()

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
				'receipt_component': row.name
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
