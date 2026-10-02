import { requiredEnv } from './config.js';

export async function embed(input) {
  const response = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { Authorization: `Bearer ${requiredEnv('OPENAI_API_KEY')}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: process.env.EMBEDDING_MODEL || 'text-embedding-3-small', input }),
  });
  if (!response.ok) throw new Error(`Embedding provider returned ${response.status}`);
  const result = await response.json();
  return result.data.map((item) => item.embedding);
}

export async function streamAnswer({ instructions, messages }) {
  return fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: { Authorization: `Bearer ${requiredEnv('OPENAI_API_KEY')}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: process.env.CHAT_MODEL || 'gpt-4.1-mini',
      instructions,
      input: messages.map(({ role, content }) => ({ role, content })),
      stream: true,
      store: false,
      max_output_tokens: 700,
    }),
  });
}
