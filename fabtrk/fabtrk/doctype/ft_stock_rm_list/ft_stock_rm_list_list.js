
frappe.listview_settings['FT Stock RM List'] = {
    refresh: function(listview) {

        listview.page.add_inner_button('Export', function() {

            window.location.href =
                '/api/method/fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.export_with_value';

        });

    }
};
