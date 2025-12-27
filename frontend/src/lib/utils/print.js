/**
 * Print Receipt Utilities
 * Supports both browser print and thermal printer (ESC/POS)
 */

/**
 * Format currency to Indonesian Rupiah
 */
function formatCurrency(amount) {
	return new Intl.NumberFormat('id-ID', {
		style: 'currency',
		currency: 'IDR',
		minimumFractionDigits: 0
	}).format(amount);
}

/**
 * Format date and time
 */
function formatDateTime(dateString) {
	const date = new Date(dateString);
	return {
		date: date.toLocaleDateString('id-ID', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric'
		}),
		time: date.toLocaleTimeString('id-ID', {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		})
	};
}

/**
 * Generate HTML for browser print
 */
function generateReceiptHTML(order) {
	const { date, time } = formatDateTime(order.created_at);
	
	return `
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>Receipt - ${order.order_number}</title>
	<style>
		@media print {
			@page {
				size: 80mm auto;
				margin: 0;
			}
			body {
				margin: 0;
				padding: 0;
			}
		}
		
		body {
			font-family: 'Courier New', monospace;
			font-size: 12px;
			line-height: 1.4;
			max-width: 80mm;
			margin: 0 auto;
			padding: 10mm;
			background: white;
		}
		
		.receipt {
			width: 100%;
		}
		
		.header {
			text-align: center;
			margin-bottom: 10px;
			border-bottom: 2px dashed #000;
			padding-bottom: 10px;
		}
		
		.header h1 {
			margin: 0 0 5px 0;
			font-size: 18px;
			font-weight: bold;
		}
		
		.header .tenant-name {
			font-size: 16px;
			font-weight: bold;
			margin: 5px 0;
		}
		
		.header .info {
			font-size: 11px;
			margin: 2px 0;
		}
		
		.section {
			margin: 10px 0;
			padding: 5px 0;
		}
		
		.section-title {
			font-weight: bold;
			margin-bottom: 5px;
			border-bottom: 1px solid #000;
			padding-bottom: 3px;
		}
		
		.item {
			display: flex;
			justify-content: space-between;
			margin: 5px 0;
		}
		
		.item-name {
			flex: 1;
		}
		
		.item-qty {
			width: 30px;
			text-align: center;
		}
		
		.item-price {
			width: 80px;
			text-align: right;
		}
		
		.modifier {
			font-size: 11px;
			padding-left: 10px;
			color: #666;
		}
		
		.totals {
			border-top: 1px solid #000;
			padding-top: 10px;
			margin-top: 10px;
		}
		
		.total-row {
			display: flex;
			justify-content: space-between;
			margin: 3px 0;
		}
		
		.total-row.grand-total {
			font-weight: bold;
			font-size: 14px;
			border-top: 2px solid #000;
			padding-top: 5px;
			margin-top: 5px;
		}
		
		.footer {
			text-align: center;
			margin-top: 15px;
			padding-top: 10px;
			border-top: 2px dashed #000;
			font-size: 11px;
		}
		
		.footer .thank-you {
			font-weight: bold;
			margin: 10px 0;
		}
		
		.barcode {
			text-align: center;
			margin: 10px 0;
			font-family: 'Libre Barcode 128', cursive;
			font-size: 40px;
		}
	</style>
</head>
<body>
	<div class="receipt">
		<!-- Header -->
		<div class="header">
			<h1>FOOD COURT</h1>
			<div class="tenant-name">${order.tenant_name || 'Unknown Tenant'}</div>
			<div class="info">Order: ${order.order_number}</div>
			<div class="info">Date: ${date}</div>
			<div class="info">Time: ${time}</div>
			${order.table_number ? `<div class="info">Table: ${order.table_number}</div>` : ''}
			${order.customer_name ? `<div class="info">Customer: ${order.customer_name}</div>` : ''}
		</div>
		
		<!-- Items -->
		<div class="section">
			<div class="section-title">ORDER ITEMS</div>
			${order.items.map(item => `
				<div class="item">
					<div class="item-name">${item.product_name}</div>
					<div class="item-qty">x${item.quantity}</div>
					<div class="item-price">${formatCurrency(item.unit_price)}</div>
				</div>
				${item.modifiers && item.modifiers.length > 0 ? item.modifiers.map(mod => `
					<div class="modifier">+ ${mod.name} ${mod.price_adjustment && mod.price_adjustment !== 0 ? formatCurrency(mod.price_adjustment) : ''}</div>
				`).join('') : ''}
				<div class="item">
					<div class="item-name"></div>
					<div class="item-qty"></div>
					<div class="item-price">${formatCurrency(item.total_price)}</div>
				</div>
			`).join('')}
		</div>
		
		<!-- Totals -->
		<div class="totals">
			<div class="total-row">
				<span>Subtotal:</span>
				<span>${formatCurrency(order.subtotal)}</span>
			</div>
			${order.tax_amount > 0 ? `
				<div class="total-row">
					<span>Tax (10%):</span>
					<span>${formatCurrency(order.tax_amount)}</span>
				</div>
			` : ''}
			${order.service_charge_amount > 0 ? `
				<div class="total-row">
					<span>Service (5%):</span>
					<span>${formatCurrency(order.service_charge_amount)}</span>
				</div>
			` : ''}
			${order.discount_amount > 0 ? `
				<div class="total-row">
					<span>Discount:</span>
					<span>-${formatCurrency(order.discount_amount)}</span>
				</div>
			` : ''}
			<div class="total-row grand-total">
				<span>TOTAL:</span>
				<span>${formatCurrency(order.total_amount)}</span>
			</div>
		</div>
		
		<!-- Payment Info -->
		<div class="section">
			<div class="section-title">PAYMENT</div>
			<div class="total-row">
				<span>Method:</span>
				<span>${order.payment_method ? order.payment_method.toUpperCase() : 'CASH'}</span>
			</div>
			<div class="total-row">
				<span>Status:</span>
				<span>${order.payment_status ? order.payment_status.toUpperCase() : 'UNPAID'}</span>
			</div>
		</div>
		
		<!-- Footer -->
		<div class="footer">
			<div class="barcode">${order.order_number}</div>
			<div class="thank-you">TERIMA KASIH</div>
			<div>Silakan datang kembali!</div>
		</div>
	</div>
	
	<script>
		// Auto print when loaded
		window.onload = function() {
			window.print();
			// Close window after print dialog
			window.onafterprint = function() {
				window.close();
			};
		};
	</script>
</body>
</html>
	`;
}

