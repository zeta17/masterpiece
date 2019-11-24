// Copyright (c) 2019, hendrik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production', {
	setup: function(frm) {
		frm.set_indicator_formatter('cost_component', function(doc) {
			let indicator = 'blue';
			if (doc.qty == doc.received_qty) {
				indicator = 'green';
			}
			if (doc.qty > doc.received_qty && doc.received_qty != 0) {
				indicator = 'purple';
			}
			return indicator;
		});
	},
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
			frm.add_custom_button(__('Buat Penerimaan Barang Jadi'),
        () => frm.events.make_receipt(frm));
    }
	},
  make_receipt: function(frm){
		var dialog = new frappe.ui.Dialog({
			title: __('Pemerimaan Barang'),
			fields: [
				{"fieldtype": "Date", "label": __("Tanggal Terima"), "fieldname": "receipt_date", "default":"Today", "reqd":1},
				{"fieldtype": "Link", "label": __("Terima digudang"), "fieldname": "warehouse", "options":"Warehouse", "reqd":1, "get_query": function(){return {filters: [["is_group",'=',0]]};}},
				{"fieldtype": "Float", "label": __("Qty"), "fieldname": "qty", "reqd":1, "default":flt(frm.doc.qty) - flt(frm.doc.received_qty)},
			]
		});
		dialog.set_primary_action(__('Submit'), function() {
			var args = dialog.get_values();
			if(!args) return;
			return cur_frm.call({
				method: "make_receipt",
				doc: cur_frm.doc,
				args: args,
				callback: function(r){
					if(r.exc){
						frappe.msgprint(__("There were errors."));
						return;
					}
					dialog.hide();
					cur_frm.refresh();
				},
				btn: this
			})
		});
		dialog.show();
  },
	item_code: function(frm) {
		if(frm.doc.item_code) {
			frappe.call({
	      method: "frappe.client.get",
	      args: {
	        doctype: "Item",
					name: frm.doc.item_code
	      },
	      callback: function(data) {
					frm.set_value("item_name", data.message.item_name);
	        frm.set_value("uom", data.message.stock_uom);
	      }
	    })
		}else{
			frm.set_value("item_name", null);
			frm.set_value("uom", null);
		}
	},
	qty: function(frm) {
		if(frm.doc.qty) {
			$.each(frm.doc.expenses, function(i, d) {
				d.qty = frm.doc.qty;
				d.amount = flt(frm.doc.qty) * flt(d.rate);
				refresh_field('qty', d.name, 'expenses');
				refresh_field('amount', d.name, 'expenses');
				calculate_total(frm);
			});
		}
	},
  // patrun_code: function(frm) {
  //   if(frm.doc.patrun_code) {
  //     frappe.call({
  //       method: "masterpiece.masterpiece.doctype.production.production.get_item_from_patrun",
  //       args: {
  //         kode_patrun: frm.doc.patrun_code
  //       },
  //       callback: function(r, rt) {
  //         if(!r.exc) {
  //           if(r.message) {
  //             frm.clear_table("items");
  //             $.each(r.message, function(i, d) {
  //               var c = frm.add_child("items");
  //               c.item_code = d.item_code;
  //               c.item_name = d.item_name;
  //               c.stock_uom = d.stock_uom;
  //               c.uom = d.uom;
  //               c.qty = d.qty;
  //               c.conversion_factor = d.conversion_factor;
  //               c.rate = d.rate;
  //               c.amount = d.amount;
  //             });
  //             frm.refresh_fields();
  //             calculate_total(frm);
  //           }
  //         }
  //       }
  //     });
  //   }
  // },
	// price_list: function(frm) {
	// 	if(frm.doc.price_list) {
	// 		$.each(frm.doc.items || [], function(i, item) {
	// 			frappe.call({
	// 				method: "frappe.client.get",
	// 				args: {
	// 					doctype: "Item Price",
	// 					filters: {
	// 						"item_code": item.item_code,
	// 						"price_list": frm.doc.price_list
	// 					}
	// 				},
	// 				callback: function(data) {
	// 					item.rate = data.message.price_list_rate;
	// 					item.amount = flt(data.message.price_list_rate) * flt(item.qty);
	// 					calculate_total(frm);
	// 					frm.refresh_field("items");
	// 				}
	// 	    })
	// 		})
	// 	}
	// },
  calculate_amount: function(frm, cdt, cdn) {
    var d = frappe.model.get_doc(cdt, cdn);
    d.amount = flt(d.qty) * flt(d.rate);
    frm.refresh_fields();
  },
});
frappe.ui.form.on('Production Expense', {
	expenses_add: function(frm, cdt, cdn) {
		frm.events.qty(frm);
	},
	expenses_remove: function(frm, cdt, cdn) {
		calculate_total(frm);
	},
	rate: function(frm, cdt, cdn) {
		frm.events.calculate_amount(frm, cdt, cdn);
		calculate_total(frm);
	},
	qty: function(frm, cdt, cdn) {
		frm.events.calculate_amount(frm, cdt, cdn);
		calculate_total(frm);
	},
	make_receipt_good: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var dialog = new frappe.ui.Dialog({
			title: __('Pemerimaan Jasa'),
			fields: [
				{"fieldtype": "Date", "label": __("Tanggal Terima"), "fieldname": "receipt_date", "default":"Today", "reqd":1},
				{"fieldtype": "Link", "label": __("Jenis Pengerjaan"), "fieldname": "cost_component", "options":"Cost Component", "default":d.cost_component, "read_only":1},
				{"fieldtype": "Float", "label": __("Qty"), "fieldname": "qty", "reqd":1, "default":flt(d.qty) - flt(d.received_qty)},
				{"fieldtype": "Link", "label": __("Production"), "fieldname": "production", "options":"Production", "default":frm.doc.name, "read_only":1, "hidden":1},
				{"fieldtype": "Link", "label": __("No Seri"), "fieldname": "item_code", "options":"Item", "default":frm.doc.item_code, "read_only":1, "hidden":1},
				{"fieldtype": "Data", "label": __("Production Detail"), "fieldname": "production_detail", "default":d.name, "read_only":1, "hidden":1},
				{"fieldtype": "Currency", "label": __("Harga"), "fieldname": "rate", "default":d.rate, "read_only":1, "hidden":1},
			]
		});
		dialog.set_primary_action(__('Submit'), function() {
			var args = dialog.get_values();
			if(!args) return;
			return frm.call({
				method: "make_receipt_expense",
				doc: frm.doc,
				args: args,
				callback: function(r){
					if(r.exc){
						frappe.msgprint(__("There were errors."));
						return;
					}
					dialog.hide();
					frm.refresh_fields();
					frm.reload_doc();
				},
				btn: this
			})
		});
		dialog.show();
	}
})
// frappe.ui.form.on('Production Item', {
//   items_remove: function(frm, cdt, cdn) {
//     calculate_total(frm);
//   },
//   item_code: function(frm, cdt, cdn) {
//     var d = locals[cdt][cdn];
//     if(d.item_code){
//       frappe.call({
// 				method: "masterpiece.masterpiece.doctype.production.production.get_item_detail",
//         args: {
//           item_code: d.item_code,
// 					price_list: frm.doc.price_list || "-"
//   			},
// 				callback: function(data) {
//           frappe.model.set_value(cdt, cdn, data.message);
//           calculate_total(frm);
// 				}
//       })
//     }else{
//       frappe.model.set_value(cdt, cdn, "item_name", null);
//       frappe.model.set_value(cdt, cdn, "stock_uom", null);
//       frappe.model.set_value(cdt, cdn, "uom", null);
//       frappe.model.set_value(cdt, cdn, "qty", null);
//       frappe.model.set_value(cdt, cdn, "conversion_factor", null);
// 			frappe.model.set_value(cdt, cdn, "rate", null);
//       frappe.model.set_value(cdt, cdn, "amount", null);
//     }
//   },
// 	qty: function(frm, cdt, cdn) {
//     frm.events.calculate_amount(frm, cdt, cdn);
//     calculate_total(frm);
// 	},
//   rate: function(frm, cdt, cdn) {
//     frm.events.calculate_amount(frm, cdt, cdn);
//     calculate_total(frm);
// 	}
// });
var calculate_total = function(frm) {
  var total = frappe.utils.sum(
		(frm.doc.expenses || []).map(function(i) {
			return (flt(i.amount));
		})
	);
	frm.set_value("total_expenses", total);
	var valuation_rate = frappe.utils.sum(
		(frm.doc.expenses || []).map(function(i) {
			return (flt(i.rate));
		})
	);
  frm.set_value("valuation_rate", valuation_rate);
}
