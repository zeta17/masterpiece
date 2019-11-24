frappe.listview_settings['Receipt Component'] = {
	get_indicator: function(doc) {
		var colors = {
			"Draft": "orange",
			"Unpaid": "blue",
			"Paid": "green",
      "Cancelled": "red"
		};
		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	}
};
