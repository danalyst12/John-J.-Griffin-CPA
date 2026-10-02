import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const configPath = fileURLToPath(new URL('../../business.config.json', import.meta.url));
const businessConfig = JSON.parse(readFileSync(configPath, 'utf8'));

export function getBusiness() {
  return {
    ...businessConfig,
    id: process.env.BUSINESS_ID || businessConfig.id,
    websiteUrl: process.env.BUSINESS_WEBSITE_URL || businessConfig.websiteUrl,
  };
}

export function requiredEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing server configuration: ${name}`);
  return value;
}
