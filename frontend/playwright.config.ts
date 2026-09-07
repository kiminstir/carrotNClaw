import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: 'e2e',
	webServer: {
		command: 'pnpm build && pnpm preview --port 4173',
		port: 4173,
		reuseExistingServer: !process.env.CI,
		env: { WAGTAIL_INTERNAL_URL: process.env.WAGTAIL_INTERNAL_URL ?? 'http://localhost:8000' }
	},
	use: { baseURL: 'http://localhost:4173' }
});
