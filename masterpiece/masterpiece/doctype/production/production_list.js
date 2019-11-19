frappe.listview_settings['Production'] = {
	add_fields: ["status",	"company"],
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if(doc.status==="Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
    } else if(doc.status==="Draft") {
			return [__("Draft"), "orange", "status,=,Draft"];
    } else if(doc.status==="Partial Accepted") {
			return [__("Partial Accepted"), "purple", "status,=,Partial Accepted"];
    } else if(doc.status==="Completed") {
			return [__("Completed"), "green", "status,=,Completed"];
		}
	}
};
