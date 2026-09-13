import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';
import { createInterface } from 'node:readline/promises';
import { AGENTS, manage, packageVersion } from './installer.mjs';
import { demo, doctor } from './workflows.mjs';

export const HELP = `optical-design — bundled optical-design skill installer

Usage:
  optical-design install --agent NAME [--global] [--json]
  optical-design update --agent NAME [--global] [--json]
  optical-design uninstall --agent NAME [--global] [--json]
  optical-design doctor [--json]
  optical-design demo --out NEW-DIRECTORY [--json]
  optical-design --help
  optical-design --version [--json]

Agents: ${Object.keys(AGENTS).join(', ')}
Project scope is the default; --global explicitly selects your home directory.
Interactive install can ask for an agent. Other uses require --agent.
Update uses this bundled version and keeps a backup. Fetch a newer version with
npx optical-design@latest update --agent NAME. Edited or unmanaged files are preserved.
Demo uses uv, which may download Python and the pinned portable dependencies.
`;

function parse(args) {
  if (args.length === 0) return { command: 'help', options: {} };
  let command = args[0];
  if (command === '--help' || command === '-h') command = 'help';
  if (command === '--version' || command === '-v') command = 'version';
  if (!['install', 'update', 'uninstall', 'doctor', 'demo', 'help', 'version'].includes(command)) throw new Error(`Unknown command: ${args[0]}. Use --help.`);
  const allowed = ['install', 'update', 'uninstall'].includes(command) ? ['agent', 'global', 'json'] : command === 'demo' ? ['out', 'json'] : ['json'];
  const options = {};
  for (let index = 1; index < args.length; index++) {
    const name = args[index].replace(/^--/, '');
    if (!args[index].startsWith('--') || !allowed.includes(name) || Object.hasOwn(options, name)) throw new Error(`Invalid or duplicate option: ${args[index]}`);
    if (['agent', 'out'].includes(name)) {
      const value = args[++index];
      if (!value || value.startsWith('--')) throw new Error(`--${name} requires a value`);
      options[name] = value;
    } else options[name] = true;
  }
  return { command, options };
}

export async function execute(args, overrides = {}) {
  const context = {
    packageRoot: path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
    cwd: process.cwd(), home: homedir(), isTTY: Boolean(process.stdin.isTTY && process.stderr.isTTY),
    ...overrides,
  };
  const { command, options } = parse(args);
  if (command === 'help') return { ok: true, operation: 'help', text: HELP };
  if (command === 'version') return { ok: true, operation: 'version', version: await packageVersion(context.packageRoot) };
  if (Number(process.versions.node.split('.')[0]) < 22) throw new Error('Node.js 22 or newer is required');
  if (command === 'doctor') return doctor(context);
  if (command === 'demo') {
    if (!options.out) throw new Error('demo requires --out NEW-DIRECTORY');
    return demo(options.out, context);
  }
  if (!options.agent && command === 'install' && context.isTTY && !options.json) {
    const prompt = createInterface({ input: process.stdin, output: process.stderr });
    try { options.agent = (await prompt.question(`Agent (${Object.keys(AGENTS).join(', ')}): `)).trim(); }
    finally { prompt.close(); }
  }
  if (!options.agent) throw new Error('An explicit --agent is required for noninteractive install, update, and uninstall. Use --help.');
  return manage(command, options, context);
}

export function format(result) {
  if (result.operation === 'help') return result.text;
  if (result.operation === 'version') return result.version;
  if (result.operation === 'doctor') return `Node ${result.node.version}: ${result.node.ready ? 'ready' : 'requires >=22'}\nuv: ${result.uv.ready ? result.uv.version : result.uv.message}\n${result.native}`;
  if (result.operation === 'demo') return `Demo improved; saved candidate verified.\nReport: ${result.report}\nReview: ${result.review}`;
  return `${result.operation}: optical-design ${result.version} (${result.agent}, ${result.scope})\n${result.destination}${result.backup ? `\nRecoverable backup: ${result.backup}` : ''}`;
}
