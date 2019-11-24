# -*- coding: utf-8 -*-
# Copyright (c) 2019, hendrik and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import flt, nowdate

class ReceiptComponent(Document):
	def on_submit(self):
		self.db_set("status", "Unpaid")

	def on_cancel(self):
		self.db_set("status", "Cancelled")
		pd = frappe.get_doc("Production Expense", self.production_detail)
		pd.received_qty = flt(pd.received_qty) - flt(self.received_qty)
		pd.flags.ignore_permissions = True
		pd.save()
