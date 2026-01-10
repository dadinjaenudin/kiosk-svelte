<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { kioskConfig } from '$lib/stores/kioskStore';
	import { browser } from '$app/environment';
	
	let currentSlide = 0;
	let autoSlideInterval: number;
	
	// Admin reset hotkey (press "R" 5 times within 2 seconds)
	let resetKeyCount = 0;
	let resetKeyTimeout: number;
	
	// Promotional carousel items
	const promoSlides = [
		{
			title: "Welcome to Our Store!",
			description: "Order from multiple brands in one transaction",
			icon: "🛍️"
		},
		{
			title: "Fast & Easy Ordering",
			description: "Browse, select, and checkout in minutes",
			icon: "⚡"
		},
		{
			title: "Multiple Payment Options",
			description: "Cash, Card, QRIS, E-Wallet supported",
			icon: "💳"
		},
		{
			title: "Fresh & Quality Food",
			description: "Made to order by our expert chefs",
			icon: "🍽️"
		}
	];
	
	onMount(() => {
		// Auto-rotate carousel every 4 seconds
		autoSlideInterval = setInterval(() => {
			currentSlide = (currentSlide + 1) % promoSlides.length;
		}, 4000);
		
		// Add keyboard listener for admin reset hotkey
		const handleKeyPress = (e: KeyboardEvent) => {
			if (e.key === 'r' || e.key === 'R') {
				resetKeyCount++;
				console.log(`🔑 Reset key pressed (${resetKeyCount}/5)`);
				
				// Clear existing timeout
				if (resetKeyTimeout) clearTimeout(resetKeyTimeout);
				
				// Reset counter after 2 seconds
				resetKeyTimeout = setTimeout(() => {
					resetKeyCount = 0;
				}, 2000);
				
				// If pressed 5 times, reset configuration
				if (resetKeyCount >= 5) {
					resetConfiguration();
				}
			}
		};
		
		window.addEventListener('keydown', handleKeyPress);
		
		return () => {
			if (autoSlideInterval) clearInterval(autoSlideInterval);
			if (resetKeyTimeout) clearTimeout(resetKeyTimeout);
			window.removeEventListener('keydown', handleKeyPress);
		};
	});
	
	function resetConfiguration() {
		if (confirm('⚠️ Reset kiosk configuration?\n\nThis will clear:\n- Store settings\n- Offline mode\n- All preferences\n\nYou will return to setup page.')) {
			console.log('🔄 Resetting kiosk configuration...');
			if (browser) {
				localStorage.removeItem('kiosk_config');
				localStorage.removeItem('offline_mode');
				console.log('✅ Configuration cleared');
			}
			kioskConfig.reset();
			window.location.href = '/kiosk';
		} else {
			resetKeyCount = 0; // Reset counter if cancelled
		}
	}
	
	function startOrder() {
		goto('/kiosk/products');
	}
	
	function goToSlide(index: number) {
		currentSlide = index;
	}
</script>

