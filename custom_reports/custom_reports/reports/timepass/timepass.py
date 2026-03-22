import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    
    query = """

        SELECT
            *,
            COALESCE(so_transaction_date, si_posting_date, dn_posting_date) AS posting_date,
            -- si_posting_date check
            CASE 
                WHEN si_posting_date < %(from_date)s THEN 'Before Range'
                WHEN si_posting_date > %(to_date)s THEN 'After Range'
                WHEN si_posting_date IS NULL THEN 'No Invoice Date'
                ELSE 'In Range'
            END AS si_date_status,

            -- dn_posting_date check
            CASE 
                WHEN dn_posting_date < %(from_date)s THEN 'Before Range'
                WHEN dn_posting_date > %(to_date)s THEN 'After Range'
                WHEN dn_posting_date IS NULL THEN 'No DN Date'
                ELSE 'In Range'
            END AS dn_date_status

        FROM (
        SELECT
            -- Sales Order Item Fields
            soi.name AS soi_item,
            soi.item_code AS soi_item_code,
            soi.is_stock_item AS soi_is_stock_item,
            soi.item_group AS soi_item_group,
            soi.brand AS soi_brand,
            soi.qty AS soi_qty,
            soi.stock_uom AS soi_stock_uom,
            soi.uom AS soi_uom,
            soi.conversion_factor AS soi_conversion_factor,
            soi.stock_qty AS soi_stock_qty,
            soi.rate AS soi_rate,
            soi.amount AS soi_amount,
            soi.net_rate AS soi_net_rate,
            soi.net_amount AS soi_net_amount,
            soi.base_net_rate AS soi_base_net_rate,
            soi.base_net_amount AS soi_base_net_amount,

            -- Sales Order Fields
            so.name AS so_name,
            so.customer AS so_customer,
            so.customer_name AS so_customer_name,
            so.order_type AS so_order_type,
            so.transaction_date AS so_transaction_date,
            so.company AS so_company,
            so.cost_center AS so_cost_center,
            so.currency AS so_currency,
            so.set_warehouse AS so_set_warehouse,
            so.total_qty AS so_total_qty,
            so.total_net_weight AS so_total_net_weight,
            so.base_total AS so_base_total,
            so.base_net_total AS so_base_net_total,
            so.total AS so_total,
            so.net_total AS so_net_total,
            so.total_taxes_and_charges AS so_total_taxes_and_charges,
            so.base_grand_total AS so_base_grand_total,
            so.grand_total AS so_grand_total,
            so.status AS so_status,
            so.delivery_status AS so_delivery_status,
            so.billing_status AS so_billing_status,

            -- Sales Invoice Fields
            si.name AS si_name,
            si.customer AS si_customer,
            si.customer_name AS si_customer_name,
            si.company AS si_company,
            si.posting_date AS si_posting_date,
            si.pos_profile AS si_pos_profile,
            si.is_return AS si_is_return,
            si.return_against AS si_return_against,
            si.is_debit_note AS si_is_debit_note,
            si.cost_center AS si_cost_center,
            si.currency AS si_currency,
            si.update_stock AS si_update_stock,
            si.set_warehouse AS si_set_warehouse,
            si.set_target_warehouse AS si_set_target_warehouse,
            si.total_qty AS si_total_qty,
            si.total_net_weight AS si_total_net_weight,
            si.base_total AS si_base_total,
            si.base_net_total AS si_base_net_total,
            si.total AS si_total,
            si.net_total AS si_net_total,
            si.total_taxes_and_charges AS si_total_taxes_and_charges,
            si.base_grand_total AS si_base_grand_total,
            si.grand_total AS si_grand_total,
            si.status AS si_status,

            -- Sales Invoice Item Fields
            sii.name AS sii_item,
            sii.item_code AS sii_item_code,
            sii.item_group AS sii_item_group,
            sii.brand AS sii_brand,
            sii.qty AS sii_qty,
            sii.stock_uom AS sii_stock_uom,
            sii.uom AS sii_uom,
            sii.conversion_factor AS sii_conversion_factor,
            sii.stock_qty AS sii_stock_qty,
            sii.rate AS sii_rate,
            sii.amount AS sii_amount,
            sii.net_rate AS sii_net_rate,
            sii.net_amount AS sii_net_amount,
            sii.base_net_rate AS sii_base_net_rate,
            sii.base_net_amount AS sii_base_net_amount,
            sii.expense_account AS sii_expense_account,
            sii.warehouse AS sii_warehouse,
            sii.serial_and_batch_bundle AS sii_serial_and_batch_bundle,
            sii.batch_no AS sii_batch_no,
            sii.pos_invoice AS sii_pos_invoice,
            sii.pos_invoice_item AS sii_pos_invoice_item,
            sii.cost_center AS sii_cost_center,

            -- Delivery Note Fields
            dn.name AS dn_ref,
            dn.customer AS dn_customer,
            dn.customer_name AS dn_customer_name,
            dn.posting_date AS dn_posting_date,
            dn.company AS dn_company,
            dn.is_return AS dn_is_return,
            dn.issue_credit_note AS dn_issue_credit_note,
            dn.return_against AS dn_return_against,
            dn.cost_center AS dn_cost_center,
            dn.currency AS dn_currency,
            dn.total_qty AS dn_total_qty,
            dn.total_net_weight AS dn_total_net_weight,
            dn.base_total AS dn_base_total,
            dn.base_net_total AS dn_base_net_total,
            dn.total AS dn_total,
            dn.net_total AS dn_net_total,
            dn.total_taxes_and_charges AS dn_total_taxes_and_charges,
            dn.grand_total AS dn_grand_total,
            dn.status AS dn_status,
            dn.per_returned AS dn_per_returned,

            -- Delivery Note Item Fields
            dni.name AS dn_item,
            dni.item_code AS dni_item_code,
            dni.brand AS dni_brand,
            dni.item_group AS dni_item_group,
            dni.qty AS dni_qty,
            dni.stock_uom AS dni_stock_uom,
            dni.uom AS dni_uom,
            dni.conversion_factor AS dni_conversion_factor,
            dni.stock_qty AS dni_stock_qty,
            dni.rate AS dni_rate,
            dni.amount AS dni_amount,
            dni.net_rate AS dni_net_rate,
            dni.net_amount AS dni_net_amount,
            dni.base_net_rate AS dni_base_net_rate,
            dni.base_net_amount AS dni_base_net_amount,
            dni.warehouse AS dni_warehouse,
            dni.serial_and_batch_bundle AS dni_serial_and_batch_bundle,
            dni.batch_no AS dni_batch_no,
            dni.expense_account AS dni_expense_account,
            dni.cost_center AS dni_cost_center,

            -- Stock Ledger Entry Fields (from either DN or SI path)
            COALESCE(sledn.item_code, slesi.item_code) AS sle_item_code,
            COALESCE(sledn.warehouse, slesi.warehouse) AS sle_warehouse,
            COALESCE(sledn.posting_date, slesi.posting_date) AS sle_posting_date,
            COALESCE(sledn.voucher_type, slesi.voucher_type) AS sle_voucher_type,
            COALESCE(sledn.voucher_no, slesi.voucher_no) AS sle_voucher_no,
            COALESCE(sledn.voucher_detail_no, slesi.voucher_detail_no) AS sle_voucher_detail_no,
            COALESCE(sledn.serial_and_batch_bundle, slesi.serial_and_batch_bundle) AS sle_serial_and_batch_bundle,
            COALESCE(sledn.recalculate_rate, slesi.recalculate_rate) AS sle_recalculate_rate,
            COALESCE(sledn.actual_qty, slesi.actual_qty) AS sle_actual_qty,
            COALESCE(sledn.incoming_rate, slesi.incoming_rate) AS sle_incoming_rate,
            COALESCE(sledn.outgoing_rate, slesi.outgoing_rate) AS sle_outgoing_rate,
            COALESCE(sledn.valuation_rate, slesi.valuation_rate) AS sle_valuation_rate,
            COALESCE(sledn.stock_value, slesi.stock_value) AS sle_stock_value,
            COALESCE(sledn.stock_value_difference, slesi.stock_value_difference) AS sle_stock_value_difference,
            COALESCE(sledn.stock_uom, slesi.stock_uom) AS sle_stock_uom,
            COALESCE(sledn.fiscal_year, slesi.fiscal_year) AS sle_fiscal_year,
            COALESCE(sledn.batch_no, slesi.batch_no, sbe_v15.batch_no) AS batch_no,

            sbe_v15.serial_no AS sbe_serial_no,
            sbe_v15.qty AS sbe_qty,
            sbe_v15.warehouse AS sbe_warehouse,
            sbe_v15.delivered_qty AS sbe_delivered_qty,
            sbe_v15.incoming_rate AS sbe_incoming_rate,

            sbb.name AS sbb_name,
            sbb.company AS sbb_company,
            sbb.item_code AS sbb_item_code,
            sbb.warehouse AS sbb_warehouse,
            sbb.total_qty AS sbb_total_qty,
            sbb.voucher_type AS sbb_voucher_type,
            sbb.voucher_no AS sbb_voucher_no,
            sbb.voucher_detail_no AS sbb_voucher_detail_no

            FROM `tabSales Order Item` soi
            LEFT JOIN `tabSales Order` so
            ON soi.parent = so.name
            LEFT JOIN `tabDelivery Note Item` dni
            ON soi.name = dni.so_detail
            LEFT JOIN `tabDelivery Note` dn
            ON dni.parent = dn.name
            LEFT JOIN `tabSales Invoice Item` sii
            ON soi.name = sii.so_detail
            LEFT JOIN `tabSales Invoice` si
            ON sii.parent = si.name
            LEFT JOIN `tabStock Ledger Entry` sledn
            ON sledn.voucher_no = dni.parent
            AND sledn.voucher_detail_no = dni.name
            AND sledn.voucher_type   = 'Delivery Note'
            AND sledn.is_cancelled   = 0
            LEFT JOIN `tabStock Ledger Entry` slesi
            ON slesi.voucher_no = sii.parent
            AND slesi.voucher_detail_no = sii.name
            AND slesi.voucher_type   = 'Sales Invoice'
            AND slesi.is_cancelled   = 0

            -- v15 LOGIC: Join via Bundle
            LEFT JOIN `tabSerial and Batch Bundle` sbb
            ON sbb.name = COALESCE(sledn.serial_and_batch_bundle, slesi.serial_and_batch_bundle)
            AND COALESCE(sledn.batch_no, slesi.batch_no) IS NULL
            AND COALESCE(sledn.is_cancelled, slesi.is_cancelled) = 0

            LEFT JOIN `tabSerial and Batch Entry` sbe_v15
            ON sbe_v15.parent = sbb.name

        UNION

        SELECT
            -- Sales Order Item Fields
            NULL AS soi_item,
            NULL AS soi_item_code,
            NULL AS soi_is_stock_item,
            NULL AS soi_item_group,
            NULL AS soi_brand,
            NULL AS soi_qty,
            NULL AS soi_stock_uom,
            NULL AS soi_uom,
            NULL AS soi_conversion_factor,
            NULL AS soi_stock_qty,
            NULL AS soi_rate,
            NULL AS soi_amount,
            NULL AS soi_net_rate,
            NULL AS soi_net_amount,
            NULL AS soi_base_net_rate,
            NULL AS soi_base_net_amount,

            -- Sales Order
            NULL AS so_name,
            NULL AS so_customer,
            NULL AS so_customer_name,
            NULL AS so_order_type,
            NULL AS so_transaction_date,
            NULL AS so_company,
            NULL AS so_cost_center,
            NULL AS so_currency,
            NULL AS so_set_warehouse,
            NULL AS so_total_qty,
            NULL AS so_total_net_weight,
            NULL AS so_base_total,
            NULL AS so_base_net_total,
            NULL AS so_total,
            NULL AS so_net_total,
            NULL AS so_total_taxes_and_charges,
            NULL AS so_base_grand_total,
            NULL AS so_grand_total,
            NULL AS so_status,
            NULL AS so_delivery_status,
            NULL AS so_billing_status,

            si.name AS si_name,
            si.customer AS si_customer,
            si.customer_name AS si_customer_name,
            si.company AS si_company,
            si.posting_date AS si_posting_date,
            si.pos_profile AS si_pos_profile,
            si.is_return AS si_is_return,
            si.return_against AS si_return_against,
            si.is_debit_note AS si_is_debit_note,
            si.cost_center AS si_cost_center,
            si.currency AS si_currency,
            si.update_stock AS si_update_stock,
            si.set_warehouse AS si_set_warehouse,
            si.set_target_warehouse AS si_set_target_warehouse,
            si.total_qty AS si_total_qty,
            si.total_net_weight AS si_total_net_weight,
            si.base_total AS si_base_total,
            si.base_net_total AS si_base_net_total,
            si.total AS si_total,
            si.net_total AS si_net_total,
            si.total_taxes_and_charges AS si_total_taxes_and_charges,
            si.base_grand_total AS si_base_grand_total,
            si.grand_total AS si_grand_total,
            si.status AS si_status,

            -- Sales Invoice Item Fields
            sii.name AS sii_item,
            sii.item_code AS sii_item_code,
            sii.item_group AS sii_item_group,
            sii.brand AS sii_brand,
            sii.qty AS sii_qty,
            sii.stock_uom AS sii_stock_uom,
            sii.uom AS sii_uom,
            sii.conversion_factor AS sii_conversion_factor,
            sii.stock_qty AS sii_stock_qty,
            sii.rate AS sii_rate,
            sii.amount AS sii_amount,
            sii.net_rate AS sii_net_rate,
            sii.net_amount AS sii_net_amount,
            sii.base_net_rate AS sii_base_net_rate,
            sii.base_net_amount AS sii_base_net_amount,
            sii.expense_account AS sii_expense_account,
            sii.warehouse AS sii_warehouse,
            sii.serial_and_batch_bundle AS sii_serial_and_batch_bundle,
            sii.batch_no AS sii_batch_no,
            sii.pos_invoice AS sii_pos_invoice,
            sii.pos_invoice_item AS sii_pos_invoice_item,
            sii.cost_center AS sii_cost_center,

            -- Delivery Note Fields
            dn.name AS dn_ref,
            dn.customer AS dn_customer,
            dn.customer_name AS dn_customer_name,
            dn.posting_date AS dn_posting_date,
            dn.company AS dn_company,
            dn.is_return AS dn_is_return,
            dn.issue_credit_note AS dn_issue_credit_note,
            dn.return_against AS dn_return_against,
            dn.cost_center AS dn_cost_center,
            dn.currency AS dn_currency,
            dn.total_qty AS dn_total_qty,
            dn.total_net_weight AS dn_total_net_weight,
            dn.base_total AS dn_base_total,
            dn.base_net_total AS dn_base_net_total,
            dn.total AS dn_total,
            dn.net_total AS dn_net_total,
            dn.total_taxes_and_charges AS dn_total_taxes_and_charges,
            dn.grand_total AS dn_grand_total,
            dn.status AS dn_status,
            dn.per_returned AS dn_per_returned,

            -- Delivery Note Item Fields
            dni.name AS dn_item,
            dni.item_code AS dni_item_code,
            dni.brand AS dni_brand,
            dni.item_group AS dni_item_group,
            dni.qty AS dni_qty,
            dni.stock_uom AS dni_stock_uom,
            dni.uom AS dni_uom,
            dni.conversion_factor AS dni_conversion_factor,
            dni.stock_qty AS dni_stock_qty,
            dni.rate AS dni_rate,
            dni.amount AS dni_amount,
            dni.net_rate AS dni_net_rate,
            dni.net_amount AS dni_net_amount,
            dni.base_net_rate AS dni_base_net_rate,
            dni.base_net_amount AS dni_base_net_amount,
            dni.warehouse AS dni_warehouse,
            dni.serial_and_batch_bundle AS dni_serial_and_batch_bundle,
            dni.batch_no AS dni_batch_no,
            dni.expense_account AS dni_expense_account,
            dni.cost_center AS dni_cost_center,

            -- Stock Ledger Entry Fields (from either DN or SI path)
            sle.item_code AS sle_item_code,
            sle.warehouse AS sle_warehouse,
            sle.posting_date AS sle_posting_date,
            sle.voucher_type AS sle_voucher_type,
            sle.voucher_no AS sle_voucher_no,
            sle.voucher_detail_no AS sle_voucher_detail_no,
            sle.serial_and_batch_bundle AS sle_serial_and_batch_bundle,
            sle.recalculate_rate AS sle_recalculate_rate,
            sle.actual_qty AS sle_actual_qty,
            sle.incoming_rate AS sle_incoming_rate,
            sle.outgoing_rate AS sle_outgoing_rate,
            sle.valuation_rate AS sle_valuation_rate,
            sle.stock_value AS sle_stock_value,
            sle.stock_value_difference AS sle_stock_value_difference,
            sle.stock_uom AS sle_stock_uom,
            sle.fiscal_year AS sle_fiscal_year,
            COALESCE(sle.batch_no, sbe_v15.batch_no) AS batch_no,

            sbe_v15.serial_no AS sbe_serial_no,
            sbe_v15.qty AS sbe_qty,
            sbe_v15.warehouse AS sbe_warehouse,
            sbe_v15.delivered_qty AS sbe_delivered_qty,
            sbe_v15.incoming_rate AS sbe_incoming_rate,

            sbb.name AS sbb_name,
            sbb.company AS sbb_company,
            sbb.item_code AS sbb_item_code,
            sbb.warehouse AS sbb_warehouse,
            sbb.total_qty AS sbb_total_qty,
            sbb.voucher_type AS sbb_voucher_type,
            sbb.voucher_no AS sbb_voucher_no,
            sbb.voucher_detail_no AS sbb_voucher_detail_no

            FROM `tabDelivery Note Item` dni
            LEFT JOIN `tabDelivery Note` dn
            ON dni.parent = dn.name
            LEFT JOIN `tabSales Invoice Item` sii
            ON dni.name = sii.dn_detail
            LEFT JOIN `tabSales Invoice` si
            ON sii.parent = si.name
            LEFT JOIN `tabStock Ledger Entry` sle
            ON sle.voucher_no   = dni.parent
            AND sle.voucher_detail_no = dni.name
            AND sle.voucher_type     = 'Delivery Note'
            AND sle.is_cancelled     = 0

            -- v15 LOGIC: Join via Bundle
            LEFT JOIN `tabSerial and Batch Bundle` sbb
            ON sbb.name = sle.serial_and_batch_bundle
            AND sle.batch_no IS NULL
            AND sle.is_cancelled = 0

            LEFT JOIN `tabSerial and Batch Entry` sbe_v15
            ON sbe_v15.parent = sbb.name

            WHERE (dni.so_detail IS NULL OR dni.so_detail = '')

        UNION

        SELECT
            -- Sales Order Item Fields
            NULL AS soi_item,
            NULL AS soi_item_code,
            NULL AS soi_is_stock_item,
            NULL AS soi_item_group,
            NULL AS soi_brand,
            NULL AS soi_qty,
            NULL AS soi_stock_uom,
            NULL AS soi_uom,
            NULL AS soi_conversion_factor,
            NULL AS soi_stock_qty,
            NULL AS soi_rate,
            NULL AS soi_amount,
            NULL AS soi_net_rate,
            NULL AS soi_net_amount,
            NULL AS soi_base_net_rate,
            NULL AS soi_base_net_amount,

            -- Sales Order
            NULL AS so_name,
            NULL AS so_customer,
            NULL AS so_customer_name,
            NULL AS so_order_type,
            NULL AS so_transaction_date,
            NULL AS so_company,
            NULL AS so_cost_center,
            NULL AS so_currency,
            NULL AS so_set_warehouse,
            NULL AS so_total_qty,
            NULL AS so_total_net_weight,
            NULL AS so_base_total,
            NULL AS so_base_net_total,
            NULL AS so_total,
            NULL AS so_net_total,
            NULL AS so_total_taxes_and_charges,
            NULL AS so_base_grand_total,
            NULL AS so_grand_total,
            NULL AS so_status,
            NULL AS so_delivery_status,
            NULL AS so_billing_status,

            si.name AS si_name,
            si.customer AS si_customer,
            si.customer_name AS si_customer_name,
            si.company AS si_company,
            si.posting_date AS si_posting_date,
            si.pos_profile AS si_pos_profile,
            si.is_return AS si_is_return,
            si.return_against AS si_return_against,
            si.is_debit_note AS si_is_debit_note,
            si.cost_center AS si_cost_center,
            si.currency AS si_currency,
            si.update_stock AS si_update_stock,
            si.set_warehouse AS si_set_warehouse,
            si.set_target_warehouse AS si_set_target_warehouse,
            si.total_qty AS si_total_qty,
            si.total_net_weight AS si_total_net_weight,
            si.base_total AS si_base_total,
            si.base_net_total AS si_base_net_total,
            si.total AS si_total,
            si.net_total AS si_net_total,
            si.total_taxes_and_charges AS si_total_taxes_and_charges,
            si.base_grand_total AS si_base_grand_total,
            si.grand_total AS si_grand_total,
            si.status AS si_status,

            -- Sales Invoice Item Fields
            sii.name AS sii_item,
            sii.item_code AS sii_item_code,
            sii.item_group AS sii_item_group,
            sii.brand AS sii_brand,
            sii.qty AS sii_qty,
            sii.stock_uom AS sii_stock_uom,
            sii.uom AS sii_uom,
            sii.conversion_factor AS sii_conversion_factor,
            sii.stock_qty AS sii_stock_qty,
            sii.rate AS sii_rate,
            sii.amount AS sii_amount,
            sii.net_rate AS sii_net_rate,
            sii.net_amount AS sii_net_amount,
            sii.base_net_rate AS sii_base_net_rate,
            sii.base_net_amount AS sii_base_net_amount,
            sii.expense_account AS sii_expense_account,
            sii.warehouse AS sii_warehouse,
            sii.serial_and_batch_bundle AS sii_serial_and_batch_bundle,
            sii.batch_no AS sii_batch_no,
            sii.pos_invoice AS sii_pos_invoice,
            sii.pos_invoice_item AS sii_pos_invoice_item,
            sii.cost_center AS sii_cost_center,

            -- Delivery Note Fields
            NULL AS dn_ref,
            NULL AS dn_customer,
            NULL AS dn_customer_name,
            NULL AS dn_posting_date,
            NULL AS dn_company,
            NULL AS dn_is_return,
            NULL AS dn_issue_credit_note,
            NULL AS dn_return_against,
            NULL AS dn_cost_center,
            NULL AS dn_currency,
            NULL AS dn_total_qty,
            NULL AS dn_total_net_weight,
            NULL AS dn_base_total,
            NULL AS dn_base_net_total,
            NULL AS dn_total,
            NULL AS dn_net_total,
            NULL AS dn_total_taxes_and_charges,
            NULL AS dn_grand_total,
            NULL AS dn_status,
            NULL AS dn_per_returned,

            -- Delivery Note Item Fields
            NULL AS dn_item,
            NULL AS dni_item_code,
            NULL AS dni_brand,
            NULL AS dni_item_group,
            NULL AS dni_qty,
            NULL AS dni_stock_uom,
            NULL AS dni_uom,
            NULL AS dni_conversion_factor,
            NULL AS dni_stock_qty,
            NULL AS dni_rate,
            NULL AS dni_amount,
            NULL AS dni_net_rate,
            NULL AS dni_net_amount,
            NULL AS dni_base_net_rate,
            NULL AS dni_base_net_amount,
            NULL AS dni_warehouse,
            NULL AS dni_serial_and_batch_bundle,
            NULL AS dni_batch_no,
            NULL AS dni_expense_account,
            NULL AS dni_cost_center,

            -- Stock Ledger Entry Fields (from either DN or SI path)
            sle.item_code AS sle_item_code,
            sle.warehouse AS sle_warehouse,
            sle.posting_date AS sle_posting_date,
            sle.voucher_type AS sle_voucher_type,
            sle.voucher_no AS sle_voucher_no,
            sle.voucher_detail_no AS sle_voucher_detail_no,
            sle.serial_and_batch_bundle AS sle_serial_and_batch_bundle,
            sle.recalculate_rate AS sle_recalculate_rate,
            sle.actual_qty AS sle_actual_qty,
            sle.incoming_rate AS sle_incoming_rate,
            sle.outgoing_rate AS sle_outgoing_rate,
            sle.valuation_rate AS sle_valuation_rate,
            sle.stock_value AS sle_stock_value,
            sle.stock_value_difference AS sle_stock_value_difference,
            sle.stock_uom AS sle_stock_uom,
            sle.fiscal_year AS sle_fiscal_year,
            COALESCE(sle.batch_no, sbe_v15.batch_no) AS batch_no,

            sbe_v15.serial_no AS sbe_serial_no,
            sbe_v15.qty AS sbe_qty,
            sbe_v15.warehouse AS sbe_warehouse,
            sbe_v15.delivered_qty AS sbe_delivered_qty,
            sbe_v15.incoming_rate AS sbe_incoming_rate,

            sbb.name AS sbb_name,
            sbb.company AS sbb_company,
            sbb.item_code AS sbb_item_code,
            sbb.warehouse AS sbb_warehouse,
            sbb.total_qty AS sbb_total_qty,
            sbb.voucher_type AS sbb_voucher_type,
            sbb.voucher_no AS sbb_voucher_no,
            sbb.voucher_detail_no AS sbb_voucher_detail_no

        FROM `tabSales Invoice Item` sii
        LEFT JOIN `tabSales Invoice` si
            ON sii.parent = si.name
        LEFT JOIN `tabStock Ledger Entry` sle
            ON sle.voucher_no    = sii.parent
            AND sle.voucher_detail_no = sii.name
            AND sle.voucher_type   = 'Sales Invoice'
            AND sle.is_cancelled   = 0

        -- v15 LOGIC: Join via Bundle
        LEFT JOIN `tabSerial and Batch Bundle` sbb
            ON sbb.name = sle.serial_and_batch_bundle
            AND sle.batch_no IS NULL
            AND sle.is_cancelled = 0

        LEFT JOIN `tabSerial and Batch Entry` sbe_v15
            ON sbe_v15.parent = sbb.name

        WHERE (sii.so_detail IS NULL OR sii.so_detail = '')
        AND (sii.dn_detail IS NULL OR sii.dn_detail = '')

        ) AS combined_sales
        HAVING 
            (posting_date >= %(from_date)s OR posting_date IS NULL)
            AND (posting_date <= %(to_date)s OR posting_date IS NULL)



"""
    
    
    # 1. Generate Chart Data
    chart = get_chart_data(data)
    
    # 2. Generate Report Summary (The small boxes at the top)
    report_summary = get_report_summary(data)

    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "soi_item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Sales Order"), "fieldname": "so_name", "fieldtype": "Link", "options": "Sales Order", "width": 140},
        {"label": _("Delivery Note"), "fieldname": "dn_ref", "fieldtype": "Link", "options": "Delivery Note", "width": 140},
        {"label": _("Sales Invoice"), "fieldname": "si_name", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
        {"label": _("Batch"), "fieldname": "batch_no", "fieldtype": "Data", "width": 100},
        {"label": _("Qty"), "fieldname": "soi_qty", "fieldtype": "Float", "width": 80},
        {"label": _("SI Status"), "fieldname": "si_date_status", "fieldtype": "Data", "width": 120},
        {"label": _("DN Status"), "fieldname": "dn_date_status", "fieldtype": "Data", "width": 120},
    ]

def get_chart_data(data):
    if not data:
        return None

    labels = []
    values = []

    # Simple logic: Grouping qty by date for the trend line
    for row in data:
        labels.append(row.get("posting_date"))
        values.append(row.get("soi_qty") or 0)

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("Quantity Sold"), "values": values}]
        },
        "type": "line", # You can use 'bar', 'line', 'percentage', 'pie'
        "colors": ["#7cd6fd"]
    }

def get_report_summary(data):
    if not data:
        return None

    total_qty = sum(row.get("soi_qty") or 0 for row in data)
    total_amount = sum(row.get("soi_amount") or 0 for row in data)

    return [
        {
            "value": total_qty,
            "indicator": "Blue",
            "label": _("Total Quantity"),
            "datatype": "Float",
        },
        {
            "value": total_amount,
            "indicator": "Green",
            "label": _("Total Value"),
            "datatype": "Currency",
        }
    ]