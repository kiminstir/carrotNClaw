<script lang="ts">
	import { onMount, tick } from 'svelte';
	import type { SiteSettings } from '$lib/api/types';

	let { music }: { music: SiteSettings['music'] } = $props();

	let audio: HTMLAudioElement | undefined = $state();
	let index = $state(0);
	let playing = $state(false);
	let muted = $state(false);
	let consecutiveErrors = $state(0);
	// The sign swings once each time playback (re)starts; the class is dropped after the
	// animation so the next start can trigger it again.
	let swaying = $state(false);
	let swayTimer: ReturnType<typeof setTimeout> | undefined;

	function onPlaying() {
		playing = true;
		consecutiveErrors = 0;
		swaying = true;
		clearTimeout(swayTimer);
		swayTimer = setTimeout(() => (swaying = false), 1700);
	}

	const track = $derived(music.tracks[index]);
	const STORAGE_KEY = 'cc-muted';

	onMount(() => {
		try {
			muted = localStorage.getItem(STORAGE_KEY) === '1';
		} catch {
			/* storage unavailable */
		}
		return () => clearTimeout(swayTimer);
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
	onplaying={onPlaying}
	onpause={() => (playing = false)}
	onended={() => skip(1)}
	onerror={handleError}
></audio>

<!-- A wooden sign hanging from a wall bracket in the corner; the equalizer bars move only while
     the audio element reports it is really playing. -->
<div
	data-testid="audio-player"
	class="bard-sign"
	class:is-playing={playing}
	class:is-swaying={swaying}
>
	<span class="sign-bracket" aria-hidden="true"></span>
	<div class="sign-hanging">
		<span class="sign-chain sign-chain-left" aria-hidden="true"></span>
		<span class="sign-chain sign-chain-right" aria-hidden="true"></span>
		<div class="sign-plank">
			<button onclick={() => skip(-1)} aria-label="Previous track">
				<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
					<path d="M17 6v12L9 12z" fill="currentColor" />
					<path d="M7 6.5v11" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
				</svg>
			</button>
			<button
				onclick={toggle}
				aria-label={playing ? 'Pause music' : 'Play music'}
				class="play-toggle"
			>
				<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
					{#if playing}
						<path
							d="M8.5 6.5v11M15.5 6.5v11"
							stroke="currentColor"
							stroke-width="3"
							stroke-linecap="round"
						/>
					{:else}
						<path d="M8.5 5.5v13l10-6.5z" fill="currentColor" />
					{/if}
				</svg>
			</button>
			<button onclick={() => skip(1)} aria-label="Next track">
				<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
					<path d="M7 6v12l8-6z" fill="currentColor" />
					<path d="M17 6.5v11" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
				</svg>
			</button>
			<span class="eq" aria-hidden="true">
				<i class="eq-bar"></i><i class="eq-bar"></i><i class="eq-bar"></i><i class="eq-bar"></i>
			</span>
			<span class="audio-title" title={track.title}>{track.title}</span>
			<button onclick={toggleMute} aria-pressed={muted} aria-label="Mute">
				<svg
					width="20"
					height="20"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.6"
					stroke-linecap="round"
					stroke-linejoin="round"
					aria-hidden="true"
					><path d="M11 5L6 9H3V15H6L11 19Z" />{#if muted}<path
							d="M16 9L22 15M22 9L16 15"
						/>{:else}<path d="M15 8Q19 12 15 16M18 5Q25 12 18 19" />{/if}</svg
				>
			</button>
		</div>
	</div>
</div>
