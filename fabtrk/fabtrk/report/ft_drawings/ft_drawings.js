// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["FT Drawings"] = {

	onload(report) {
		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("po_serial_no", []);
		frappe.query_report.set_filter_value("is_active", 1);

		report.page.add_inner_button("Drawing Excel", function () {
			let filters = report.get_values();
			let url = "/api/method/fabtrk.fabtrk.report.ft_drawings.ft_drawings.download_drawing_excel"
				+ "?filters=" + encodeURIComponent(JSON.stringify(filters));
			window.location.href = url;
		});

		setTimeout(() => frappe.query_report.refresh(), 100);
	},

	// ✅ after_datatable_render — ft_drawing_part.js wala pattern follow kar raha hai
	after_datatable_render(report) {
		render_cards_from_api();
		attach_sticky_total_footer(report);   
	},

	filters: [

		// ---------- PROJECT ----------
		{
			fieldname: "project_number",
			label: "Project Number",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				let is_active = frappe.query_report.get_filter_value("is_active");
				let filters = {};
				if (is_active) filters.is_active = 1;
				return frappe.call({
					method: "frappe.client.get_list",
					args: { doctype: "FT Project", filters: filters, fields: ["name", "description"], limit: 0 }
				}).then(r => {
					let result = (r.message || []).map(d => ({
						value: d.name, label: d.name, description: d.description || ""
					}));
					if (txt) result = result.filter(i => i.label.toLowerCase().includes(txt.toLowerCase()));
					return result;
				});
			},
			on_change() {
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.set_filter_value("po_serial_no", []);
				frappe.query_report.refresh();
				setTimeout(() => frappe.query_report.refresh(), 100);
			}
		},

		// ---------- DRAWING ----------
		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				let projects = frappe.query_report.get_filter_value("project_number");
				return frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawings.ft_drawings.get_drawing_numbers",
					args: { project_number: JSON.stringify(projects || []), txt: txt || "" }
				}).then(r => r.message || []);
			},
			on_change() {
				frappe.query_report.set_filter_value("po_serial_no", []);
				frappe.query_report.refresh();
			}
		},

		// ---------- PO SERIAL NO ----------
		{
			fieldname: "po_serial_no",
			label: "PO Serial No",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				let projects = frappe.query_report.get_filter_value("project_number");
				let drawings = frappe.query_report.get_filter_value("drawing_number");
				return frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawings.ft_drawings.get_po_serial_numbers",
					args: {
						project_number: JSON.stringify(projects || []),
						drawing_number: JSON.stringify(drawings || []),
						txt: txt || ""
					}
				}).then(r => r.message || []);
			},
			on_change() { frappe.query_report.refresh(); }
		},

		// ---------- IS ACTIVE ----------
		{
			fieldname: "is_active",
			label: "Is Active",
			fieldtype: "Check",
			default: 1,
			on_change() {
				frappe.query_report.set_filter_value("project_number", []);
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.set_filter_value("po_serial_no", []);
				frappe.query_report.refresh();
			}
		}
	],

	formatter: function (value, row, column, data, default_formatter) {
		return default_formatter(value, row, column, data);
	}
};


// ------------------ STICKY TOTAL FOOTER 
function attach_sticky_total_footer(report) {
	// Pehle purana footer hata do
	$(report.wrapper).find("#ft-sticky-total-footer").remove();

	let $wrapper  = $(report.wrapper);
	let $dt_body  = $wrapper.find(".dt-scrollable");
	if (!$dt_body.length) return;

	// ── Data aur columns frappe se lo
	let data    = frappe.query_report.data    || [];
	let columns = frappe.query_report.columns || [];

	// ── FT Drawings ke columns ke totals
	// Sirf numeric columns ka total: unit_weight, quantity, total_weight
	let totals = {
		unit_weight:  0,
		quantity:     0,
		total_weight: 0,
	};

	data.forEach(function (d) {
		// TOTAL naam ki row already nahi hai (Python mein nahi daali)
		// Phir bhi safe raho
		if (d.project_name === "TOTAL") return;
		totals.unit_weight  += parseFloat(d.unit_weight  || 0);
		totals.quantity     += parseFloat(d.quantity      || 0);
		totals.total_weight += parseFloat(d.total_weight  || 0);
	});

	// ── Header cells se exact widths lo (ft_drawing_part.js wala same approach)
	let col_widths = [];
	$wrapper.find(".dt-header .dt-cell").each(function () {
		let w = $(this).outerWidth();
		col_widths.push(w > 0 ? w : 100);
	});

	if (!col_widths.length) return;

	// ── Format helper
	function fmt(num, dec) {
		dec = dec !== undefined ? dec : 3;
		return Number(num).toLocaleString("en-IN", {
			minimumFractionDigits: dec,
			maximumFractionDigits: dec
		});
	}

	// ── Serial number column (col index 0) — blank
	let cells_html = `
		<div style="
			width:${col_widths[0]}px;
			min-width:${col_widths[0]}px;
			max-width:${col_widths[0]}px;
			display:inline-flex;
			align-items:center;
			justify-content:center;
			padding:0 4px;
			border-right:1px solid #d1d8dd;
			flex-shrink:0;
			box-sizing:border-box;
			height:40px;
			background:#f3f3f3;
		"></div>`;

	// ── Data columns — columns array se iterate karo
	columns.forEach(function (col, i) {
		let w  = col_widths[i + 1] || 120;   // i+1 kyunki 0 serial number ka tha
		let fn = col.fieldname;
		let val = "";
		let align = "center";

		if (fn === "project_name") {
			// ✅ TOTAL label — left aligned, bold
			val   = `<span style="font-weight:900; font-size:13px; color:#000;">TOTAL</span>`;
			align = "left";

		} else if (fn === "unit_weight") {
			val = fmt(totals.unit_weight, 3);

		} else if (fn === "quantity") {
			val = fmt(totals.quantity, 0);

		} else if (fn === "total_weight") {
			val = fmt(totals.total_weight, 3);

		}
		// drawing_number, po_serial_no — blank rehenge

		let is_last    = (i === columns.length - 1);
		let border_right = is_last ? "none" : "1px solid #d1d8dd";

		cells_html += `
			<div style="
				width:${w}px;
				min-width:${w}px;
				max-width:${w}px;
				display:inline-flex;
				align-items:center;
				justify-content:${align === "left" ? "flex-start" : "center"};
				padding:0 8px;
				border-right:${border_right};
				flex-shrink:0;
				box-sizing:border-box;
				height:40px;
				font-weight:700;
				font-size:13px;
				color:#000;
				background:#f3f3f3;
				white-space:nowrap;
				overflow:hidden;
			">${val}</div>`;
	});

	// ── Footer DOM inject karo — dt-scrollable ke BAAD (ft_drawing_part.js wala same)
	let $footer = $(`
		<div id="ft-sticky-total-footer">
			<div id="ft-footer-inner" style="
				display: inline-flex;
				flex-wrap: nowrap;
				transform: translateX(0px);
				height: 40px;
			">${cells_html}</div>
		</div>
	`);

	$dt_body.after($footer);

	// ── Horizontal scroll sync — dt-scrollable scroll hone par footer bhi saath move kare
	$dt_body.off("scroll.ft_drawings_footer").on("scroll.ft_drawings_footer", function () {
		$("#ft-footer-inner").css("transform", `translateX(-${this.scrollLeft}px)`);
	});
}

