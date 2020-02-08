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
		calculate_total(frm);
	},
	seri_n_patrun: function(frm) {
		if(frm.doc.seri_n_patrun) {
			var str = frm.doc.seri_n_patrun;
			var count = (str.match(/-/g) || []).length;
			if(flt(count) > 1 || flt(count) == 0) {
				msgprint("Salah format, yang benar misalnya: 1234-567");
			}else{
				var res = str.split("-");
				frappe.call({
		      method: "masterpiece.masterpiece.doctype.production.production.count_item",
		      args: {
						item: res[0]
		      },
		      callback: function(data) {
						if(data.message == "kosong") {
							frm.events.make_new_item(frm, res[0]);
						}else{
							frm.set_value("item_code", res[0])
						}
		      }
		    })
				frappe.call({
		      method: "masterpiece.masterpiece.doctype.production.production.count_patrun",
		      args: {
						patrun: res[1]
		      },
		      callback: function(data) {
						if(data.message == "kosong") {
							frm.events.make_new_patrun(frm, res[1]);
						}else{
							frm.set_value("patrun_code", res[1])
						}
		      }
		    })
			}
		}
	},
	make_new_item: function(frm, item) {
		var dialog = new frappe.ui.Dialog({
			title: __('New Seri'),
			fields: [
				{"fieldtype": "Data", "label": __("No Seri"), "fieldname": "item_code", "default":item, "reqd":1},
				{"fieldtype": "Data", "label": __("Item Name"), "fieldname": "item_name", "reqd":1},
				{"fieldtype": "Link", "label": __("Item Group"), "fieldname": "item_group", "options":"Item Group", "reqd":1, "get_query": function(){return {filters: [["is_group",'=',0]]};}},
				{"fieldtype": "Link", "label": __("UOM"), "fieldname": "uom", "options":"UOM", "reqd":1},
			]
		});
		dialog.set_primary_action(__('Submit'), function() {
			var args = dialog.get_values();
			if(!args) return;
			return cur_frm.call({
				method: "make_new_item",
				doc: cur_frm.doc,
				args: args,
				callback: function(r){
					if(r.exc){
						frappe.msgprint(__("There were errors."));
						return;
					}
					dialog.hide();
					frm.set_value("item_code", item);
					cur_frm.refresh();
				},
				btn: this
			})
		});
		dialog.show();
	},
	make_new_patrun: function(frm, patrun) {
		var dialog = new frappe.ui.Dialog({
			title: __('New Kode Patrun'),
			fields: [
				{"fieldtype": "Data", "label": __("Kode Patrun"), "fieldname": "kode_patrun", "default":patrun, "reqd":1},
			]
		});
		dialog.set_primary_action(__('Submit'), function() {
			var args = dialog.get_values();
			if(!args) return;
			return cur_frm.call({
				method: "make_new_patrun",
				doc: cur_frm.doc,
				args: args,
				callback: function(r){
					if(r.exc){
						frappe.msgprint(__("There were errors."));
						return;
					}
					dialog.hide();
					frm.set_value("patrun_code", patrun)
					cur_frm.refresh();
				},
				btn: this
			})
		});
		dialog.show();
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
	patrun_code: function(frm) {
		if(frm.doc.patrun_code) {
			frappe.call({
	      method: "frappe.client.get",
	      args: {
	        doctype: "Kode Patrun",
					name: frm.doc.patrun_code
	      },
	      callback: function(data) {
					frm.set_value("image1", data.message.image1);
	        frm.set_value("image2", data.message.image2);
					frm.set_value("image3", data.message.image3);
					frm.refresh_fields();
	      }
	    })
		}else{
			frm.set_value("image1", null);
			frm.set_value("image2", null);
			frm.set_value("image3", null);
			frm.refresh_fields();
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
  calculate_amount: function(frm, cdt, cdn) {
    var d = frappe.model.get_doc(cdt, cdn);
    d.amount = flt(d.qty) * flt(d.rate);
    frm.refresh_fields();
  },
	add_cost_component: function(frm) {
		var dialog = new frappe.ui.Dialog({
			title: __('Tambah Komponen Biaya'),
			fields: [
				{"fieldtype": "Link", "label": __("Jenis Pengerjaan"), "fieldname": "cost_component", "options":"Cost Component", "reqd":1},
				{"fieldtype": "Link", "label": __("Tukang"), "fieldname": "tukang", "options":"Tukang", "reqd":1},
				{"fieldtype": "Currency", "label": __("Harga"), "fieldname": "rate", "reqd":1},
			]
		});
		dialog.set_primary_action(__('Submit'), function() {
			var args = dialog.get_values();
			if(!args) return;
			return cur_frm.call({
				method: "add_expenses",
				doc: cur_frm.doc,
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
				{"fieldtype": "Link", "label": __("Jenis Pengerjaan"), "fieldname": "cost_component", "options":"Cost Component", "default":d.cost_component, "read_only":1},
				{"fieldtype": "Link", "label": __("Tukang"), "fieldname": "tukang", "options":"Tukang", "default":d.tukang, "read_only":1},
				{"fieldtype": "Column Break", "fieldname": "cb01"},
				{"fieldtype": "Date", "label": __("Tanggal Terima"), "fieldname": "receipt_date", "default":"Today", "reqd":1},
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
