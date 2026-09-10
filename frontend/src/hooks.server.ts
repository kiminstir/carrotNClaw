import * as Sentry from '@sentry/sveltekit';
import { env } from '$env/dynamic/private';
import { sentryOptions } from '$lib/monitoring';

// Initialised here rather than in instrumentation.server.ts: tracing is off, so import order
// does not matter for error capture, and this needs no experimental kit flags.
const options = sentryOptions({
	dsn: env.SENTRY_DSN,
	environment: env.SENTRY_ENVIRONMENT,
	release: env.APP_RELEASE
});
if (options) Sentry.init(options);

export const handle = Sentry.sentryHandle();
export const handleError = Sentry.handleErrorWithSentry();
