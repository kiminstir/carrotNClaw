import * as Sentry from '@sentry/sveltekit';
import { env } from '$env/dynamic/public';
import { sentryOptions } from '$lib/monitoring';

const options = sentryOptions({
	dsn: env.PUBLIC_SENTRY_DSN,
	environment: env.PUBLIC_SENTRY_ENVIRONMENT,
	release: env.PUBLIC_APP_RELEASE
});
if (options) Sentry.init(options);

export const handleError = Sentry.handleErrorWithSentry();