/**
 * Print receipt using browser print dialog
 * Opens receipt in new window and triggers print
 */
export function printReceipt(order) {
	try {
		console.log('🖨️ Printing receipt for order:', order.order_number);
		
		// Generate HTML
		const html = generateReceiptHTML(order);
		
		// Open new window
		const printWindow = window.open('', '_blank', 'width=300,height=600');
		
		if (!printWindow) {
			throw new Error('Popup blocked! Please allow popups for this site.');
		}
		
		// Write HTML to new window
		printWindow.document.write(html);
		printWindow.document.close();
		
		console.log('✅ Print window opened successfully');
		return true;
	} catch (error) {
		console.error('❌ Print error:', error);
		alert('Failed to print receipt: ' + error.message);
		return false;
	}
}

/**
 * Generate ESC/POS commands for thermal printer
 * Returns Uint8Array that can be sent to thermal printer
 */
export function generateThermalReceipt(order) {
	const { date, time } = formatDateTime(order.created_at);
	
	// ESC/POS Commands
	const ESC = 0x1B;
	const GS = 0x1D;
	
	// Text formatting
	const INIT = [ESC, 0x40]; // Initialize printer
	const ALIGN_CENTER = [ESC, 0x61, 0x01];
	const ALIGN_LEFT = [ESC, 0x61, 0x00];
	const BOLD_ON = [ESC, 0x45, 0x01];
	const BOLD_OFF = [ESC, 0x45, 0x00];
	const DOUBLE_HEIGHT = [ESC, 0x21, 0x10];
	const NORMAL_SIZE = [ESC, 0x21, 0x00];
	const CUT_PAPER = [GS, 0x56, 0x00];
	const LINE_FEED = [0x0A];
	
	// Build receipt data
	const commands = [];
	
	// Helper to add text
	function addText(text) {
		const encoder = new TextEncoder();
		commands.push(...encoder.encode(text));
	}
	
	function addCommand(...bytes) {
		commands.push(...bytes);
	}
	
	function addLine(text = '') {
		addText(text);
		addCommand(...LINE_FEED);
	}
	
	function addDashedLine() {
		addLine('--------------------------------');
	}
	
	function addPaddedLine(left, right) {
		const maxWidth = 32;
		const padding = maxWidth - left.length - right.length;
		addLine(left + ' '.repeat(Math.max(0, padding)) + right);
	}
	
	// Initialize
	addCommand(...INIT);
	
	// Header
	addCommand(...ALIGN_CENTER, ...BOLD_ON, ...DOUBLE_HEIGHT);
	addLine('FOOD COURT');
	addCommand(...NORMAL_SIZE);
	addLine(order.tenant_name || 'Unknown Tenant');
	addCommand(...BOLD_OFF);
	addCommand(...ALIGN_LEFT);
	addDashedLine();
	
	// Order info
	addLine(`Order: ${order.order_number}`);
	addLine(`Date: ${date}`);
	addLine(`Time: ${time}`);
	if (order.table_number) addLine(`Table: ${order.table_number}`);
	if (order.customer_name) addLine(`Customer: ${order.customer_name}`);
	addDashedLine();
	
	// Items
	addCommand(...BOLD_ON);
	addLine('ORDER ITEMS');
	addCommand(...BOLD_OFF);
	addLine();
	
	order.items.forEach(item => {
		// Item name and quantity
		addLine(`${item.product_name} x${item.quantity}`);
		
		// Modifiers
		if (item.modifiers && item.modifiers.length > 0) {
			item.modifiers.forEach(mod => {
				const modText = `  + ${mod.name}`;
				if (mod.price_adjustment && mod.price_adjustment !== 0) {
					addPaddedLine(modText, formatCurrency(mod.price_adjustment));
				} else {
					addLine(modText);
				}
			});
		}
		
		// Item total
		addPaddedLine('', formatCurrency(item.total_price));
		addLine();
	});
	
	addDashedLine();
	
	// Totals
	addPaddedLine('Subtotal:', formatCurrency(order.subtotal));
	if (order.tax_amount > 0) {
		addPaddedLine('Tax (10%):', formatCurrency(order.tax_amount));
	}
	if (order.service_charge_amount > 0) {
		addPaddedLine('Service (5%):', formatCurrency(order.service_charge_amount));
	}
	if (order.discount_amount > 0) {
		addPaddedLine('Discount:', `-${formatCurrency(order.discount_amount)}`);
	}
	
	addDashedLine();
	addCommand(...BOLD_ON, ...DOUBLE_HEIGHT);
	addPaddedLine('TOTAL:', formatCurrency(order.total_amount));
	addCommand(...NORMAL_SIZE, ...BOLD_OFF);
	addDashedLine();
	
	// Payment
	addLine(`Payment: ${order.payment_method ? order.payment_method.toUpperCase() : 'CASH'}`);
	addLine(`Status: ${order.payment_status ? order.payment_status.toUpperCase() : 'UNPAID'}`);
	addDashedLine();
	
	// Footer
	addCommand(...ALIGN_CENTER, ...BOLD_ON);
	addLine();
	addLine('TERIMA KASIH');
	addCommand(...BOLD_OFF);
	addLine('Silakan datang kembali!');
	addLine();
	addLine(order.order_number);
	addLine();
	addLine();
	addLine();
	
	// Cut paper
	addCommand(...CUT_PAPER);
	
	return new Uint8Array(commands);
}

