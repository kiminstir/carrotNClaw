<script lang="ts">
	import { page } from '$app/state';
</script>

<section class="mx-auto max-w-3xl px-4 py-24 text-center">
	<h1 class="font-display text-5xl">{page.status}</h1>
	<p class="mt-4 text-muted">{page.error?.message ?? 'Something went wrong.'}</p>
	<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- static home link -->
	<a href="/" class="mt-8 inline-block text-accent underline">Back to the tavern</a>
</section>
