from frappe import _


def get_dashboard_data(data):
	data = data or {}
	transactions = list(data.get("transactions") or [])
	transactions.append(
		{
			"label": _("Fabrication"),
			"items": ["Fabrication Drawing", "Fabrication Part"],
		}
	)
	data["transactions"] = transactions
	return data