// ------------------------ CARDS — Directly Doctype API se (table se bilkul alag)
function render_cards_from_api() {
	let filters = frappe.query_report.get_values() || {};

	frappe.call({
		method: "fabtrk.fabtrk.report.ft_drawings.ft_drawings.get_summary_cards",
		args: { filters: JSON.stringify(filters) },
		callback: function (r) {
			if (!r.message) return;
			render_cards_html(r.message);
		}
	});
}

function render_cards_html(data) {
	$(".ft-custom-summary-2").remove();

	function fmt(num) {
		return Number(num).toLocaleString("en-IN", {
			minimumFractionDigits: 3,
			maximumFractionDigits: 3
		});
	}

	let html = `
	<div class="ft-custom-summary-2">
		<div class="ft-card-2">
			<p class="ft-card-label-2">Total Projects</p>
			<span class="ft-card-value-2">${data.total_projects}</span>
			<p class="ft-card-label-2" style="margin-top:12px;">Total Weight as per Project (Kg)</p>
			<span class="ft-card-value-2">${fmt(data.project_total_weight)}</span>
		</div>
		<div class="ft-card-2">
			<p class="ft-card-label-2">Project Total No of Line Items</p>
			<span class="ft-card-value-2">${data.total_line_items}</span>
			<p class="ft-card-label-2" style="margin-top:12px;">Total Weight of Line Items Assign to Project (Kg)</p>
			<span class="ft-card-value-2">${fmt(data.total_weight_line_items)}</span>
		</div>
		<div class="ft-card-2">
			<p class="ft-card-label-2">Total No of Unique Drawings</p>
			<span class="ft-card-value-2">${data.total_drawings}</span>
		</div>
		<div class="ft-card-2">
			<p class="ft-card-label-2">Drawing Balance for Customer (Kg)</p>
			<span class="ft-card-value-2">${fmt(data.drawing_balance)}</span>
		</div>
	</div>`;

	$(".report-wrapper").prepend(html);
}

$(`<style>

/* ===== STICKY FOOTER — ft_drawing_part.js se same pattern ===== */
#ft-sticky-total-footer {
	position: sticky !important;
	bottom: 0 !important;
	z-index: 50 !important;
	background-color: #f3f3f3 !important;
	border-top: 3px solid #d1d8dd !important;
	width: 100% !important;
	display: flex !important;
	overflow: hidden !important;
	height: 40px !important;
}

#ft-sticky-total-footer > div {
	background-color: #f3f3f3 !important;
}

#ft-footer-inner {
	will-change: transform;
}


/* ===== CARDS ===== */
.ft-custom-summary-2 {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 20px;
	width: 100%;
	padding: 20px 0;
}
@media (max-width: 768px) {
	.ft-custom-summary-2 { grid-template-columns: repeat(1, 1fr) !important; }
	.datatable .dt-scrollable { overflow-x: auto !important; -webkit-overflow-scrolling: touch; }
}
.ft-card-2 {
	background: #fff;
	padding: 20px;
	border-radius: 10px;
	text-align: center;
	border: 2px solid #eef0f4;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	transition: box-shadow 0.2s ease;
}
.ft-card-label-2 { font-size: 13px; color: #6c757d; margin: 0 0 4px 0; text-align: center; width: 100%; }
.ft-card-value-2 { font-size: 18px; font-weight: 700; color: #1a1a2e; display: block; text-align: center; width: 100%; }


/* ===== TABLE ===== */
.report-wrapper, .datatable, .datatable-container { width: 100% !important; }
.datatable table { width: 100% !important; table-layout: auto !important; }
.datatable .dt-cell { white-space: nowrap !important; }
.datatable .dt-cell__content {
	text-align: center !important;
	justify-content: center !important;
	overflow: visible !important;
	text-overflow: unset !important;
}
.datatable .dt-row { width: 100% !important; }
.datatable .dt-scrollable { overflow-x: auto !important; }

</style>`).appendTo("head");







