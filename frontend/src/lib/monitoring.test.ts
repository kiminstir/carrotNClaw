import { describe, expect, it } from 'vitest';
import { sentryOptions } from './monitoring';

describe('sentryOptions', () => {
	it('is disabled without a DSN', () => {
		expect(sentryOptions({})).toBeNull();
		expect(sentryOptions({ dsn: '', environment: 'develop' })).toBeNull();
	});

	it('reports errors only, with context', () => {
		expect(
			sentryOptions({
				dsn: 'https://k@bugs.example.com/2',
				environment: 'develop',
				release: 'sha-abc1234'
			})
		).toEqual({
			dsn: 'https://k@bugs.example.com/2',
			environment: 'develop',
			release: 'sha-abc1234',
			tracesSampleRate: 0,
			sendDefaultPii: true
		});
	});

	it('defaults the environment and omits an empty release', () => {
		const options = sentryOptions({ dsn: 'https://k@bugs.example.com/2', release: '' });
		expect(options?.environment).toBe('development');
		expect(options?.release).toBeUndefined();
	});
});
