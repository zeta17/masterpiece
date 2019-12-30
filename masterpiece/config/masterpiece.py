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
					"name": _("Receipt Component"),
					"onboard": 1,
					"dependencies": ["Production"],
					"description": _("Receipt Component."),
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
					"name": _("Payroll for Component"),
					"onboard": 1,
					"dependencies": ["Production"],
					"description": _("Payroll for Component."),
				},
				{
					"type": "doctype",
					"name": _("Store Cash Flow"),
					"onboard": 1,
					"description": _("Store Cash Flow."),
				},
			]
		},
		{
			"label": _("Master"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": _("Kode Patrun"),
					"onboard": 1,
					"description": _("Kode Patrun."),
				},
				{
					"type": "doctype",
					"name": _("Cost Component"),
					"onboard": 1,
					"description": _("Cost Component."),
				},
				{
					"type": "doctype",
					"name": _("Tukang"),
					"onboard": 1,
					"description": _("Tukang."),
				}
			]
		},
	]
