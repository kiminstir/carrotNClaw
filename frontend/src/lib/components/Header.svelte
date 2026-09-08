<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import type { SiteSettings } from '$lib/api/types';
	import Picture from './Picture.svelte';
	import TavernMark from './TavernMark.svelte';
	import OpenBadge from './OpenBadge.svelte';

	let { header, hours }: { header: SiteSettings['header']; hours: SiteSettings['hours'] } =
		$props();
	let open = $state(false);

	const isCurrent = (href: string) =>
		page.url.pathname.replace(/\/$/, '') === href.replace(/\/$/, '');
</script>

<svelte:window
	onkeydown={(event) => {
		if (event.key === 'Escape' && open) {
			open = false;
			document.querySelector<HTMLButtonElement>('.menu-toggle')?.focus();
		}
	}}
/>

<header class="site-header">
	<div class="header-inner">
		<a href={resolve('/')} class="brand" onclick={() => (open = false)}>
			{#if header.logo}
				<Picture
					image={header.logo}
					sizes="48px"
					class="h-12 w-12 rounded-full object-cover"
					priority
				/>
			{:else}
				<span class="brand-mark"><TavernMark /></span>
			{/if}
			<span>{header.site_title}</span>
		</a>

		<div class="header-end">
			<nav class="desktop-nav" aria-label="Main">
				{#each header.menu as link (link.href + link.label)}
					<!-- eslint-disable svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
					<a
						href={link.href}
						target={link.external ? '_blank' : undefined}
						rel={link.external ? 'noopener' : undefined}
						aria-current={isCurrent(link.href) ? 'page' : undefined}
						class="nav-link"
					>
						{link.label}
					</a>
					<!-- eslint-enable svelte/no-navigation-without-resolve -->
				{/each}
			</nav>

			<div class="desktop-badge"><OpenBadge {hours} /></div>

			<button
				class="menu-toggle"
				aria-expanded={open}
				aria-controls="mobile-nav"
				onclick={() => (open = !open)}
			>
				<span class="sr-only">Toggle menu</span>
				<svg
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					{#if open}<path d="M6 6l12 12M18 6L6 18" />{:else}<path
							d="M4 7h16M4 12h16M4 17h16"
						/>{/if}
				</svg>
			</button>
		</div>
	</div>

	{#if open}
		<nav id="mobile-nav" class="mobile-nav" aria-label="Main">
			<div class="mobile-badge"><OpenBadge {hours} /></div>
			{#each header.menu as link (link.href + link.label)}
				<!-- eslint-disable svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
				<a
					href={link.href}
					class="nav-link"
					aria-current={isCurrent(link.href) ? 'page' : undefined}
					target={link.external ? '_blank' : undefined}
					rel={link.external ? 'noopener' : undefined}
					onclick={() => (open = false)}>{link.label}</a
				>
				<!-- eslint-enable svelte/no-navigation-without-resolve -->
			{/each}
		</nav>
	{/if}
</header>
