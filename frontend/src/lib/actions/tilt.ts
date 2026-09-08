/**
 * Writes the cursor's offset from the element's centre to `--tilt-x` / `--tilt-y` (each -1..1)
 * so decorative layers can lean toward the pointer. Only active for a fine pointer that can
 * hover, and never under reduced motion; touch devices get nothing to run.
 */
export interface Box {
	left: number;
	top: number;
	width: number;
	height: number;
}

export function tiltOffset(clientX: number, clientY: number, box: Box): { x: number; y: number } {
	const unit = (value: number, start: number, size: number) => {
		if (size <= 0) return 0;
		const normalized = ((value - start) / size) * 2 - 1;
		return Math.round(Math.min(1, Math.max(-1, normalized)) * 100) / 100;
	};
	return { x: unit(clientX, box.left, box.width), y: unit(clientY, box.top, box.height) };
}

export function tilt(node: HTMLElement) {
	const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
	const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	if (!fine || reduce) return;

	let frame = 0;
	let pending: { x: number; y: number } | null = null;

	const apply = () => {
		frame = 0;
		if (!pending) return;
		node.style.setProperty('--tilt-x', String(pending.x));
		node.style.setProperty('--tilt-y', String(pending.y));
		pending = null;
	};
	const schedule = (offset: { x: number; y: number }) => {
		pending = offset;
		if (!frame) frame = requestAnimationFrame(apply);
	};
	const onMove = (event: PointerEvent) => {
		schedule(tiltOffset(event.clientX, event.clientY, node.getBoundingClientRect()));
	};
	const onLeave = () => schedule({ x: 0, y: 0 });

	node.addEventListener('pointermove', onMove, { passive: true });
	node.addEventListener('pointerleave', onLeave);
	return {
		destroy() {
			node.removeEventListener('pointermove', onMove);
			node.removeEventListener('pointerleave', onLeave);
			if (frame) cancelAnimationFrame(frame);
		}
	};
}
