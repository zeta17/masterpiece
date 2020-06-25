# -*- coding: utf-8 -*-
# Copyright (c) 2019, hendrik and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import flt, nowdate
from frappe.model.mapper import get_mapped_doc

class Production(Document):
	def on_update(self):
		self.set_title()
		self.set_seri()
		self.update_patrun()
		self.update_price_list()
		self.update_item()
		self.recalculate_rate()

	def set_title(self):
		title = self.seri_n_patrun if self.seri_n_patrun else self.item_code+"-"+self.patrun_code
		self.db_set("title", title)

	def set_seri(self):
		if self.seri_n_patrun:
			a, b = self.seri_n_patrun.split("-")
			if not self.item_code:
				self.db_set("item_code", a)
			if not self.patrun_code:
				self.db_set("patrun_code", b)

	def update_patrun(self):
		if self.image1:
			frappe.db.set_value("Kode Patrun", self.patrun_code, "image1", self.image1)
		if self.image2:
			frappe.db.set_value("Kode Patrun", self.patrun_code, "image2", self.image2)
		if self.image3:
			frappe.db.set_value("Kode Patrun", self.patrun_code, "image3", self.image3)

	def update_price_list(self):
		if flt(self.price_list_rate) > 0:
			if frappe.db.exists("Item Price", {"item_code":self.item_code, "price_list":"Standard Selling", "selling":1}):
				frappe.db.set_value("Item Price", {"item_code":self.item_code, "price_list":"Standard Selling", "selling":1}, "price_list_rate", self.price_list_rate)
			else:
				item_price = frappe.new_doc("Item Price")
				item_price.item_code = self.item_code
				item_price.item_name = self.item_name
				item_price.description = frappe.db.get_value("Item", self.item_code, "description")
				item_price.uom = self.uom
				item_price.price_list = "Standard Selling"
				item_price.price_list_rate = self.price_list_rate
				item_price.selling = 1
				item_price.flags.ignore_permissions = True
				item_price.save()

	def update_item(self):
		if self.default_image:
			if self.default_image == "Gambar 1":
				image = self.image1
			if self.default_image == "Gambar 2":
				image = self.image2
			if self.default_image == "Gambar 3":
				image = self.image3
			frappe.db.set_value("Item", self.item_code, "image", image)

	def recalculate_rate(self):
		total = 0
		cogs = 0
		for row in self.expenses:
			row.db_set("qty", self.qty)
			amount = flt(row.qty) * flt(row.rate)
			row.db_set("amount", amount)
			total += amount
			cogs += flt(row.rate)
		self.db_set("total_expenses", total)
		self.db_set("valuation_rate", cogs)

	def on_submit(self):
		if self.received_qty == self.qty:
			self.db_set("status", "Completed")
		else:
			if self.received_qty != 0:
				self.db_set("status", "Partial Accepted")
			else:
				self.db_set("status", "Submitted")
		self.update_patrun()
		self.update_price_list()
		self.update_item()

	def on_update_after_submit(self):
		if self.received_qty == self.qty:
			self.db_set("status", "Completed")
		else:
			if self.received_qty != 0:
				self.db_set("status", "Partial Accepted")
			else:
				self.db_set("status", "Submitted")
		self.update_patrun()
		self.update_price_list()
		self.update_item()

	def on_cancel(self):
		if self.status == "Submitted":
			self.db_set("status", "Cancelled")
		else:
			frappe.throw(_("Can not cancel {0} document").format(self.status))

	def make_new_item(self, item_code, item_name, item_group, uom):
		item = frappe.new_doc("Item")
		item.item_code = item_code
		item.item_name = item_name
		item.item_group = item_group
		item.stock_uom = uom
		item.flags.ignore_permissions = True
		item.save()
		return item.name

	def make_new_patrun(self, kode_patrun):
		patrun = frappe.new_doc("Kode Patrun")
		patrun.patrun_code = kode_patrun
		patrun.flags.ignore_permissions = True
		patrun.save()

	def make_receipt(self, warehouse, receipt_date, qty):
		sisa_qty = flt(self.qty) - flt(self.received_qty)
		if flt(sisa_qty) >= flt(qty):
			item = frappe.get_doc("Item", self.item_code)
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Receipt"
			se.set_posting_time = 1
			se.posting_date = receipt_date
			se.to_warehouse = warehouse
			se.production = self.name
			se.append("items", {
				"item_code": self.item_code,
				"item_name": self.item_name,
				"description": item.description,
				"item_group": item.item_group,
				"qty": qty,
				"basic_rate": flt(self.valuation_rate),
				"basic_amount": flt(self.valuation_rate) * flt(qty),
				"amount": flt(self.valuation_rate) * flt(qty),
				"valuation_rate": flt(self.valuation_rate),
				"uom": item.stock_uom,
				"conversion_factor": 1,
				"stock_uom": item.stock_uom
			})
			se.flags.ignore_permissions = True
			se.submit()

			received_qty = flt(self.received_qty) + flt(qty)
			self.db_set("received_qty", received_qty)

			self.save()

		else:
			frappe.throw(_("Sisa qty yang belum diterima adalah {0}").format(str(sisa_qty)[:-2]))

	def make_receipt_expense(self, receipt_date, cost_component, qty, production, item_code, production_detail, rate, tukang):
		pe = frappe.get_doc("Production Expense", production_detail)
		sisa_qty = flt(pe.qty) - flt(pe.received_qty)
		if sisa_qty >= flt(qty):
			prod = frappe.get_doc("Production", production)
			rc = frappe.new_doc("Receipt Component")
			rc.employee = tukang
			rc.item_code = item_code
			rc.item_name = frappe.db.get_value("Item", item_code, "item_name")
			rc.patrun_code = prod.patrun_code
			rc.posting_date = receipt_date
			rc.received_qty = qty
			rc.uom = prod.uom
			rc.rate = rate
			rc.amount = flt(qty) * flt(rate)
			rc.production = production
			rc.production_detail = production_detail
			rc.cost_component = cost_component
			rc.company = prod.company
			rc.flags.ignore_permissions = True
			rc.submit()

			received_qty = flt(pe.received_qty) + flt(qty)
			pe.received_qty = received_qty
			pe.flags.ignore_permissions = True
			pe.save()
		else:
			frappe.throw(_("Sisa qty yang belum diterima adalah {0}").format(str(sisa_qty)[:-2]))

	def add_expenses(self, cost_component, employee, rate):
		prod = frappe.get_doc("Production", self.name)
		amount = flt(self.qty) * flt(rate)
		total_expenses = flt(prod.total_expenses) + flt(amount)
		valuation_rate = flt(total_expenses) / flt(self.qty)
		prod.append("expenses", {
			"cost_component": cost_component,
			"employee": employee,
			"rate": rate,
			"qty": self.qty,
			"amount": amount
		})
		prod.total_expenses = total_expenses
		prod.valuation_rate = valuation_rate
		prod.flags.ignore_permissions = True
		prod.flags.ignore_validate_update_after_submit = True
		prod.save()

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
def count_item(item):
	if frappe.db.exists("Item", item):
		return "ada"
	else:
		return "kosong"

