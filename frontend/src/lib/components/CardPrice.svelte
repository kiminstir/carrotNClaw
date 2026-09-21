<script lang="ts">
	import { formatGilAmount } from '$lib/blocks/cards';

	let { value }: { value: string } = $props();
	const amount = $derived(formatGilAmount(value));
</script>

{#if amount}
	<span class="card-price" aria-label={`${amount} Gil`}>
		<span class="card-price-amount" aria-hidden="true">{amount}</span>
		<span class="card-price-currency" aria-hidden="true">Gil</span>
	</span>
{/if}
