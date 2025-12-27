<script>
	import { onMount, onDestroy } from 'svelte';
	import Chart from 'chart.js/auto';
	
	export let data = [];
	export let label = 'Revenue';
	export let type = 'line'; // line, bar
	
	let canvas;
	let chart;
	
	function createChart() {
		if (chart) {
			chart.destroy();
		}
		
		const ctx = canvas.getContext('2d');
		
		chart = new Chart(ctx, {
			type: type,
			data: {
				labels: data.map(d => d.label),
				datasets: [{
					label: label,
					data: data.map(d => d.value),
					backgroundColor: type === 'bar' 
						? 'rgba(59, 130, 246, 0.5)'
						: 'rgba(59, 130, 246, 0.1)',
					borderColor: 'rgba(59, 130, 246, 1)',
					borderWidth: 2,
					fill: true,
					tension: 0.4,
					pointBackgroundColor: 'rgba(59, 130, 246, 1)',
					pointBorderColor: '#fff',
					pointBorderWidth: 2,
					pointRadius: 4,
					pointHoverRadius: 6
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						display: false
					},
					tooltip: {
						backgroundColor: 'rgba(0, 0, 0, 0.8)',
						padding: 12,
						displayColors: false,
						callbacks: {
							label: function(context) {
								let value = context.parsed.y;
								return new Intl.NumberFormat('id-ID', {
									style: 'currency',
									currency: 'IDR',
									minimumFractionDigits: 0
								}).format(value);
							}
						}
					}
				},
				scales: {
					y: {
						beginAtZero: true,
						ticks: {
							callback: function(value) {
								if (value >= 1000000) {
									return (value / 1000000).toFixed(1) + 'M';
								} else if (value >= 1000) {
									return (value / 1000).toFixed(0) + 'K';
								}
								return value;
							}
						},
						grid: {
							color: 'rgba(0, 0, 0, 0.05)'
						}
					},
					x: {
						grid: {
							display: false
						}
					}
				},
				interaction: {
					intersect: false,
					mode: 'index'
				}
			}
		});
	}
	
	onMount(() => {
		if (data.length > 0) {
			createChart();
		}
	});
	
	onDestroy(() => {
		if (chart) {
			chart.destroy();
		}
	});
	
	// Re-create chart when data changes
	$: if (canvas && data.length > 0) {
		createChart();
	}
</script>

<div class="chart-container" style="position: relative; height: 300px;">
	<canvas bind:this={canvas}></canvas>
</div>

<style>
	.chart-container {
		width: 100%;
	}
</style>
