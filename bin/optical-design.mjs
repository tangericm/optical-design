#!/usr/bin/env node
import { execute, format } from '../lib/cli.mjs';

const args = process.argv.slice(2);
const json = args.includes('--json');
try {
  const result = await execute(args, { progress: message => process.stderr.write(`${message}\n`) });
  process.stdout.write(`${json ? JSON.stringify(result) : format(result)}\n`);
  process.exitCode = result.ok ? 0 : 1;
} catch (error) {
  const result = { ok: false, error: error.message };
  (json ? process.stdout : process.stderr).write(`${json ? JSON.stringify(result) : `Error: ${result.error}`}\n`);
  process.exitCode = 1;
}
