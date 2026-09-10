/**
 * Options for the Sentry SDK, which reports to our own Bugsink instance. Returns null when no
 * DSN is configured (local dev, tests), so the hooks skip initialisation entirely. Bugsink stores
 * errors only: tracing stays off, and no replay is loaded, which keeps the bundle small.
 */
export interface MonitoringEnv {
	dsn?: string;
	environment?: string;
	release?: string;
}

export interface SentryOptions {
	dsn: string;
	environment: string;
	release: string | undefined;
	tracesSampleRate: 0;
	sendDefaultPii: true;
}

export function sentryOptions({ dsn, environment, release }: MonitoringEnv): SentryOptions | null {
	if (!dsn) return null;
	return {
		dsn,
		environment: environment || 'development',
		release: release || undefined,
		tracesSampleRate: 0,
		sendDefaultPii: true
	};
}
