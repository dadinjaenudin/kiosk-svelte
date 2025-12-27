<script>
	import { createEventDispatcher, onMount } from 'svelte';
	
	export let product = null;
	export let show = false;
	
	const dispatch = createEventDispatcher();
	
	let selectedModifiers = [];
	let specialInstructions = '';
	let quantity = 1;
	
	$: totalPrice = product ? calculateTotalPrice() : 0;
	$: groupedModifiers = product?.modifiers ? groupModifiersByType(product.modifiers) : {};
	
	onMount(() => {
		console.log('🎨 ModifierModal mounted');
		console.log('📦 Product:', product?.name);
		console.log('🔧 Modifiers available:', product?.modifiers?.length || 0);
	});
	
	function groupModifiersByType(modifiers) {
		const groups = {};
		modifiers.forEach(mod => {
			if (!groups[mod.type]) {
				groups[mod.type] = [];
			}
			groups[mod.type].push(mod);
		});
		return groups;
	}
	
	function getTypeLabel(type) {
		const labels = {
			'size': '📏 Ukuran Porsi',
			'topping': '🧀 Topping',
			'spicy': '🌶️ Level Pedas',
			'extra': '➕ Tambahan',
			'sauce': '🥫 Pilihan Kuah'
		};
		return labels[type] || type;
	}
	
	function isModifierSelected(modifierId) {
		return selectedModifiers.some(m => m.id === modifierId);
	}
	
	function toggleModifier(modifier, type) {
		// For size and sauce, only one can be selected (radio behavior)
		if (type === 'size' || type === 'sauce') {
			selectedModifiers = selectedModifiers.filter(m => m.type !== type);
			if (!isModifierSelected(modifier.id)) {
				selectedModifiers = [...selectedModifiers, modifier];
			}
		} 
		// For spicy level, only one level (radio behavior)
		else if (type === 'spicy') {
			selectedModifiers = selectedModifiers.filter(m => m.type !== 'spicy');
			selectedModifiers = [...selectedModifiers, modifier];
		}
		// For toppings and extras, multiple can be selected (checkbox behavior)
		else {
			if (isModifierSelected(modifier.id)) {
				selectedModifiers = selectedModifiers.filter(m => m.id !== modifier.id);
			} else {
				selectedModifiers = [...selectedModifiers, modifier];
			}
		}
	}
	
	function calculateTotalPrice() {
		if (!product) return 0;
		
		let base = parseFloat(product.price);
		let modifiersTotal = selectedModifiers.reduce((sum, mod) => {
			return sum + parseFloat(mod.price_adjustment);
		}, 0);
		
		return (base + modifiersTotal) * quantity;
	}
	
	function formatCurrency(amount) {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
	
	function handleAddToCart() {
		console.log('🛒 ModifierModal: Adding to cart', {
			product: product?.name,
			quantity,
			modifiers: selectedModifiers.length,
			notes: specialInstructions
		});
		
		dispatch('addToCart', {
			product,
			quantity,
			modifiers: selectedModifiers,
			notes: specialInstructions
		});
		handleClose();
	}
	
	function handleClose() {
		selectedModifiers = [];
		specialInstructions = '';
		quantity = 1;
		dispatch('close');
	}
	
	function incrementQuantity() {
		quantity += 1;
	}
	
	function decrementQuantity() {
		if (quantity > 1) {
			quantity -= 1;
		}
	}
</script>

{#if show && product}
	<div class="modal-overlay" on:click={handleClose}>
		<div class="modal-content" on:click|stopPropagation>
			<!-- Header -->
			<div class="modal-header">
				<div class="product-info">
					<h2>{product.name}</h2>
					<p class="base-price">{formatCurrency(product.price)}</p>
				</div>
				<button class="close-btn" on:click={handleClose}>✕</button>
			</div>
			
			<!-- Modifiers -->
			<div class="modal-body">
				{#if Object.keys(groupedModifiers).length > 0}
					{#each Object.entries(groupedModifiers) as [type, modifiers]}
						<div class="modifier-group">
							<h3>{getTypeLabel(type)}</h3>
							<div class="modifiers-list">
								{#each modifiers as modifier}
									<button
										class="modifier-option"
										class:selected={isModifierSelected(modifier.id)}
										on:click={() => toggleModifier(modifier, type)}
									>
										<span class="modifier-name">{modifier.name}</span>
										<span class="modifier-price">
											{#if modifier.price_adjustment > 0}
												+{formatCurrency(modifier.price_adjustment)}
											{:else if modifier.price_adjustment < 0}
												{formatCurrency(modifier.price_adjustment)}
											{:else}
												<span class="free-badge">Gratis</span>
											{/if}
										</span>
										{#if isModifierSelected(modifier.id)}
											<span class="check-icon">✓</span>
										{/if}
									</button>
								{/each}
							</div>
						</div>
					{/each}
				{:else}
					<div class="no-modifiers">
						<p>Produk ini tidak memiliki pilihan kustomisasi</p>
					</div>
				{/if}
				
				<!-- Special Instructions -->
				<div class="modifier-group">
					<h3>📝 Catatan Khusus (Opsional)</h3>
					<textarea
						bind:value={specialInstructions}
						placeholder="Contoh: Tidak pakai kecap, tambah banyak sambal, dll"
						rows="3"
						class="special-instructions"
					/>
				</div>
			</div>
			
			<!-- Footer -->
			<div class="modal-footer">
				<div class="quantity-selector">
					<button class="qty-btn" on:click={decrementQuantity} disabled={quantity <= 1}>−</button>
					<span class="qty-display">{quantity}</span>
					<button class="qty-btn" on:click={incrementQuantity}>+</button>
				</div>
				
				<button class="add-to-cart-btn" on:click={() => {
					console.log('🔵 Button clicked in ModifierModal');
					handleAddToCart();
				}}>
					<span>Tambah ke Keranjang</span>
					<span class="total-price">{formatCurrency(totalPrice)}</span>
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 2000;
		padding: 20px;
		animation: fadeIn 0.2s;
	}
	
	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}
	
	.modal-content {
		background: white;
		border-radius: 20px;
		max-width: 600px;
		width: 100%;
		max-height: 90vh;
		display: flex;
		flex-direction: column;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: slideUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	}
	
	@keyframes slideUp {
		from {
			transform: translateY(30px);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}
	
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		padding: 24px;
		border-bottom: 2px solid #E5E7EB;
	}
	
	.product-info h2 {
		font-size: 24px;
		font-weight: 800;
		color: #1F2937;
		margin: 0 0 8px 0;
	}
	
	.base-price {
		font-size: 18px;
		font-weight: 600;
		color: #10B981;
		margin: 0;
	}
	
	.close-btn {
		background: #F3F4F6;
		border: none;
		width: 40px;
		height: 40px;
		border-radius: 50%;
		font-size: 24px;
		color: #6B7280;
		cursor: pointer;
		transition: all 0.2s;
		flex-shrink: 0;
	}
	
	.close-btn:hover {
		background: #E5E7EB;
		transform: rotate(90deg);
	}
	
	.modal-body {
		flex: 1;
		overflow-y: auto;
		padding: 24px;
	}
	
	.modifier-group {
		margin-bottom: 24px;
	}
	
	.modifier-group:last-child {
		margin-bottom: 0;
	}
	
	.modifier-group h3 {
		font-size: 16px;
		font-weight: 700;
		color: #374151;
		margin: 0 0 12px 0;
	}
	
	.modifiers-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	
	.modifier-option {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16px;
		background: #F9FAFB;
		border: 2px solid #E5E7EB;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.2s;
		text-align: left;
	}
	
	.modifier-option:hover {
		border-color: #10B981;
		background: #F0FDF4;
	}
	
	.modifier-option.selected {
		border-color: #10B981;
		background: #D1FAE5;
		border-width: 3px;
	}
	
	.modifier-name {
		font-size: 15px;
		font-weight: 600;
		color: #1F2937;
		flex: 1;
	}
	
	.modifier-price {
		font-size: 14px;
		font-weight: 700;
		color: #059669;
		margin-right: 8px;
	}
	
	.free-badge {
		background: #DBEAFE;
		color: #1E40AF;
		padding: 4px 8px;
		border-radius: 6px;
		font-size: 12px;
		font-weight: 700;
	}
	
	.check-icon {
		position: absolute;
		top: 8px;
		right: 8px;
		background: #10B981;
		color: white;
		width: 24px;
		height: 24px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 14px;
		font-weight: 700;
	}
	
	.no-modifiers {
		text-align: center;
		padding: 40px 20px;
		color: #9CA3AF;
	}
	
	.special-instructions {
		width: 100%;
		padding: 12px;
		border: 2px solid #E5E7EB;
		border-radius: 12px;
		font-size: 14px;
		font-family: inherit;
		resize: vertical;
		transition: border-color 0.2s;
	}
	
	.special-instructions:focus {
		outline: none;
		border-color: #10B981;
	}
	
	.modal-footer {
		padding: 24px;
		border-top: 2px solid #E5E7EB;
		display: flex;
		gap: 16px;
		align-items: center;
	}
	
	.quantity-selector {
		display: flex;
		align-items: center;
		gap: 12px;
		background: #F3F4F6;
		padding: 8px;
		border-radius: 12px;
	}
	
	.qty-btn {
		background: white;
		border: 2px solid #E5E7EB;
		width: 40px;
		height: 40px;
		border-radius: 10px;
		font-size: 20px;
		font-weight: 700;
		color: #374151;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.qty-btn:hover:not(:disabled) {
		border-color: #10B981;
		color: #10B981;
	}
	
	.qty-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	
	.qty-display {
		font-size: 20px;
		font-weight: 700;
		color: #1F2937;
		min-width: 32px;
		text-align: center;
	}
	
	.add-to-cart-btn {
		flex: 1;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16px 20px;
		background: linear-gradient(135deg, #10B981 0%, #059669 100%);
		border: none;
		border-radius: 12px;
		font-size: 16px;
		font-weight: 700;
		color: white;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.add-to-cart-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
	}
	
	.total-price {
		font-size: 18px;
	}
	
	@media (max-width: 640px) {
		.modal-content {
			max-height: 95vh;
		}
		
		.modal-footer {
			flex-direction: column;
		}
		
		.quantity-selector {
			width: 100%;
			justify-content: center;
		}
		
		.add-to-cart-btn {
			width: 100%;
		}
	}
</style>
