#!/usr/bin/env node
'use strict';

const { ApiClient } = require('./index');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    }
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv);
  const url = args.url;
  const method = (args.method || 'GET').toUpperCase();
  const data = args.data;

  if (!url) {
    console.error('Usage: api-client --url <URL> [--method GET|POST] [--data <json>] [--headers <json>] [--timeout ms]');
    process.exit(1);
  }

  const client = new ApiClient({
    baseUrl: url,
    timeout: args.timeout ? parseInt(args.timeout) : 15000,
    headers: args.headers ? JSON.parse(args.headers) : {}
  });

  try {
    let result;
    if (method === 'GET') {
      result = await client.get(url, { retries: 0 });
    } else {
      result = await client.request ? client.request(method, url, data ? JSON.parse(data) : null, { retries: 0 })
        : await client.post(url, data ? JSON.parse(data) : null, { retries: 0 });
    }
    console.log(JSON.stringify(result.data, null, 2));
  } catch (err) {
    console.error(`Error: ${err.message} (${err.status})`);
    process.exit(1);
  }
}

main();