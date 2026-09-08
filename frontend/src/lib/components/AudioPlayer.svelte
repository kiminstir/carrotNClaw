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

<div data-testid="audio-player" class="audio-player">
	<button onclick={() => skip(-1)} aria-label="Previous track">‹</button>
	<button onclick={toggle} aria-label={playing ? 'Pause music' : 'Play music'} class="play-toggle">
		{playing ? '❚❚' : '▶'}
	</button>
	<button onclick={() => skip(1)} aria-label="Next track">›</button>
	<span class="audio-title" title={track.title}>{track.title}</span>
	<button onclick={toggleMute} aria-pressed={muted} aria-label="Mute">
		<svg
			width="19"
			height="19"
			viewBox="0 0 24 24"
			fill="none"
			stroke="currentColor"
			stroke-width="1.5"
			aria-hidden="true"
			><path d="M11 5L6 9H3V15H6L11 19Z" />{#if muted}<path
					d="M16 9L22 15M22 9L16 15"
				/>{:else}<path d="M15 8Q19 12 15 16M18 5Q25 12 18 19" />{/if}</svg
		>
	</button>
</div>
