<script lang="ts">
	import { onMount } from 'svelte';
	import type { SiteSettings } from '$lib/api/types';
	import { openingLabel, openingState } from '$lib/hours';

	// Open / closed pill for the header. The schedule comes from the CMS in UTC (server time);
	// the state is worked out here and re-checked every minute so the badge flips on its own.
	let { hours }: { hours: SiteSettings['hours'] } = $props();
	let now = $state(new Date());
	const status = $derived(hours.enabled ? openingState(hours.slots, now) : null);

	onMount(() => {
		const timer = setInterval(() => (now = new Date()), 60_000);
		return () => clearInterval(timer);
	});
</script>

{#if status}
	<span class="open-badge" class:is-open={status.open} role="status">
		<span class="open-dot" aria-hidden="true"></span>
		{openingLabel(status, now)}
	</span>
{/if}
