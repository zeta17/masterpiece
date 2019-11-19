# -*- coding: utf-8 -*-
# Copyright (c) 2019, hendrik and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import flt

class Approval(Document):
	def on_submit(self):
		frappe.db.set_value(self.document_type, self.document_name, "approved_by", self.owner)
		self.db_set("document_name_ref", self.document_name)
		self.db_set("document_name", None)

	def on_cancel(self):
		check = frappe.db.get_value(self.document_type, self.document_name_ref, "docstatus")
		if check != 1:
			frappe.throw(_("{0} {1} sudah di cancel atau hapus").format(self.document_type, self.document_name_ref))
		else:
			frappe.db.set_value(self.document_type, self.document_name_ref, "approved_by", None)
