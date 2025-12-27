<script>
	import { createEventDispatcher } from 'svelte';

	export let startDate = '';
	export let endDate = '';
	export let days = {
		monday: true,
		tuesday: true,
		wednesday: true,
		thursday: true,
		friday: true,
		saturday: true,
		sunday: true
	};
	export let timeStart = '';
	export let timeEnd = '';
	export let errors = {};

	const dispatch = createEventDispatcher();

	let localStartDate = startDate;
	let localEndDate = endDate;
	let localDays = { ...days };
	let localTimeStart = timeStart;
	let localTimeEnd = timeEnd;
	let enableTimeRestriction = !!(timeStart || timeEnd);

	const dayLabels = [
		{ key: 'monday', label: 'Mon' },
		{ key: 'tuesday', label: 'Tue' },
		{ key: 'wednesday', label: 'Wed' },
		{ key: 'thursday', label: 'Thu' },
		{ key: 'friday', label: 'Fri' },
		{ key: 'saturday', label: 'Sat' },
		{ key: 'sunday', label: 'Sun' }
	];

	function emitChange() {
		dispatch('change', {
			start_date: localStartDate,
			end_date: localEndDate,
			days: localDays,
			time_start: enableTimeRestriction ? localTimeStart : '',
			time_end: enableTimeRestriction ? localTimeEnd : ''
		});
	}

	function toggleAllDays() {
		const allSelected = Object.values(localDays).every((v) => v);
		Object.keys(localDays).forEach((key) => {
			localDays[key] = !allSelected;
		});
		emitChange();
	}

	function toggleWeekdays() {
		const weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
		const allWeekdaysSelected = weekdays.every((day) => localDays[day]);
		weekdays.forEach((day) => {
			localDays[day] = !allWeekdaysSelected;
		});
		emitChange();
	}

	function toggleWeekends() {
		const weekends = ['saturday', 'sunday'];
		const allWeekendsSelected = weekends.every((day) => localDays[day]);
		weekends.forEach((day) => {
			localDays[day] = !allWeekendsSelected;
		});
		emitChange();
	}
</script>

<div class="space-y-6">
	<!-- Date Range -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
		<div>
			<label class="block text-sm font-medium text-gray-700 mb-2">
				Start Date & Time <span class="text-red-500">*</span>
			</label>
			<input
				type="datetime-local"
				bind:value={localStartDate}
				on:change={emitChange}
				class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 {errors.start_date
					? 'border-red-500'
					: 'border-gray-300'}"
			/>
			{#if errors.start_date}
				<p class="mt-1 text-sm text-red-600">{errors.start_date}</p>
			{/if}
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-700 mb-2">
				End Date & Time <span class="text-red-500">*</span>
			</label>
			<input
				type="datetime-local"
				bind:value={localEndDate}
				on:change={emitChange}
				class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 {errors.end_date
					? 'border-red-500'
					: 'border-gray-300'}"
			/>
			{#if errors.end_date}
				<p class="mt-1 text-sm text-red-600">{errors.end_date}</p>
			{/if}
		</div>
	</div>

	<!-- Days of Week -->
	<div>
		<label class="block text-sm font-medium text-gray-700 mb-3"> Active Days </label>

		<!-- Quick Actions -->
		<div class="flex gap-2 mb-3">
			<button
				type="button"
				on:click={toggleAllDays}
				class="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
			>
				All Days
			</button>
			<button
				type="button"
				on:click={toggleWeekdays}
				class="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
			>
				Weekdays
			</button>
			<button
				type="button"
				on:click={toggleWeekends}
				class="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
			>
				Weekends
			</button>
		</div>

		<!-- Day Checkboxes -->
		<div class="flex flex-wrap gap-2">
			{#each dayLabels as day}
				<label
					class="flex items-center gap-2 px-4 py-2 border-2 rounded-lg cursor-pointer transition-all {localDays[
						day.key
					]
						? 'border-blue-600 bg-blue-50 text-blue-900'
						: 'border-gray-300 hover:border-gray-400'}"
				>
					<input
						type="checkbox"
						bind:checked={localDays[day.key]}
						on:change={emitChange}
						class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
					/>
					<span class="text-sm font-medium">{day.label}</span>
				</label>
			{/each}
		</div>
	</div>

	<!-- Time Restriction -->
	<div>
		<label class="flex items-center gap-2 mb-3">
			<input
				type="checkbox"
				bind:checked={enableTimeRestriction}
				on:change={emitChange}
				class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
			/>
			<span class="text-sm font-medium text-gray-700">Enable daily time restriction</span>
		</label>

		{#if enableTimeRestriction}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-blue-50 rounded-lg">
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2"> Start Time </label>
					<input
						type="time"
						bind:value={localTimeStart}
						on:change={emitChange}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
					<p class="mt-1 text-xs text-gray-500">Promotion starts at this time daily</p>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2"> End Time </label>
					<input
						type="time"
						bind:value={localTimeEnd}
						on:change={emitChange}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
					<p class="mt-1 text-xs text-gray-500">Promotion ends at this time daily</p>
				</div>
			</div>
		{/if}
	</div>

	<!-- Schedule Summary -->
	<div class="bg-gray-50 rounded-lg p-4">
		<h4 class="text-sm font-medium text-gray-700 mb-2">Schedule Summary</h4>
		<div class="text-sm text-gray-600 space-y-1">
			<p>
				<span class="font-medium">Date Range:</span>
				{#if localStartDate && localEndDate}
					{new Date(localStartDate).toLocaleString('id-ID', {
						dateStyle: 'medium',
						timeStyle: 'short'
					})}
					→
					{new Date(localEndDate).toLocaleString('id-ID', {
						dateStyle: 'medium',
						timeStyle: 'short'
					})}
				{:else}
					Not set
				{/if}
			</p>
			<p>
				<span class="font-medium">Active Days:</span>
				{Object.entries(localDays)
					.filter(([_, v]) => v)
					.map(([k]) => dayLabels.find((d) => d.key === k)?.label)
					.join(', ') || 'None selected'}
			</p>
			{#if enableTimeRestriction && (localTimeStart || localTimeEnd)}
				<p>
					<span class="font-medium">Time Range:</span>
					{localTimeStart || '00:00'} → {localTimeEnd || '23:59'}
				</p>
			{/if}
		</div>
	</div>
</div>
