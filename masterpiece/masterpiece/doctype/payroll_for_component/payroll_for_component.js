// Copyright (c) 2019, hendrik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll for Component', {
  onload: function(frm) {
		frm.events.set_read_only(frm);
    frm.set_query("paid_from_account", function(doc) {
			return {
				filters: {
          is_group: 0,
          account_type: ["in", ["Cash", "Bank"]]
				}
			}
		})
  },
	refresh: function(frm) {

	},
  set_posting_time: function(frm){
		frm.events.set_read_only(frm);
	},
	set_read_only: function(frm){
		if(frm.doc.set_posting_time == 1){
			frm.set_df_property("posting_date", "read_only", false);
			frm.set_df_property("posting_time", "read_only", false);
		}else{
			frm.set_df_property("posting_date", "read_only", true);
			frm.set_df_property("posting_time", "read_only", true);
		}
	},
  employee: function(frm) {
    if(frm.doc.employee) {
      frm.events.get_receipt_component(frm);
    }
  },
  from_date: function(frm) {
    if(frm.doc.from_date) {
      frm.events.get_receipt_component(frm);
    }
  },
  to_date: function(frm) {
    if(frm.doc.to_date) {
      frm.events.get_receipt_component(frm);
    }
  },
  get_receipt_component: function(frm) {
    if(frm.doc.employee && frm.doc.from_date && frm.doc.to_date){
      frm.clear_table("details");
      frappe.call({
        method: "masterpiece.masterpiece.doctype.payroll_for_component.payroll_for_component.get_receipt_component",
        args: {
          employee: frm.doc.employee,
          from_date: frm.doc.from_date,
          to_date: frm.doc.to_date
        },
        callback: function(r, rt) {
          if(r.message) {
            $.each(r.message, function(i, d) {
              var c = frm.add_child("details");
              c.posting_date = d.posting_date;
              c.patrun_code = d.patrun_code;
              c.item_code = d.item_code;
              c.item_name = d.item_name;
              c.received_qty = d.received_qty;
              c.uom = d.uom;
              c.rate = d.rate;
              c.amount = d.amount;
              c.receipt_component = d.receipt_component;
              c.cost_component = d.cost_component;
            })
            calculate_total(frm);
            frm.refresh_fields();
          }
        }
      })
    }
  },
  get_other_payroll: function(frm) {
    frm.clear_table("others");
    frappe.call({
      method: "masterpiece.masterpiece.doctype.payroll_for_component.payroll_for_component.get_other_payroll",
      args: {
        employee: frm.doc.employee
      },
      callback: function(r, rt) {
        if(r.message) {
          $.each(r.message, function(i, d) {
            var c = frm.add_child("others");
            c.payroll_for_component = d.payroll_for_component;
            c.date = d.date;
            c.held_amount = d.held_amount;
          })
          calculate_total(frm);
          frm.refresh_fields();
        }
      }
    })
  },
  payment_percentage: function(frm) {
    calculate_total(frm);
  }
});

frappe.ui.form.on('Payroll for Component Detail', {
  details_remove: function(frm, cdt, cdn) {
		calculate_total(frm);
	},
})
frappe.ui.form.on('Payroll for Component Other', {
  others_remove: function(frm, cdt, cdn) {
		calculate_total(frm);
	},
})

var calculate_total = function(frm) {
  var total = frappe.utils.sum(
		(frm.doc.details || []).map(function(i) {
			return (flt(i.amount));
		})
	);
	frm.set_value("total", total);
  var total_held = frappe.utils.sum(
		(frm.doc.others || []).map(function(i) {
			return (flt(i.held_amount));
		})
	);
	frm.set_value("total_held_others", total_held);
  var total_pay = frappe.utils.sum(
		(frm.doc.details || []).map(function(i) {
			return (flt(i.amount) * (flt(frm.doc.payment_percentage) / 100));
		})
	) + (flt(frm.doc.total_held_others) * (flt(frm.doc.payment_percentage) / 100));
	frm.set_value("total_payment", total_pay);
  var held_amount = flt(total) + flt(total_held) - flt(total_pay);
	frm.set_value("held_amount", held_amount);
}
