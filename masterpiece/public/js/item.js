frappe.ui.form.on('Item', {
  onload: function(frm) {
    frm.set_df_property("sb_barcodes", "hidden", 1);
    frm.set_df_property("inventory_section", "hidden", 1);
    frm.set_df_property("reorder_section", "hidden", 1);
    frm.set_df_property("serial_nos_and_batches", "hidden", 1);
    frm.set_df_property("variants_section", "hidden", 1);
    frm.set_df_property("purchase_details", "hidden", 1);
    frm.set_df_property("supplier_details", "hidden", 1);
    frm.set_df_property("foreign_trade_details", "hidden", 1);
    frm.set_df_property("sales_details", "hidden", 1);
    frm.set_df_property("deferred_revenue", "hidden", 1);
    frm.set_df_property("deferred_expense_section", "hidden", 1);
    frm.set_df_property("customer_details", "hidden", 1);
    frm.set_df_property("item_tax_section_break", "hidden", 1);
    frm.set_df_property("inspection_criteria", "hidden", 1);
    frm.set_df_property("manufacturing", "hidden", 1);
    frm.set_df_property("website_section", "hidden", 1);
    frm.set_df_property("sb72", "hidden", 1);
    frm.set_df_property("hub_publishing_sb", "hidden", 1);
  },
  refresh: function(frm) {
    // frm.set_df_property("sb_barcodes", "hidden", 1);
  },
})
