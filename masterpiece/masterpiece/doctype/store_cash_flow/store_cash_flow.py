# -*- coding: utf-8 -*-
# Copyright (c) 2019, hendrik and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt

class StoreCashFlow(Document):
	def on_submit(self):
		if self.expenses:
			je = frappe.new_doc("Journal Entry")
			je.voucher_type = "Journal Entry"
			je.posting_date = self.posting_date
			je.company = self.company

			for row in self.expenses:
				je.append("accounts", {
					"account": row.account,
					"debit_in_account_currency": row.amount
				})
			je.append("accounts", {
				"account": self.account,
				"credit_in_account_currency": self.total_expenses
			})
			je.flags.ignore_permissions = True
			je.submit()

@frappe.whitelist()
def get_initial_stock(warehouse, posting_date):
	date_start = str(posting_date)+" 00:00:00"
	date_end = str(posting_date)+" 23:59:59"
	initial_stock = 0
	final_stock = 0
	for item in frappe.get_all("Item", filters={"is_stock_item":1}, fields=["*"]):
		count_start = frappe.db.sql("select count(*) from `tabStock Ledger Entry` where warehouse = %s and concat_ws(' ',posting_date,posting_time) <= '"+date_start+"' and item_code = %s", (warehouse, item.item_code))[0][0]
		if flt(count_start) >= 1:
			item_qty_start = frappe.db.sql("select qty_after_transaction from `tabStock Ledger Entry` where warehouse = %s and concat_ws(' ',posting_date,posting_time) <= '"+date_start+"' and item_code = %s order by concat_ws(' ',posting_date,posting_time) desc limit 1", (warehouse, item.item_code))[0][0]
		else:
			item_qty_start = 0
		count_end = frappe.db.sql("select count(*) from `tabStock Ledger Entry` where warehouse = %s and concat_ws(' ',posting_date,posting_time) <= '"+date_end+"' and item_code = %s", (warehouse, item.item_code))[0][0]
		if flt(count_end) >= 1:
			item_qty_end = frappe.db.sql("select qty_after_transaction from `tabStock Ledger Entry` where warehouse = %s and concat_ws(' ',posting_date,posting_time) <= '"+date_end+"' and item_code = %s order by concat_ws(' ',posting_date,posting_time) desc limit 1", (warehouse, item.item_code))[0][0]
		else:
			item_qty_end = 0
		price_list_rate = frappe.db.get_value("Item Price", {"price_list":"Standard Selling", "item_code":item.item_code}, "price_list_rate") or 0
		initial_stock += flt(item_qty_start) * flt(price_list_rate)
		final_stock += flt(item_qty_end) * flt(price_list_rate)

	sales_invoice = frappe.db.get_value("Sales Invoice", {"docstatus":1, "posting_date": posting_date, "mode_of_payment":"Cash Toko"}, "sum(grand_total)") or 0
	items = {
		'initial_stock': initial_stock,
		'final_stock': final_stock,
		'total_transaction': sales_invoice
	}
	return items
