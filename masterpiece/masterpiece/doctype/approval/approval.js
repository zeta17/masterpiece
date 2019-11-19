// Copyright (c) 2019, hendrik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Approval', {
  onload: function(frm) {
    frm.set_query("document_name", function(doc) {
			return {
				filters: {
          docstatus: 1
				}
			}
		})
	},
  on_submit: function(frm) {
    frm.refresh_fields();
  },
  document_name: function(frm) {
    if(frm.doc.document_name) {
      frappe.call({
        method: "masterpiece.masterpiece.query.get_invoice_transaction",
        args: {
          document_type: frm.doc.document_type,
          document_name: frm.doc.document_name
        },
        callback: function(data) {
          frm.set_value("transaction", data.message);
        }
      });
    }else{
      frm.set_value("transaction", "-");
    }
  }
});
