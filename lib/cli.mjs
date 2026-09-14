import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';
import { createInterface } from 'node:readline/promises';
import { AGENTS, manage, packageVersion } from './installer.mjs';
import { demo, doctor, walkthrough } from './workflows.mjs';

export const HELP = `optical-design — bundled optical-design skill installer

Usage:
  optical-design install --agent NAME [--global] [--json]
  optical-design update --agent NAME [--global] [--json]
  optical-design uninstall --agent NAME [--global] [--json]
  optical-design prune-backups --agent NAME [--global] [--apply] [--json]
  optical-design doctor [--engine-check] [--json]
  optical-design demo --out NEW-DIRECTORY [--json]
  optical-design walkthrough --out NEW-DIRECTORY [--json]
  optical-design --help
  optical-design --version [--json]

Agents: ${Object.keys(AGENTS).join(', ')}
Project scope is the default; --global explicitly selects your home directory.
Interactive install can ask for an agent. Other uses require --agent.
Update uses this bundled version and retains one intact prior backup. Fetch a newer version with
npx optical-design@latest update --agent NAME. Edited or unmanaged files are preserved.
Prune-backups previews cleanup by default; --apply removes only intact owned backups.
Demo, walkthrough, and doctor --engine-check use uv and may download Python and pinned dependencies.
`;

function parse(args) {
  if (args.length === 0) return { command: 'help', options: {} };
  let command = args[0];
  if (command === '--help' || command === '-h') command = 'help';
  if (command === '--version' || command === '-v') command = 'version';
  if (!['install', 'update', 'uninstall', 'prune-backups', 'doctor', 'demo', 'walkthrough', 'help', 'version'].includes(command)) throw new Error(`Unknown command: ${args[0]}. Use --help.`);
  const allowed = ['install', 'update', 'uninstall'].includes(command) ? ['agent', 'global', 'json'] : command === 'prune-backups' ? ['agent', 'global', 'apply', 'json'] : ['demo', 'walkthrough'].includes(command) ? ['out', 'json'] : command === 'doctor' ? ['engine-check', 'json'] : ['json'];
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
  if (command === 'doctor') return doctor(context, { engineCheck: options['engine-check'] });
  if (['demo', 'walkthrough'].includes(command)) {
    if (!options.out) throw new Error(`${command} requires --out NEW-DIRECTORY`);
    return (command === 'demo' ? demo : walkthrough)(options.out, context);
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
  if (result.operation === 'doctor') return `Node ${result.node.version}: ${result.node.ready ? 'ready' : 'requires >=22'}\nuv: ${result.uv.ready ? result.uv.version : result.uv.message}\nPortable engine: ${result.portable.status}. ${result.portable.message}\n${result.native}`;
  if (result.operation === 'walkthrough') return `Walkthrough complete.\nReview: ${result.review}\nSummary: ${result.summary}`;
  if (result.operation === 'prune-backups') return `${result.dryRun ? 'Preview' : 'Cleanup'}: ${result.removable.length} intact owned backup(s); ${result.removed.length} removed.\n${result.removable.join('\n')}${result.preserved.length ? `\nPreserved (edited, legacy, or unowned):\n${result.preserved.join('\n')}` : ''}`;
  if (result.operation === 'demo') return `Demo improved; saved candidate verified.\nReport: ${result.report}\nReview: ${result.review}`;
  return `${result.operation}: optical-design ${result.version} (${result.agent}, ${result.scope})\n${result.destination}${result.backup ? `\nRecoverable backup (one prior version retained): ${result.backup}` : ''}${result.preservedBackups?.length ? `\nPreserved backups requiring manual review:\n${result.preservedBackups.join('\n')}` : ''}`;
}
