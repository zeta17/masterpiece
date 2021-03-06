frappe.listview_settings['Production'] = {
	get_indicator: function(doc) {
		var colors = {
			"Draft": "orange",
			"Submitted": "blue",
			"Partial Accepted": "purple",
			"Completed": "green",
      "Cancelled": "red"
		};
		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	}
};
