# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "masterpiece"
app_title = "Masterpiece"
app_publisher = "hendrik"
app_description = "Masterpiece"
app_icon = "fa fa-pie-chart"
app_color = "blue"
app_email = "hendrik.zeta@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/masterpiece/css/masterpiece.css"
app_include_css = "/assets/masterpiece/css/custom.css"
# app_include_js = "/assets/masterpiece/js/timestamp.js"

# include js, css files in header of web template
# web_include_css = "/assets/masterpiece/css/masterpiece.css"
# web_include_js = "/assets/masterpiece/js/masterpiece.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Employee": "public/js/employee.js",
    "Item": "public/js/item.js",
    "Sales Invoice": "public/js/sales_invoice.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "masterpiece.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "masterpiece.install.before_install"
# after_install = "masterpiece.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "masterpiece.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Stock Entry": {
        "on_submit": "masterpiece.masterpiece.event.submit_stock_entry",
        "on_cancel": "masterpiece.masterpiece.event.cancel_stock_entry"
    },
    "Sales Invoice": {
        "on_submit": "masterpiece.masterpiece.event.submit_sales_invoice",
        "before_cancel": "masterpiece.masterpiece.event.cancel_sales_invoice"
    },
    "Journal Entry": {
        "on_submit": "masterpiece.masterpiece.event.submit_journal_entry"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"masterpiece.tasks.all"
# 	],
# 	"daily": [
# 		"masterpiece.tasks.daily"
# 	],
# 	"hourly": [
# 		"masterpiece.tasks.hourly"
# 	],
# 	"weekly": [
# 		"masterpiece.tasks.weekly"
# 	]
# 	"monthly": [
# 		"masterpiece.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "masterpiece.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "masterpiece.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "masterpiece.task.get_dashboard_data"
# }
