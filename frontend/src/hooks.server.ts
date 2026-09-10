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

// injectFetchProxyScript: false — Kit >= 2.16 needs no fetch proxy, but the SDK's runtime
// detection imports @sveltejs/kit, a devDependency pruned from this image, so that check
// always throws and it would otherwise inject the proxy script into every SSR'd page.
export const handle = Sentry.sentryHandle({ injectFetchProxyScript: false });
export const handleError = Sentry.handleErrorWithSentry();