@frappe.whitelist()
def count_patrun(patrun):
	if frappe.db.exists("Kode Patrun", patrun):
		return "ada"
	else:
		return "kosong"
# @frappe.whitelist()
# def make_stock_receipt(source_name, target_doc=None):
# 	def set_missing_values(source, target):
# 		target.stock_entry_type = _("Material Receipt")
# 		target.to_warehouse = "Gudang Keamanan - MPC"
# 		target.run_method("set_missing_values")
#
# 	def update_item(source, target, source_parent):
# 		item = frappe.get_doc("Item", source.item_code)
# 		target.qty = (flt(source.qty) * flt(source.conversion_factor)) - flt(source.received_qty)
# 		target.item_group = item.item_group
# 		target.description = item.description
# 		target.basic_rate = 1
# 		target.amount = 1
#
# 	jv = get_mapped_doc("Production", source_name, {
# 		"Production": {
# 			"doctype": "Stock Entry",
#     		"field_map":{
#     			"posting_date": "posting_date"
#     		},
# 		},
# 		"Production Item": {
# 			"doctype": "Stock Entry Detail",
#     		"field_map":{
#     			"rate": "basic_rate",
# 				"parent": "production",
# 				"name": "production_item"
#     		},
# 			"postprocess": update_item,
# 			"condition": lambda doc: ((flt(doc.qty) * flt(doc.conversion_factor)) - flt(doc.received_qty)) >= 1
# 		},
# 	}, target_doc, set_missing_values)
# 	return jv
