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
    },
    onload(listview) {

        let btn = listview.page.add_inner_button("Export", function() {
            window.open("/app/data-export/new-data-export?reference_doctype=FT Add Drawing");
        });

        btn.removeClass("btn-default");
        btn.addClass("no-hover-export-btn");
    }
    
};
$("<style>")
    .prop("type", "text/css")
    .html(`
        .no-hover-export-btn,
        .no-hover-export-btn:hover,
        .no-hover-export-btn:focus,
        .no-hover-export-btn:active {
            background-color: #000 !important;
            color: #fff !important;
            border: none !important;
            box-shadow: none !important;
            transform: none !important;
            padding: 10px 15px !important;
            font-size: 14px !important;
            cursor: pointer !important;
        }
    `)
    .appendTo("head");