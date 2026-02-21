frappe.listview_settings["FT Add Drawing"] = {
    formatters: {
        unit_weight(value) {
            if (value !== undefined && value !== null) {
                return Number(value).toFixed(3);
            }
            return value;
        },
        total_weight(value) {
            if (value !== undefined && value !== null) {
                return Number(value).toFixed(3);
            }
            return value;
        }
    }
};
