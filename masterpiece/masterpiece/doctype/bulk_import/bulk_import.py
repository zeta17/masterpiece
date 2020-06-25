# -*- coding: utf-8 -*-
# Copyright (c) 2020, hendrik and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import flt

class BulkImport(Document):
	def on_submit(self):
		prod = frappe.new_doc("Production")
		prod.posting_date = "2020-01-01"
		prod.seri_n_patrun = self.seri
		prod.qty = self.qty
		prod.received_qty = self.qty
		prod.uom = "PCS"
		prod.lebar_dada = self.ld
		prod.panjang = self.pj
		prod.price_list_rate = self.price_list
		if flt(self.potong) > 0:
			prod.append("expenses", {
				"cost_component": "Potong",
				"tukang": "Fung",
				"rate": self.potong,
				"qty": self.qty,
				"received_qty": self.qty
			})
		if flt(self.cmt) > 0:
			prod.append("expenses", {
				"cost_component": "CMT",
				"tukang": "Fung",
				"rate": self.cmt,
				"qty": self.qty,
				"received_qty": self.qty
			})
		if flt(self.wash) > 0:
			prod.append("expenses", {
				"cost_component": "Wash",
				"tukang": "Fung",
				"rate": self.wash,
				"qty": self.qty,
				"received_qty": self.qty
			})
		if flt(self.finishing) > 0:
			prod.append("expenses", {
				"cost_component": "Finishing",
				"tukang": "Fung",
				"rate": self.finishing,
				"qty": self.qty,
				"received_qty": self.qty
			})
		prod.flags.ignore_permissions = True
		prod.submit()
