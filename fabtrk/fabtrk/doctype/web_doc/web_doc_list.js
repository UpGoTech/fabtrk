frappe.listview_settings['Web Doc'] = {
    onload: function (listview) {
        listview.page.add_inner_button(__('Go to Web Page'), function () {
            window.location.href = '/event';
        });

        // Event Registration Button
        listview.page.add_inner_button(__('Event Registration'), function () {
            window.location.href = '/event_registration';
        });
    },
};