/**
 * Send receipt to thermal printer via Web Bluetooth
 * Requires HTTPS and user gesture
 */
export async function printThermalReceipt(order) {
	try {
		console.log('🖨️ Connecting to thermal printer...');
		
		// Request Bluetooth device
		const device = await navigator.bluetooth.requestDevice({
			filters: [
				{ services: ['000018f0-0000-1000-8000-00805f9b34fb'] }, // Printer service
			],
			optionalServices: ['battery_service']
		});
		
		console.log('📱 Connecting to:', device.name);
		
		const server = await device.gatt.connect();
		const service = await server.getPrimaryService('000018f0-0000-1000-8000-00805f9b34fb');
		const characteristic = await service.getCharacteristic('00002af1-0000-1000-8000-00805f9b34fb');
		
		// Generate receipt data
		const data = generateThermalReceipt(order);
		
		// Send data in chunks (max 20 bytes per write)
		const chunkSize = 20;
		for (let i = 0; i < data.length; i += chunkSize) {
			const chunk = data.slice(i, i + chunkSize);
			await characteristic.writeValue(chunk);
			await new Promise(resolve => setTimeout(resolve, 10)); // Small delay between chunks
		}
		
		console.log('✅ Receipt sent to thermal printer');
		device.gatt.disconnect();
		return true;
		
	} catch (error) {
		console.error('❌ Thermal printer error:', error);
		
		if (error.name === 'NotFoundError') {
			alert('No printer found. Make sure your Bluetooth printer is turned on and nearby.');
		} else if (error.name === 'SecurityError') {
			alert('Bluetooth access denied. Please use HTTPS and allow Bluetooth access.');
		} else {
			alert('Failed to print: ' + error.message);
		}
		
		return false;
	}
}

