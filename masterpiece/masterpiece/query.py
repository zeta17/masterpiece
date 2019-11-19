from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint
from frappe.utils import flt, fmt_money

@frappe.whitelist()
def get_stock_warehouse(item_code):
    tr = []
    uom = frappe.db.get_value("Item", item_code, "stock_uom")
    count = frappe.db.sql("""select count(*) from `tabProduction` p, `tabProduction Item` pi where p.`name` = pi.parent and p.`status` in ("Submitted", "Partial Accepted") and pi.item_code = %s""", item_code)[0][0]
    if flt(count) != 0:
        qty_production = frappe.db.sql("""select sum((pi.qty * pi.conversion_factor) - pi.received_qty) from `tabProduction` p, `tabProduction Item` pi where p.`name` = pi.parent and p.`status` in ("Submitted", "Partial Accepted") and pi.item_code =  %s""", item_code)[0][0]
    else:
        qty_production = 0
    td = "<tr><td>Produksi</td><td class='text-right'>{0}</td><td>{1}</td></tr>".format(qty_production, uom)
    tr.append(td)
    for wh in frappe.get_all("Warehouse", filters={"is_group":0, "disabled":0}, fields=["*"]):
        qty = frappe.db.get_value("Bin", {"warehouse":wh.name, "item_code":item_code}, "actual_qty") or 0
        td = "<tr><td>{0}</td><td class='text-right'>{1}</td><td>{2}</td></tr>".format(wh.name, qty, uom)
        tr.append(td)
    tr2 = "".join(tr)
    table = "<div class='tax-break-up' style='overflow-x: auto;'><table class='table table-bordered table-hover'><thead><tr><th class='text-left'>Warehouse</th><th class='text-right'>Stock Qty</th><th>UOM</th></tr></thead><tbody>"+tr2+"</tbody></table></div>"
    return table

@frappe.whitelist()
def get_invoice_transaction(document_type, document_name):
    tr = []
    invoice = frappe.get_doc(document_type, document_name)
    for row in frappe.get_all("Sales Invoice Item", filters={"parent":document_name}, fields=["*"]):
        td = "<tr><td>{0} : {1}</td><td class='text-right'>{2}</td><td>{3}</td><td class='text-right'>{4}</td><td class='text-right'>{5}</td></tr>".format(row.item_code, row.item_name, fmt_money(row.qty), row.uom, fmt_money(row.rate), fmt_money(row.amount))
        tr.append(td)
    td = "<tr><td colspan='4' class='text-right'>Total</td><td class='text-right'>{0}</td></tr>".format(fmt_money(invoice.total))
    tr.append(td)
    td = "<tr><td colspan='4' class='text-right'>Discount</td><td class='text-right'>{0}</td></tr>".format(fmt_money(invoice.discount_amount))
    tr.append(td)
    td = "<tr><td colspan='4' class='text-right'>Grand Total</td><td class='text-right'>{0}</td></tr>".format(fmt_money(invoice.grand_total))
    tr.append(td)
    tr2 = "".join(tr)
    table = "<span>Customer: {0}</span><br><div class='tax-break-up' style='overflow-x: auto;'><table class='table table-bordered table-hover'><thead><tr><th class='text-left'>Item</th><th class='text-right'>Qty</th><th>UOM</th><th class='text-right'>Harga</th><th class='text-right'>Jumlah</th></tr></thead><tbody>{1}</tbody></table></div>".format(invoice.customer, tr2)
    return table
