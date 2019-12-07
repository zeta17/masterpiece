frappe.ui.form.on('Employee', {
  onload: function(frm) {
    frm.set_df_property("employee_number", "reqd", 0);
  }
})
