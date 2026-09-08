<script lang="ts">
	import type { SiteSettings } from '$lib/api/types';
	import TavernMark from './TavernMark.svelte';
	import { SOCIAL_ICONS } from './socialIcons';
	let { footer, siteTitle }: { footer: SiteSettings['footer']; siteTitle: string } = $props();
</script>

<footer class="site-footer">
	<div class="footer-inner">
		<div class="footer-top">
			<div class="footer-brand"><TavernMark /><span>{siteTitle}</span></div>
			{#if footer.social.length}
				<nav class="footer-social" aria-label="Social">
					{#each footer.social as { network, url } (network)}
						<!-- eslint-disable svelte/no-navigation-without-resolve -- CMS-managed link -->
						<a href={url} target="_blank" rel="noopener" aria-label={SOCIAL_ICONS[network].label}>
							<svg viewBox="0 0 24 24" aria-hidden="true">
								<path fill="currentColor" d={SOCIAL_ICONS[network].path} />
							</svg>
						</a>
						<!-- eslint-enable svelte/no-navigation-without-resolve -->
					{/each}
				</nav>
			{/if}
		</div>
		<div class="footer-grid">
			<!-- eslint-disable-next-line svelte/no-at-html-tags -->
			<div class="prose prose-sm max-w-lg">{@html footer.text}</div>
			{#if footer.links.length}
				<nav class="footer-links" aria-label="Footer">
					{#each footer.links as link (link.href + link.label)}
						<!-- eslint-disable svelte/no-navigation-without-resolve -- CMS-managed link -->
						<a
							href={link.href}
							target={link.external ? '_blank' : undefined}
							rel={link.external ? 'noopener' : undefined}>{link.label}</a
						>
						<!-- eslint-enable svelte/no-navigation-without-resolve -->
					{/each}
				</nav>
			{/if}
		</div>
		{#if footer.copyright}<p class="footer-copyright">{footer.copyright}</p>{/if}
	</div>
</footer>
