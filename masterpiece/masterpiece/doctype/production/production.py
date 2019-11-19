# -*- coding: utf-8 -*-
# Copyright (c) 2019, hendrik and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc

class Production(Document):
	def on_submit(self):
		self.db_set("status", "Submitted")

	def on_update_after_submit(self):
		count_item = frappe.db.get_value("Production Item", {"parent":self.name}, "count(*)")
		count_complete = 0
		count_receipt = 0
		for row in self.items:
			sisa = (flt(row.qty) * flt(row.conversion_factor)) - flt(row.received_qty)
			if sisa <= 0:
				count_complete += 1
			if flt(row.received_qty) >= 1:
				count_receipt += 1
		if count_item == count_complete:
			self.db_set("status", "Completed")
		else:
			if count_receipt != 0 and count_item != count_complete:
				self.db_set("status", "Partial Accepted")
			else:
				self.db_set("status", "Submitted")

	def on_cancel(self):
		if self.status == "Submitted":
			self.db_set("status", "Cancelled")
		else:
			frappe.throw(_("Can not cancel {0} document").format(self.status))

@frappe.whitelist()
def get_item_detail(item_code, price_list):
	item = frappe.get_doc("Item", item_code)
	if price_list != "-":
		rate = frappe.db.get_value("Item Price", {"item_code":item_code, "price_list":price_list}, "price_list_rate") or 0
	else:
		rate = 0
	items = {
		'item_name': item.item_name,
		'description': item.description,
		'stock_uom': item.stock_uom,
		'uom': item.stock_uom,
		'qty': 1,
		'conversion_factor': 1,
		'rate': rate
	}
	return items

@frappe.whitelist()
def get_item_from_patrun(kode_patrun):
	if frappe.db.exists("Production", {"patrun_code":kode_patrun, "docstatus":1}):
		items = []
		query = frappe.db.sql("""select distinct(pi.item_code) from `tabProduction Item` pi, `tabProduction` p where pi.parent = p.`name` and p.docstatus = '1' and p.patrun_code = %s order by pi.item_code asc""", kode_patrun, as_dict=1)
		for prod in query:
			i = frappe.get_doc("Item", prod.item_code)
			rate = frappe.db.sql("""select pi.rate from `tabProduction Item` pi, `tabProduction` p where pi.parent = p.`name` and p.docstatus = '1' and p.patrun_code = %s order by p.`name` asc limit 1""", kode_patrun)[0][0]
			items.append(frappe._dict({
				'item_code': prod.item_code,
				'item_name': i.item_name,
				'stock_uom': i.stock_uom,
				'uom': i.stock_uom,
				'qty': 1,
				'conversion_factor': 1,
				'rate': rate,
				'amount': rate
			}))
		return items


@frappe.whitelist()
def make_stock_receipt(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.stock_entry_type = _("Material Receipt")
		target.to_warehouse = "Gudang Keamanan - MPC"
		target.run_method("set_missing_values")

	def update_item(source, target, source_parent):
		item = frappe.get_doc("Item", source.item_code)
		target.qty = (flt(source.qty) * flt(source.conversion_factor)) - flt(source.received_qty)
		target.item_group = item.item_group
		target.description = item.description
		target.basic_rate = 1
		target.amount = 1

	jv = get_mapped_doc("Production", source_name, {
		"Production": {
			"doctype": "Stock Entry",
    		"field_map":{
    			"posting_date": "posting_date"
    		},
		},
		"Production Item": {
			"doctype": "Stock Entry Detail",
    		"field_map":{
    			"rate": "basic_rate",
				"parent": "production",
				"name": "production_item"
    		},
			"postprocess": update_item,
			"condition": lambda doc: ((flt(doc.qty) * flt(doc.conversion_factor)) - flt(doc.received_qty)) >= 1
		},
	}, target_doc, set_missing_values)
	return jv
