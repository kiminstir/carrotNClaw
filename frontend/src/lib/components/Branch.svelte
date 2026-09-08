<script lang="ts">
	import oak from '$lib/assets/branches/oak.svg';
	import ivy from '$lib/assets/branches/ivy.svg';
	import willow from '$lib/assets/branches/willow.svg';

	let {
		kind = 'oak',
		corner = 'top-left'
	}: {
		kind?: 'oak' | 'ivy' | 'willow';
		corner?: 'top-left' | 'top-right' | 'bottom-right' | 'bottom-left';
	} = $props();
	const artwork = { oak, ivy, willow };
</script>

<span class="botanical botanical--{corner}" aria-hidden="true">
	<img src={artwork[kind]} alt="" width="260" height="260" />
</span>

<style>
	.botanical {
		position: absolute;
		z-index: 2;
		width: var(--branch-size, 180px);
		height: var(--branch-size, 180px);
		pointer-events: none;
		user-select: none;
	}
	img {
		display: block;
		width: 100%;
		height: 100%;
	}
	.botanical--top-left {
		top: calc(var(--branch-size, 180px) * -0.2);
		left: calc(var(--branch-size, 180px) * -0.2);
	}
	.botanical--top-right {
		top: calc(var(--branch-size, 180px) * -0.2);
		right: calc(var(--branch-size, 180px) * -0.2);
		transform: rotate(90deg);
	}
	.botanical--bottom-right {
		bottom: calc(var(--branch-size, 180px) * -0.2);
		right: calc(var(--branch-size, 180px) * -0.2);
		transform: rotate(180deg);
	}
	.botanical--bottom-left {
		bottom: calc(var(--branch-size, 180px) * -0.2);
		left: calc(var(--branch-size, 180px) * -0.2);
		transform: rotate(270deg);
	}
</style>