<div class="idle-screen">
	<div class="idle-container">
		<!-- Store Header -->
		<div class="store-header">
			<h1 class="store-name">{$kioskConfig.storeName || 'Welcome'}</h1>
			{#if $kioskConfig.tenantName}
				<p class="tenant-name">{$kioskConfig.tenantName}</p>
			{/if}
		</div>
		
		<!-- Main CTA -->
		<div class="main-cta">
			<div class="cta-icon">👋</div>
			<h2 class="cta-title">Welcome!</h2>
			<p class="cta-subtitle">Tap anywhere to start your order</p>
		</div>
		
		<!-- Promotional Carousel -->
		<div class="promo-carousel">
			<div class="carousel-container">
				{#each promoSlides as slide, index}
					<div 
						class="carousel-slide" 
						class:active={currentSlide === index}
					>
						<div class="slide-icon">{slide.icon}</div>
						<h3 class="slide-title">{slide.title}</h3>
						<p class="slide-description">{slide.description}</p>
					</div>
				{/each}
			</div>
			
			<!-- Carousel Indicators -->
			<div class="carousel-indicators">
				{#each promoSlides as _, index}
					<button
						class="indicator"
						class:active={currentSlide === index}
						on:click={() => goToSlide(index)}
						aria-label="Go to slide {index + 1}"
					/>
				{/each}
			</div>
		</div>
		
		<!-- Start Button -->
		<button class="start-button" on:click={startOrder}>
			<span class="button-text">Tap to Start Order</span>
			<span class="button-icon">→</span>
		</button>
		
		<!-- Features -->
		<div class="features">
			<div class="feature">
				<div class="feature-icon">🏪</div>
				<p class="feature-text">Multiple Brands</p>
			</div>
			<div class="feature">
				<div class="feature-icon">🛒</div>
				<p class="feature-text">One Cart</p>
			</div>
			<div class="feature">
				<div class="feature-icon">💰</div>
				<p class="feature-text">Single Payment</p>
			</div>
		</div>
	</div>
	
	<!-- Reset Configuration Button (Admin) -->
	<button class="reset-config-button" on:click={resetConfiguration} title="Reset Configuration">
		⚙️ Reset
	</button>
	
	<!-- Full-screen tap area -->
	<button class="tap-overlay" on:click={startOrder} aria-label="Start order">
		<span class="sr-only">Tap to start</span>
	</button>
</div>

<style>
	.idle-screen {
		min-height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		position: relative;
		overflow: hidden;
	}
	
	.idle-screen::before {
		content: '';
		position: absolute;
		top: -50%;
		right: -50%;
		width: 200%;
		height: 200%;
		background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
		animation: pulse 4s ease-in-out infinite;
	}
	
	@keyframes pulse {
		0%, 100% { transform: scale(1); opacity: 0.5; }
		50% { transform: scale(1.1); opacity: 0.8; }
	}
	
	.idle-container {
		position: relative;
		z-index: 2;
		max-width: 1200px;
		width: 100%;
		text-align: center;
		color: white;
	}
	
	/* Store Header */
	.store-header {
		margin-bottom: 3rem;
		animation: fadeInDown 0.8s ease-out;
	}
	
	.store-name {
		font-size: 3rem;
		font-weight: 800;
		margin-bottom: 0.5rem;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
	}
	
	.tenant-name {
		font-size: 1.5rem;
		opacity: 0.9;
		font-weight: 300;
	}
	
	/* Main CTA */
	.main-cta {
		margin-bottom: 3rem;
		animation: fadeInUp 0.8s ease-out 0.2s both;
	}
	
	.cta-icon {
		font-size: 5rem;
		margin-bottom: 1rem;
		animation: wave 2s ease-in-out infinite;
	}
	
	@keyframes wave {
		0%, 100% { transform: rotate(0deg); }
		25% { transform: rotate(20deg); }
		75% { transform: rotate(-20deg); }
	}
	
	.cta-title {
		font-size: 3.5rem;
		font-weight: 800;
		margin-bottom: 1rem;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
	}
	
	.cta-subtitle {
		font-size: 1.5rem;
		opacity: 0.9;
		animation: blink 2s ease-in-out infinite;
	}
	
	@keyframes blink {
		0%, 100% { opacity: 0.9; }
		50% { opacity: 0.5; }
	}
	
	/* Promotional Carousel */
	.promo-carousel {
		margin: 4rem 0;
		animation: fadeInUp 0.8s ease-out 0.4s both;
	}
	
	.carousel-container {
		position: relative;
		height: 250px;
		margin-bottom: 2rem;
	}
	
	.carousel-slide {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		opacity: 0;
		transform: translateY(20px);
		transition: all 0.6s ease-in-out;
		pointer-events: none;
	}
	
	.carousel-slide.active {
		opacity: 1;
		transform: translateY(0);
		pointer-events: auto;
	}
	
	.slide-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
	}
	
	.slide-title {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: 1rem;
	}
	
	.slide-description {
		font-size: 1.25rem;
		opacity: 0.9;
		max-width: 600px;
		margin: 0 auto;
	}
	
	/* Carousel Indicators */
	.carousel-indicators {
		display: flex;
		gap: 1rem;
		justify-content: center;
		align-items: center;
	}
	
	.indicator {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: rgba(255,255,255,0.3);
		border: none;
		cursor: pointer;
		transition: all 0.3s ease;
		padding: 0;
	}
	
	.indicator:hover {
		background: rgba(255,255,255,0.5);
		transform: scale(1.2);
	}
	
	.indicator.active {
		background: white;
		width: 32px;
		border-radius: 6px;
	}
	
	/* Start Button */
	.start-button {
		display: inline-flex;
		align-items: center;
		gap: 1rem;
		padding: 1.5rem 3rem;
		font-size: 1.5rem;
		font-weight: 700;
		background: white;
		color: #667eea;
		border: none;
		border-radius: 9999px;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 10px 30px rgba(0,0,0,0.3);
		animation: fadeInUp 0.8s ease-out 0.6s both;
		z-index: 10;
		position: relative;
	}
	
	.start-button:hover {
		transform: translateY(-4px);
		box-shadow: 0 15px 40px rgba(0,0,0,0.4);
	}
	
	.start-button:active {
		transform: translateY(-2px);
	}
	
	.button-icon {
		font-size: 2rem;
		transition: transform 0.3s ease;
	}
	
	.start-button:hover .button-icon {
		transform: translateX(8px);
	}
	
	/* Features */
	.features {
		display: flex;
		gap: 3rem;
		justify-content: center;
		margin-top: 4rem;
		animation: fadeInUp 0.8s ease-out 0.8s both;
	}
	
	.feature {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}
	
	.feature-icon {
		font-size: 2.5rem;
		margin-bottom: 0.5rem;
	}
	
	.feature-text {
		font-size: 1rem;
		opacity: 0.9;
		font-weight: 500;
	}
	
	/* Tap Overlay */
	.tap-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: transparent;
		border: none;
		cursor: pointer;
		z-index: 1;
		pointer-events: auto;
	}
	
	/* Allow clicks through tap-overlay for specific elements */
	.reset-config-button {
		pointer-events: auto;
	}
	
	/* Reset Configuration Button */
	.reset-config-button {
		position: absolute;
		top: 1rem;
		right: 1rem;
		background: rgba(255, 255, 255, 0.15);
		backdrop-filter: blur(10px);
		border: 2px solid rgba(255, 255, 255, 0.3);
		color: white;
		padding: 0.75rem 1.5rem;
		border-radius: 12px;
		font-size: 0.95rem;
		font-weight: 600;
		cursor: pointer;
		z-index: 100;
		transition: all 0.3s ease;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}
	
	.reset-config-button:hover {
		background: rgba(239, 68, 68, 0.9);
		border-color: rgba(255, 255, 255, 0.5);
		transform: translateY(-2px);
		box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
	}
	
	.reset-config-button:active {
		transform: translateY(0);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	}
	
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border-width: 0;
	}
	
	/* Animations */
	@keyframes fadeInDown {
		from {
			opacity: 0;
			transform: translateY(-30px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	
	@keyframes fadeInUp {
		from {
			opacity: 0;
			transform: translateY(30px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	
	/* Responsive */
	@media (max-width: 768px) {
		.idle-screen {
			padding: 1rem;
		}
		
		.store-name {
			font-size: 2rem;
		}
		
		.tenant-name {
			font-size: 1.25rem;
		}
		
		.cta-icon {
			font-size: 3.5rem;
		}
		
		.cta-title {
			font-size: 2.5rem;
		}
		
		.cta-subtitle {
			font-size: 1.25rem;
		}
		
		.carousel-container {
			height: 200px;
		}
		
		.slide-icon {
			font-size: 3rem;
		}
		
		.slide-title {
			font-size: 1.5rem;
		}
		
		.slide-description {
			font-size: 1rem;
		}
		
		.start-button {
			padding: 1.25rem 2.5rem;
			font-size: 1.25rem;
		}
		
		.features {
			gap: 1.5rem;
			flex-wrap: wrap;
		}
		
		.feature-icon {
			font-size: 2rem;
		}
		
		.feature-text {
			font-size: 0.875rem;
		}
	}
</style>
