frappe.ui.form.on('Sales Invoice', {
  onload: function(frm) {
    frm.trigger("reset_property");
    frm.set_query("mode_of_payment", function(doc) {
      if(frm.doc.payment_method == "Cash"){
        return {
  				filters: {
            enabled: 1,
            type: "Cash"
  				}
  			}
      }
      if(frm.doc.payment_method == "Transfer/EDC"){
        return {
  				filters: {
            enabled: 1,
            type: "Bank"
  				}
  			}
      }
		})
  },
  refresh: function(frm) {
    frm.toggle_reqd("mode_of_payment", in_list(["Cash", "Transfer/EDC"], frm.doc.payment_method));
  },
  reset_property: function(frm) {
    frm.toggle_reqd("customer", true);
    frm.set_value("update_stock", 1);
    frm.set_value("apply_discount_on", "Net Total");
    frm.set_df_property("update_stock", "read_only", 1);
    frm.set_df_property("apply_discount_on", "read_only", 1);
    frm.set_df_property("is_pos", "hidden", 1);
    frm.set_df_property("section_break_40", "hidden", 1);
    frm.set_df_property("taxes_section", "hidden", 1);
    frm.set_df_property("taxes", "hidden", 1);
    frm.set_df_property("section_break_43", "hidden", 1);
    frm.set_df_property("loyalty_points_redemption", "hidden", 1);
    frm.set_df_property("redeem_loyalty_points", "hidden", 1);
    frm.set_df_property("time_sheet_list", "hidden", 1);
    frm.set_df_property("timesheets", "hidden", 1);
    frm.set_df_property("total_billing_amount", "hidden", 1);
    frm.set_df_property("advances_section", "hidden", 1);
    frm.set_df_property("allocate_advances_automatically", "hidden", 1);
    frm.set_df_property("get_advances", "hidden", 1);
    frm.set_df_property("advances", "hidden", 1);
    frm.set_df_property("accounting_dimensions_section", "hidden", 1);
    frm.set_df_property("project", "hidden", 1);
    frm.set_df_property("cost_center", "hidden", 1);
    frm.set_df_property("scan_barcode", "hidden", 1);
    frm.set_df_property("payment_schedule_section", "hidden", 1);
    frm.set_df_property("payments_section", "hidden", 1);
    frm.set_df_property("column_break4", "hidden", 1);
    frm.set_df_property("terms_section_break", "hidden", 1);
    frm.set_df_property("edit_printing_settings", "hidden", 1);
    frm.set_df_property("sales_team_section_break", "hidden", 1);
    frm.set_df_property("section_break2", "hidden", 1);
    frm.set_df_property("subscription_section", "hidden", 1);
    frappe.meta.get_docfield("Sales Invoice Item", "barcode", frm.doc.name).hidden = 1;
    frappe.meta.get_docfield("Sales Invoice Item", "item_name", frm.doc.name).read_only = 1;
    frappe.meta.get_docfield("Sales Invoice Item", "drop_ship", frm.doc.name).hidden = 1;
    frappe.meta.get_docfield("Sales Invoice Item", "deferred_revenue", frm.doc.name).hidden = 1;
    frappe.meta.get_docfield("Sales Invoice Item", "section_break_18", frm.doc.name).hidden = 1;
    frappe.meta.get_docfield("Sales Invoice Item", "edit_references", frm.doc.name).hidden = 1;
    frappe.meta.get_docfield("Sales Invoice Item", "item_code", frm.doc.name).label = "Seri";
  },
  mode_of_payment: function(frm) {
    frm.toggle_reqd("mode_of_payment", in_list(["Cash", "Transfer/EDC"], frm.doc.payment_method));
  }
})
frappe.ui.form.on('Sales Invoice Item', {
  item_code: function(frm, cdt, cdn){
    var d = locals[cdt][cdn];
    if(d.item_code){
      frappe.call({
				method: "masterpiece.masterpiece.query.get_stock_warehouse",
				args:{
					item_code: d.item_code
				},
				callback: function (r) {
					if(r.message) {
            frappe.model.set_value(cdt, cdn, "stock_warehouse", r.message);
					}
				}
			})
    }else{
      frappe.model.set_value(cdt, cdn, "stock_warehouse", null);
    }
  }
})
