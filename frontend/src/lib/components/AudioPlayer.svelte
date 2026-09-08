<script lang="ts">
	import { onMount, tick } from 'svelte';
	import type { SiteSettings } from '$lib/api/types';

	let { music }: { music: SiteSettings['music'] } = $props();

	let audio: HTMLAudioElement | undefined = $state();
	let index = $state(0);
	let playing = $state(false);
	let muted = $state(false);
	let consecutiveErrors = $state(0);

	const track = $derived(music.tracks[index]);
	const STORAGE_KEY = 'cc-muted';

	onMount(() => {
		try {
			muted = localStorage.getItem(STORAGE_KEY) === '1';
		} catch {
			/* storage unavailable */
		}
	});

	$effect(() => {
		if (audio) audio.volume = Math.min(1, Math.max(0, music.volume / 100));
	});

	async function play() {
		if (!audio) return;
		try {
			await audio.play();
			playing = true;
			consecutiveErrors = 0;
		} catch {
			playing = false; // autoplay blocked until the user interacts
		}
	}

	function handleError() {
		consecutiveErrors += 1;
		if (consecutiveErrors >= music.tracks.length) {
			// Every track in the playlist has now failed in a row - stop
			// instead of skipping forever.
			playing = false;
			return;
		}
		skip(1);
	}

	function toggle() {
		if (!audio) return;
		if (audio.paused) play();
		else {
			audio.pause();
			playing = false;
		}
	}

	async function skip(delta: number) {
		const wasPlaying = playing;
		index = (index + delta + music.tracks.length) % music.tracks.length;
		await tick();
		if (wasPlaying) play();
	}

	function toggleMute() {
		muted = !muted;
		try {
			localStorage.setItem(STORAGE_KEY, muted ? '1' : '0');
		} catch {
			/* ignore */
		}
	}
</script>

<audio
	bind:this={audio}
	src={track.src}
	{muted}
	preload="none"
	onended={() => skip(1)}
	onerror={handleError}
></audio>

<div
	data-testid="audio-player"
	class="fixed right-4 bottom-4 z-50 flex items-center gap-2 rounded-full border border-white/10 bg-surface-2/95 px-3 py-2 shadow-lg backdrop-blur"
>
	<button
		onclick={() => skip(-1)}
		aria-label="Previous track"
		class="px-1 text-muted hover:text-ink">‹</button
	>
	<button
		onclick={toggle}
		aria-label={playing ? 'Pause music' : 'Play music'}
		class="rounded-full bg-accent px-3 py-1 font-semibold text-surface"
	>
		{playing ? '❚❚' : '▶'}
	</button>
	<button onclick={() => skip(1)} aria-label="Next track" class="px-1 text-muted hover:text-ink"
		>›</button
	>
	<span class="max-w-40 truncate text-sm text-muted" title={track.title}>{track.title}</span>
	<button
		onclick={toggleMute}
		aria-pressed={muted}
		aria-label="Mute"
		class="px-1 text-muted hover:text-ink"
	>
		{muted ? '🔇' : '🔊'}
	</button>
</div>
