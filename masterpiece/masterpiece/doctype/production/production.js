// Copyright (c) 2019, hendrik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production', {
	onload: function(frm) {
		frm.set_query("price_list", function(doc) {
			return {
				filters: {
          enabled: 1,
					selling: 1
				}
			}
		})
	},
	refresh: function(frm) {
    if(frm.doc.docstatus == 1 && in_list(["Submitted", "Partial Accepted"], frm.doc.status)) {
      frm.add_custom_button(__('Make Receipt'), frm.events.make_receipt);
    }
	},
  make_receipt: function(frm){
    frappe.model.open_mapped_doc({
  		method: "masterpiece.masterpiece.doctype.production.production.make_stock_receipt",
  		frm: cur_frm
  	})
  },
  patrun_code: function(frm) {
    if(frm.doc.patrun_code) {
      frappe.call({
        method: "masterpiece.masterpiece.doctype.production.production.get_item_from_patrun",
        args: {
          kode_patrun: frm.doc.patrun_code
        },
        callback: function(r, rt) {
          if(!r.exc) {
            if(r.message) {
              frm.clear_table("items");
              $.each(r.message, function(i, d) {
                var c = frm.add_child("items");
                c.item_code = d.item_code;
                c.item_name = d.item_name;
                c.stock_uom = d.stock_uom;
                c.uom = d.uom;
                c.qty = d.qty;
                c.conversion_factor = d.conversion_factor;
                c.rate = d.rate;
                c.amount = d.amount;
              })
              frm.refresh_fields();
              calculate_total(frm);
            }
          }
        }
      });
    }
  },
	price_list: function(frm) {
		if(frm.doc.price_list) {
			$.each(frm.doc.items || [], function(i, item) {
				frappe.call({
					method: "frappe.client.get",
					args: {
						doctype: "Item Price",
						filters: {
							"item_code": item.item_code,
							"price_list": frm.doc.price_list
						}
					},
					callback: function(data) {
						item.rate = data.message.price_list_rate;
						item.amount = flt(data.message.price_list_rate) * flt(item.qty);
						calculate_total(frm);
						frm.refresh_field("items");
					}
		    })
			})
		}
	},
  calculate_amount: function(frm, cdt, cdn) {
    var d = frappe.model.get_doc(cdt, cdn);
    d.amount = flt(d.qty) * flt(d.rate);
    frm.refresh_fields();
  },
});
frappe.ui.form.on('Production Item', {
  items_remove: function(frm, cdt, cdn) {
    calculate_total(frm);
  },
  item_code: function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if(d.item_code){
      frappe.call({
				method: "masterpiece.masterpiece.doctype.production.production.get_item_detail",
        args: {
          item_code: d.item_code,
					price_list: frm.doc.price_list || "-"
  			},
				callback: function(data) {
          frappe.model.set_value(cdt, cdn, data.message);
          calculate_total(frm);
				}
      })
    }else{
      frappe.model.set_value(cdt, cdn, "item_name", null);
      frappe.model.set_value(cdt, cdn, "stock_uom", null);
      frappe.model.set_value(cdt, cdn, "uom", null);
      frappe.model.set_value(cdt, cdn, "qty", null);
      frappe.model.set_value(cdt, cdn, "conversion_factor", null);
			frappe.model.set_value(cdt, cdn, "rate", null);
      frappe.model.set_value(cdt, cdn, "amount", null);
    }
  },
	qty: function(frm, cdt, cdn) {
    frm.events.calculate_amount(frm, cdt, cdn);
    calculate_total(frm);
	},
  rate: function(frm, cdt, cdn) {
    frm.events.calculate_amount(frm, cdt, cdn);
    calculate_total(frm);
	}
});
var calculate_total = function(frm) {
  var total = frappe.utils.sum(
		(frm.doc.items || []).map(function(i) {
			return (flt(i.amount));
		})
	);
  frm.set_value("total", total);
}
