// Copyright (c) 2019, hendrik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Store Cash Flow', {
  onload: function(frm) {
    frm.events.account(frm);
    frm.events.initial_stock(frm);
    calculate_total(frm);
    frm.set_query("account", "expenses", function(doc, cdt, cdn) {
      var d = locals[cdt][cdn];
			return {
				filters: {
          disabled: 0,
					is_group: 0,
          root_type: "Expense",
          company: doc.company
				}
			}
		})
  },
  refresh: function(frm) {
    if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Buat Penarikan Uang"),  function() {
				frm.trigger('make_return_cash');
			});
		}
  },
  warehouse: function(frm) {
    frm.events.initial_stock(frm);
  },
  account: function(frm) {
    if(frm.doc.account) {
      frappe.call({
        method: "masterpiece.masterpiece.doctype.store_cash_flow.store_cash_flow.get_account_amount",
        args: {
          account: frm.doc.account,
          posting_date: frm.doc.posting_date
        },
        callback: function (data) {
          frm.set_value(data.message);
          frm.refresh_fields();
          calculate_total(frm);
        }
      })
    }
  },
  posting_date: function(frm) {
    frm.events.initial_stock(frm);
  },
  initial_stock: function(frm) {
    frappe.call({
			method: "masterpiece.masterpiece.doctype.store_cash_flow.store_cash_flow.get_initial_stock",
			args: {
				warehouse: frm.doc.warehouse,
				posting_date: frm.doc.posting_date
			},
			callback: function (data) {
				frm.set_value(data.message);
				frm.refresh_fields();
        calculate_total(frm);
			}
		})
  },
  make_return_cash: function(frm) {
		frappe.call({
			method: 'masterpiece.masterpiece.doctype.store_cash_flow.store_cash_flow.make_return_cash',
			args: {
        'document': frm.doc.name,
				'company': frm.doc.company,
        'account': frm.doc.account,
				'return_amount': frm.doc.net_total,
        'posting_date': frm.doc.posting_date
			},
			callback: function(r) {
				const doclist = frappe.model.sync(r.message);
				frappe.set_route('Form', doclist[0].doctype, doclist[0].name);
			}
		});
	},
});
frappe.ui.form.on('Store Cash Flow Expense', {
	expenses_add: function(frm, cdt, cdn) {
    calculate_total(frm);
	},
	expenses_remove: function(frm, cdt, cdn) {
		calculate_total(frm);
	},
	amount: function(frm, cdt, cdn) {
		calculate_total(frm);
	},
})
var calculate_total = function(frm) {
  var total_expenses = frappe.utils.sum(
		(frm.doc.expenses || []).map(function(i) {
			return (flt(i.amount));
		})
	);
	frm.set_value("total_expenses", total_expenses);
  var total = (flt(frm.doc.total_transaction) + flt(frm.doc.cash_amount)) - total_expenses;
  frm.set_value("net_total", total);
}
