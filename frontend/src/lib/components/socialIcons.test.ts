import { describe, expect, it } from 'vitest';
import type { SocialNetwork } from '$lib/api/types';
import { SOCIAL_ICONS } from './socialIcons';

const NETWORKS: SocialNetwork[] = ['discord', 'youtube', 'twitch'];

describe('SOCIAL_ICONS', () => {
	it('has a label and a 24px path for every network the API can return', () => {
		for (const network of NETWORKS) {
			const icon = SOCIAL_ICONS[network];
			expect(icon.label).toBeTruthy();
			expect(icon.path).toMatch(/^M/);
		}
	});
});