/**
 * Print all receipts from checkout result
 * Checkout result contains multiple orders (one per tenant)
 */
export function printAllReceipts(checkoutResult) {
	if (!checkoutResult || !checkoutResult.orders || checkoutResult.orders.length === 0) {
		alert('No orders to print');
		return;
	}
	
	console.log(`🖨️ Printing ${checkoutResult.orders.length} receipt(s)...`);
	
	let printed = 0;
	checkoutResult.orders.forEach((order, index) => {
		// Add small delay between prints to avoid browser blocking
		setTimeout(() => {
			if (printReceipt(order)) {
				printed++;
			}
		}, index * 500); // 500ms delay between each print
	});
	
	console.log(`✅ Queued ${printed} receipt(s) for printing`);
}

/**
 * Download receipt as text file
 */
export function downloadReceipt(order) {
	try {
		const { date, time } = formatDateTime(order.created_at);
		
		let text = '';
		text += '================================\n';
		text += '         FOOD COURT\n';
		text += `   ${order.tenant_name || 'Unknown Tenant'}\n`;
		text += '================================\n\n';
		text += `Order: ${order.order_number}\n`;
		text += `Date: ${date}\n`;
		text += `Time: ${time}\n`;
		if (order.table_number) text += `Table: ${order.table_number}\n`;
		if (order.customer_name) text += `Customer: ${order.customer_name}\n`;
		text += '--------------------------------\n\n';
		text += 'ORDER ITEMS\n\n';
		
		order.items.forEach(item => {
			text += `${item.product_name} x${item.quantity}\n`;
			text += `  ${formatCurrency(item.unit_price)}\n`;
			
			if (item.modifiers && item.modifiers.length > 0) {
				item.modifiers.forEach(mod => {
					text += `  + ${mod.name}`;
					if (mod.price_adjustment && mod.price_adjustment !== 0) {
						text += ` ${formatCurrency(mod.price_adjustment)}`;
					}
					text += '\n';
				});
			}
			
			text += `  Total: ${formatCurrency(item.total_price)}\n\n`;
		});
		
		text += '--------------------------------\n';
		text += `Subtotal: ${formatCurrency(order.subtotal)}\n`;
		if (order.tax_amount > 0) text += `Tax (10%): ${formatCurrency(order.tax_amount)}\n`;
		if (order.service_charge_amount > 0) text += `Service (5%): ${formatCurrency(order.service_charge_amount)}\n`;
		if (order.discount_amount > 0) text += `Discount: -${formatCurrency(order.discount_amount)}\n`;
		text += `TOTAL: ${formatCurrency(order.total_amount)}\n`;
		text += '--------------------------------\n\n';
		text += `Payment: ${order.payment_method ? order.payment_method.toUpperCase() : 'CASH'}\n`;
		text += `Status: ${order.payment_status ? order.payment_status.toUpperCase() : 'UNPAID'}\n\n`;
		text += '================================\n';
		text += '       TERIMA KASIH\n';
		text += '   Silakan datang kembali!\n';
		text += '================================\n';
		
		// Create download
		const blob = new Blob([text], { type: 'text/plain' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `receipt-${order.order_number}.txt`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
		
		console.log('✅ Receipt downloaded:', a.download);
		return true;
	} catch (error) {
		console.error('❌ Download error:', error);
		alert('Failed to download receipt: ' + error.message);
		return false;
	}
}
