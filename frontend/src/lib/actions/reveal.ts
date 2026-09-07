export function reveal(node: HTMLElement, options: { threshold?: number } = {}) {
	const { threshold = 0.15 } = options;
	const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	if (reduce || !('IntersectionObserver' in window)) {
		node.classList.add('is-visible');
		return;
	}
	node.classList.add('reveal');
	const observer = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (entry.isIntersecting) {
					node.classList.add('is-visible');
					observer.disconnect();
				}
			}
		},
		{ threshold }
	);
	observer.observe(node);
	return { destroy: () => observer.disconnect() };
}
