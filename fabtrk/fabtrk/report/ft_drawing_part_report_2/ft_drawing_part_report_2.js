

frappe.query_reports["FT Drawing Part Report 2"] = {

	onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("item", []);
		frappe.query_report.set_filter_value("is_active", 1);

		setTimeout(() => {
			frappe.query_report.refresh();
		}, 100);
	},

	
	// filters: [
	// 	{
	// 		fieldname: "project_number",
	// 		label: "Project Number",
	// 		fieldtype: "MultiSelectList",
	// 		get_data: function (txt) {
	// 			return frappe.db.get_link_options("FT Project", txt);
	// 		}
	// 	},

	// 	// {
	// 	// 	fieldname: "drawing_number",
	// 	// 	label: "Drawing Number",
	// 	// 	fieldtype: "MultiSelectList",
	// 	// 	get_data: function (txt) {
	// 	// 		let projects = frappe.query_report.get_filter_value("project_number") || [];
	// 	// 		let filters = {};
	// 	// 		if (projects.length) {
	// 	// 			filters.project_number = ["in", projects];
	// 	// 		}
	// 	// 		return frappe.db.get_link_options("Add Drawing", txt, filters);
	// 	// 	}
	// 	// },
	// 	{
	// 		fieldname: "drawing_number",
	// 		label: "Drawing Number",
	// 		fieldtype: "MultiSelectList",
	// 		get_data: function (txt) {

	// 			let projects = frappe.query_report.get_filter_value("project_number");
	// 			let filters = {};

	// 			if (projects && projects.length > 0) {
	// 				filters.project_number = ["in", projects];
	// 			}

	// 			return frappe.call({
	// 				method: "frappe.client.get_list",
	// 				args: {
	// 					doctype: "Add Drawing",
	// 					filters: filters,
	// 					fields: ["name", "drawing_number"],
	// 					// limit_page_length: 500
	// 				}
	// 			}).then(r => {

	// 				let unique_map = {};
	// 				let result = [];

	// 				(r.message || []).forEach(d => {
	// 					if (!unique_map[d.drawing_number]) {
	// 						unique_map[d.drawing_number] = true;

	// 						result.push({
	// 							value: d.drawing_number,
	// 							label: d.drawing_number,       // sirf value show karega
	// 							description: ""                // undefined hatane ke liye
	// 						});
	// 					}
	// 				});

	// 				return result;
	// 			});
	// 		},
	// 		on_change() {
	// 			frappe.query_report.refresh();
	// 		}
	// 	},

	// 	{
	// 		fieldname: "item",
	// 		label: "Drawing Part",
	// 		fieldtype: "MultiSelectList",

	// 		get_data: function (txt) {
	// 			let projects = frappe.query_report.get_filter_value("project_number") || [];
	// 			let drawings = frappe.query_report.get_filter_value("drawing_number") || [];

	// 			// CASE 1: Nothing selected → show all items
	// 			if (!projects.length && !drawings.length) {
	// 				return frappe.call({
	// 					method: "frappe.client.get_list",
	// 					args: {
	// 						doctype: "FT Stock RM List",
	// 						fields: ["name", "computed_name"],
	// 						filters: [["computed_name", "like", "%" + txt + "%"]],
	// 					}
	// 				}).then(r => {
	// 					return (r.message || []).map(d => ({
	// 						value: d.name,
	// 						label: d.computed_name,
	// 						description: ""
	// 					}));
	// 				});
	// 			}

	// 			// CASE 2: Project selected but no drawing → show nothing
	// 			// if (projects.length && !drawings.length) {
	// 			// 	return [];
	// 			// }
	// 			// CASE 2: Project selected but no drawing → filter items by project
	// 			if (projects.length && !drawings.length) {
	// 				return frappe.call({
	// 					method: "frappe.client.get_list",
	// 					args: {
	// 						doctype: "Drawing Parts",
	// 						fields: ["item"],
	// 						filters: [["project_number", "in", projects]],
	// 					}
	// 				}).then(r => {

	// 					let unique_items = [...new Set((r.message || []).map(d => d.item))];
	// 					if (!unique_items.length) return [];

	// 					return frappe.call({
	// 						method: "frappe.client.get_list",
	// 						args: {
	// 							doctype: "FT Stock RM List",
	// 							fields: ["name", "computed_name"],
	// 							filters: [
	// 								["name", "in", unique_items],
	// 								["computed_name", "like", "%" + txt + "%"]
	// 							]
	// 						}
	// 					}).then(res => {
	// 						return (res.message || []).map(d => ({
	// 							value: d.name,
	// 							label: d.computed_name,
	// 							description: ""
	// 						}));
	// 					});
	// 				});
	// 			}


	// 			// CASE 3: Drawing selected → show only items of those drawings
	// 			return frappe.call({
	// 				method: "frappe.client.get_list",
	// 				args: {
	// 					doctype: "Drawing Parts",
	// 					fields: ["item"],
	// 					filters: [["drawing_number", "in", drawings]],
	// 				}
	// 			}).then(r => {
	// 				let unique_items = [...new Set((r.message || []).map(d => d.item))];
	// 				if (!unique_items.length) return [];

	// 				return frappe.call({
	// 					method: "frappe.client.get_list",
	// 					args: {
	// 						doctype: "FT Stock RM List",
	// 						fields: ["name", "computed_name"],
	// 						filters: [
	// 							["name", "in", unique_items],
	// 							["computed_name", "like", "%" + txt + "%"]
	// 						]
	// 					}
	// 				}).then(res => {
	// 					return (res.message || []).map(d => ({
	// 						value: d.name,
	// 						label: d.computed_name,
	// 						description: ""
	// 					}));
	// 				});
	// 			});
	// 		}

	// 	},

	// 	{
	// 		fieldname: "is_active",
	// 		label: "Is Active",
	// 		fieldtype: "Check",
	// 		default: 1
	// 	}
	// ],
	filters: [

		// ---------------- PROJECT ----------------
		{
			fieldname: "project_number",
			label: "Project Number",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options("FT Project", txt);
			},
			on_change() {
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.set_filter_value("item", []);
				frappe.query_report.refresh();
			}
		},

		// ---------------- DRAWING ----------------
		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {

				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let filters = {};

				if (projects.length) {
					filters.project_number = ["in", projects];
				}

				return frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Add Drawing",
						filters: filters,
						fields: ["name", "drawing_number"]
					}
				}).then(r => {

					let unique = {};
					let result = [];

					(r.message || []).forEach(d => {
						if (!unique[d.drawing_number]) {
							unique[d.drawing_number] = true;

							result.push({
								value: d.drawing_number,
								label: d.drawing_number,
								description: ""
							});
						}
					});

					return result;
				});
			},

			on_change() {
				frappe.query_report.set_filter_value("item", []);
				frappe.query_report.refresh();
			}
		},

		// ---------------- ITEM ----------------
		{
			fieldname: "item",
			label: "Drawing Part",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {

				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let drawings = frappe.query_report.get_filter_value("drawing_number") || [];

				// ---------------- CASE 1 ----------------
				// Nothing selected → show all items
				if (!projects.length && !drawings.length) {

					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Stock RM List",
							fields: ["name", "computed_name"],
							filters: [["computed_name", "like", "%" + txt + "%"]]
						}
					}).then(r => {
						return (r.message || []).map(d => ({
							value: d.name,
							label: d.computed_name,
							description: ""
						}));
					});
				}

				// ---------------- CASE 2 ----------------
				// Project selected but no drawing
				if (projects.length && !drawings.length) {

					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "Drawing Parts",
							fields: ["item"],
							filters: [["project_number", "in", projects]]
						}
					}).then(r => {

						let unique_items = [...new Set((r.message || []).map(d => d.item))];
						if (!unique_items.length) return [];

						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Stock RM List",
								fields: ["name", "computed_name"],
								filters: [
									["name", "in", unique_items],
									["computed_name", "like", "%" + txt + "%"]
								]
							}
						}).then(res => {
							return (res.message || []).map(d => ({
								value: d.name,
								label: d.computed_name,
								description: ""
							}));
						});

					});
				}

				// ---------------- CASE 3 ----------------
				// Drawing selected → PROPER FIX
				if (drawings.length) {

					// Step 1: Get Add Drawing document names
					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "Add Drawing",
							fields: ["name"],
							filters: [
								["drawing_number", "in", drawings]
							]
						}
					}).then(res => {

						let drawing_names = (res.message || []).map(d => d.name);
						if (!drawing_names.length) return [];

						// Step 2: Get items from Drawing Parts
						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "Drawing Parts",
								fields: ["item"],
								filters: [
									["drawing_number", "in", drawing_names]
								]
							}
						}).then(r => {

							let unique_items = [...new Set((r.message || []).map(d => d.item))];
							if (!unique_items.length) return [];

							return frappe.call({
								method: "frappe.client.get_list",
								args: {
									doctype: "FT Stock RM List",
									fields: ["name", "computed_name"],
									filters: [
										["name", "in", unique_items],
										["computed_name", "like", "%" + txt + "%"]
									]
								}
							}).then(res2 => {
								return (res2.message || []).map(d => ({
									value: d.name,
									label: d.computed_name,
									description: ""
								}));
							});

						});

					});
				}
			}
		},

		// ---------------- IS ACTIVE ----------------
		{
			fieldname: "is_active",
			label: "Is Active",
			fieldtype: "Check",
			default: 1,
			on_change() {
				frappe.query_report.refresh();
			}
		}

	],


	after_datatable_render(report) {

		$(report.wrapper)
			.off("click", ".view-btn")
			.on("click", ".view-btn", function () {

				let project = $(this).data("project");
				let item = $(this).data("item");

				if (!project || !item) {
					frappe.msgprint("No Data");
					return;
				}

				frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.get_item_details",
					args: {
						project: project,
						item: item
					},
					callback: function (r) {

						// if (!r.message || !r.message.length) {
						if (!r.message || !r.message.data || !r.message.data.length) {

							frappe.msgprint("No Details Found");
							return;
						}

						$("#item-detail-container").remove();

						let rows = "";
						let totalWeight = 0;

						// r.message.forEach(d => {
						r.message.data.forEach(d => {

							rows += `
								<tr>
									<td>${d.drawing_number}</td>
									<td>${d.quantity}</td>
									<td>${d.lenght}</td>
									<td>${d.width}</td>
									<td>${d.single_weight}</td>
									<td>${d.total_weight}</td>
								</tr>
							`;

							totalWeight += parseFloat(d.total_weight) || 0; // calculate total
						});

						let html = `
							<div id="item-detail-container"
								style="margin-top:20px; padding:20px; border:1px solid #ddd;">

								<div style="display:flex;justify-content:space-between;align-items:center;">
									<h4>Item Details - ${r.message.item_name}</h4>
									<button class="btn btn-xs btn-danger close-view">
										Close
									</button>
								</div>

								<table class="table table-bordered" style="margin-top:15px;">
									<tr>
										<th>Drawing</th>
										<th>Qty</th>
										<th>Length</th>
										<th>Width</th>
										<th>Single Weight</th>
										<th>Total Weight</th>
									</tr>
									${rows}
								</table>
							</div>
						`;

						$(report.wrapper).find(".datatable").after(html);

						$(".close-view").on("click", function () {
							$("#item-detail-container").remove();
						});

					}
				});
			});
	}
};

