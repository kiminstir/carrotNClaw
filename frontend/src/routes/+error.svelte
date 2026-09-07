<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
</script>

<section class="mx-auto max-w-3xl px-4 py-24 text-center">
	<h1 class="font-display text-5xl">{page.status}</h1>
	<p class="mt-4 text-muted">{page.error?.message ?? 'Something went wrong.'}</p>
	<a href={resolve('/')} class="mt-8 inline-block text-accent underline">Back to the tavern</a>
</section>
