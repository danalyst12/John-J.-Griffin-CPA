import { createClient } from '@supabase/supabase-js';
import { requiredEnv } from './config.js';

let client;
export function db() {
  if (!client) client = createClient(requiredEnv('SUPABASE_URL'), requiredEnv('SUPABASE_SERVICE_ROLE_KEY'), {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  return client;
}
