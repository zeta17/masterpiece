from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Document"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": _("Production"),
					"onboard": 1,
					"dependencies": ["Item"],
					"description": _("Production."),
				},
				{
					"type": "doctype",
					"name": _("Approval"),
					"onboard": 1,
					"dependencies": ["Sales Invoice"],
					"description": _("Approval."),
				},
				{
					"type": "doctype",
					"name": _("Kode Patrun"),
					"onboard": 1,
					"description": _("Kode Patrun."),
				},
			]
		},
	]
