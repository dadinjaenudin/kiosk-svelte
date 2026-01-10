<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { syncProgress } from '$lib/services/syncService';
	
	let countdown = 15;
	let interval: ReturnType<typeof setInterval>;
	
	// Get order data from URL params
	$: orderNumber = $page.url.searchParams.get('orderNumber') || 'OFFLINE-XXX';
	$: paymentMethod = $page.url.searchParams.get('payment') || 'cash';
	$: totalAmount = parseFloat($page.url.searchParams.get('total') || '0');
	$: cashGiven = parseFloat($page.url.searchParams.get('cashGiven') || '0');
	$: changeAmount = parseFloat($page.url.searchParams.get('change') || '0');
	$: customerName = $page.url.searchParams.get('customerName') || 'Customer';
	$: customerPhone = $page.url.searchParams.get('customerPhone') || '';
	
	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
	
	function getPaymentIcon(method: string): string {
		switch(method) {
			case 'cash': return '💵';
			case 'card': return '💳';
			case 'qris': return '📱';
			case 'ewallet': return '📲';
			default: return '💰';
		}
	}
	
	function getPaymentName(method: string): string {
		switch(method) {
			case 'cash': return 'Cash';
			case 'card': return 'Card';
			case 'qris': return 'QRIS';
			case 'ewallet': return 'E-Wallet';
			default: return 'Unknown';
		}
	}
	
	onMount(() => {
		interval = setInterval(() => {
			countdown--;
			if (countdown === 0) {
				clearInterval(interval);
				goto('/kiosk');
			}
		}, 1000);
		
		return () => clearInterval(interval);
	});
	
	function goBackNow() {
		clearInterval(interval);
		goto('/kiosk');
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-orange-400 to-yellow-500 flex items-center justify-center p-4">
	<div class="bg-white rounded-3xl shadow-2xl p-8 max-w-2xl w-full text-center animate-fadeIn">
		<!-- Success Checkmark -->
		<div class="mb-6">
			<div class="w-32 h-32 mx-auto bg-gradient-to-br from-orange-100 to-yellow-100 rounded-full flex items-center justify-center animate-bounce">
				<svg class="w-20 h-20 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" 
						d="M5 13l4 4L19 7" />
				</svg>
			</div>
		</div>
		
		<!-- Title -->
		<h1 class="text-4xl font-bold text-gray-800 mb-2">
			Payment Confirmed! ✅
		</h1>
		
		<p class="text-lg text-orange-600 font-semibold mb-6">
			📴 OFFLINE MODE - Order tersimpan di perangkat
		</p>
		
		
		<!-- Order Number Box -->
		<div class="bg-gray-50 border-2 border-gray-200 rounded-xl p-4 mb-6">
			<p class="text-sm text-gray-500 mb-1">Order Number</p>
			<p class="text-2xl font-bold text-gray-800 font-mono">{orderNumber}</p>
		</div>

		<!-- Customer Info -->
		<div class="bg-blue-50 border-2 border-blue-200 rounded-xl p-4 mb-6 text-left">
			<h3 class="font-bold text-blue-800 text-lg mb-3">Customer Information</h3>
			<div class="space-y-2">
				<div class="flex justify-between">
					<span class="text-gray-600">Name:</span>
					<span class="font-semibold text-gray-800">{customerName}</span>
				</div>
				{#if customerPhone}
				<div class="flex justify-between">
					<span class="text-gray-600">Phone:</span>
					<span class="font-semibold text-gray-800">{customerPhone}</span>
				</div>
				{/if}
			</div>
		</div>
		
		<!-- Payment Details -->
		{#if totalAmount > 0}
		<div class="bg-green-50 border-2 border-green-200 rounded-xl p-6 mb-6">
			<h3 class="font-bold text-green-800 text-lg mb-4 flex items-center justify-center">
				<span class="text-2xl mr-2">💰</span>
				Payment Details
			</h3>
			<div class="space-y-3 text-left">
				<div class="flex justify-between items-center py-2 border-b border-green-200">
					<span class="text-gray-600">Method:</span>
					<span class="font-semibold text-gray-800 text-lg">{getPaymentIcon(paymentMethod)} {getPaymentName(paymentMethod)}</span>
				</div>
				<div class="flex justify-between items-center py-3 bg-green-100 rounded-lg px-4">
					<span class="text-green-700 font-semibold text-lg">Total:</span>
					<span class="font-bold text-green-700 text-2xl">{formatCurrency(totalAmount)}</span>
				</div>
				{#if paymentMethod === 'cash' && cashGiven > 0}
					<div class="flex justify-between items-center py-2 border-t border-green-200 pt-3">
						<span class="text-gray-600">Cash Given:</span>
						<span class="font-semibold text-gray-800 text-lg">{formatCurrency(cashGiven)}</span>
					</div>
					<div class="flex justify-between items-center py-3 bg-yellow-100 rounded-lg px-4">
						<span class="text-yellow-700 font-semibold text-lg">Change:</span>
						<span class="font-bold text-yellow-700 text-2xl">{formatCurrency(changeAmount)}</span>
					</div>
				{/if}
			</div>
		</div>
		{/if}
		
		<!-- Info Box -->
		<div class="bg-orange-50 border-2 border-orange-200 rounded-xl p-6 mb-6 text-left">
			<h3 class="font-bold text-orange-800 text-lg mb-3 flex items-center">
				<svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
						d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				What Happens Next:
			</h3>
			<ul class="space-y-2 text-gray-700">
				<li class="flex items-start">
					<span class="text-orange-600 mr-2 text-lg">✓</span>
					<span>Order saved to device storage</span>
				</li>
				<li class="flex items-start">
					<span class="text-orange-600 mr-2 text-lg">✓</span>
					<span>Will <strong>auto-sync to kitchen</strong> when internet returns</span>
				</li>
				<li class="flex items-start">
					<span class="text-orange-600 mr-2 text-lg">✓</span>
					<span>You'll receive notification when order is sent successfully</span>
				</li>
			</ul>
		</div>
		
		<!-- Sync Status -->
		{#if $syncProgress.isRunning}
			<div class="bg-blue-50 border-2 border-blue-200 rounded-xl p-4 mb-6">
				<div class="flex items-center justify-center mb-2">
					<svg class="animate-spin h-5 w-5 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					<span class="text-blue-800 font-semibold">Trying to send order...</span>
				</div>
				<p class="text-sm text-blue-600">
					{$syncProgress.processedItems} / {$syncProgress.totalItems} orders sent
				</p>
			</div>
		{/if}
		
		<!-- Countdown -->
		<div class="mb-6">
			<p class="text-gray-500 mb-4">
				Returning to menu in <span class="font-bold text-3xl text-orange-600">{countdown}</span> seconds
			</p>
			<div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
				<div 
					class="bg-gradient-to-r from-orange-500 to-yellow-500 h-full transition-all duration-1000" 
					style="width: {((15 - countdown) / 15) * 100}%"
				></div>
			</div>
		</div>
		
		<!-- Action Button -->
		<button
			on:click={goBackNow}
			class="w-full bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white font-bold py-4 px-8 rounded-xl text-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
		>
			🏠 Back to Menu Now
		</button>
		
		<!-- Support Info -->
		<p class="text-sm text-gray-400 mt-6">
			Need help? Please contact our staff
		</p>
	</div>
</div>
