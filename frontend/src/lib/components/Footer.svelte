<script lang="ts">
	import type { SiteSettings } from '$lib/api/types';

	let { footer }: { footer: SiteSettings['footer'] } = $props();
</script>

<footer class="border-t border-white/10 bg-surface-2">
	<div class="mx-auto grid max-w-6xl gap-6 px-4 py-10 md:grid-cols-2">
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		<div class="prose prose-sm max-w-none prose-invert">{@html footer.text}</div>
		<div class="flex flex-col gap-2 md:items-end">
			{#each footer.links as link (link.href + link.label)}
				<!-- eslint-disable svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
				<a
					href={link.href}
					class="text-muted hover:text-accent"
					target={link.external ? '_blank' : undefined}
					rel={link.external ? 'noopener' : undefined}
				>
					{link.label}
				</a>
				<!-- eslint-enable svelte/no-navigation-without-resolve -->
			{/each}
			{#if footer.copyright}<p class="mt-4 text-sm text-muted">{footer.copyright}</p>{/if}
		</div>
	</div>
</footer>
