#!/usr/bin/env node
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync, copyFileSync, lstatSync, realpathSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';
import os from 'os';
import readline from 'readline';

function copyDirSync(src, dest) {
  let realSrc = src;
  try { realSrc = realpathSync(src); } catch {}
  mkdirSync(dest, { recursive: true });
  const entries = readdirSync(realSrc, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = join(realSrc, entry.name);
    const destPath = join(dest, entry.name);
    let stat;
    try { stat = lstatSync(srcPath); } catch { continue; }
    if (stat.isSymbolicLink()) {
      try {
        const real = realpathSync(srcPath);
        const realStat = lstatSync(real);
        if (realStat.isDirectory()) copyDirSync(real, destPath);
        else copyFileSync(real, destPath);
      } catch {}
    } else if (stat.isDirectory()) {
      copyDirSync(srcPath, destPath);
    } else if (stat.isFile()) {
      copyFileSync(srcPath, destPath);
    }
  }
}

function countFiles(dir) {
  if (!existsSync(dir)) return 0;
  let count = 0;
  const entries = readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) count += countFiles(fullPath);
    else if (entry.isFile()) count++;
  }
  return count;
}

function countDirs(dir) {
  if (!existsSync(dir)) return 0;
  return readdirSync(dir, { withFileTypes: true }).filter(e => e.isDirectory()).length;
}

function scanSkillNames(skillsDir) {
  const names = [];
  if (!existsSync(skillsDir)) return names;
  for (const entry of readdirSync(skillsDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    names.push(entry.name);
  }
  return names.sort();
}

function generateBootstrapRule(targetDir, rulesLabel, skillsLabel) {
  const rulesDir = resolve(targetDir, 'rules');
  mkdirSync(rulesDir, { recursive: true });

  const skillNames = scanSkillNames(resolve(targetDir, 'skills'));
  const ruleFiles = existsSync(rulesDir)
    ? readdirSync(rulesDir, { withFileTypes: true }).filter(e => e.isFile() && e.name.endsWith('.md')).map(e => e.name)
    : [];

  const skillBullets = skillNames.map(n => `  - \`${n}\``).join('\n');

  const content = `---
alwaysApply: true
description: Trae AI Agent Enhancements bootstrap — enables rule routing, skill discovery, and agent enhancement.
---

# Trae AI Agent Enhancements

你已经加载了 Trae AI Agent Enhancements。本系统通过规则路由、专业技能和持久记忆三大层，让 AI Agent 更稳定、更专业。

## 核心规则

1. **任务分级** — 使用 T-Shirt Sizing（S/M/L）对任务自动分级：小任务快，大任务严
2. **技能优先** — 收到任务时，先检查是否有匹配的技能（Skill），如有则严格遵循其流程
3. **设计先于编码** — 需求模糊时，先做分析/设计，再写代码
4. **测试先于实现** — 推荐 TDD 流程：先写测试，再写实现
5. **验证先于完成** — 声称完成前，必须运行验证命令并提供证据
6. **可审计** — 所有决策和操作保留可追溯的记录

## 已安装的规则

规则文件位于 \`${rulesLabel}\` 目录，每个文件包含独立的规则定义。

## 已安装的技能（${skillNames.length} 个）

技能位于 \`${skillsLabel}\` 目录，每个技能有独立的 \`SKILL.md\` 文件：

${skillBullets}

## 使用方式

当任务匹配某个技能时，读取对应的 \`${skillsLabel}<skill-name>/SKILL.md\` 并严格遵循其流程。
`;

  const rulePath = resolve(rulesDir, '00-trae-agent-enhancements.md');
  writeFileSync(rulePath, content, 'utf8');
  return rulePath;
}

function verifySkillsCopied(srcCount, dest) {
  if (srcCount > 0 && countDirs(dest) === 0) {
    throw new Error(
      `复制 skills 失败：源目录有 ${srcCount} 个技能，但目标 ${dest} 为空。` +
      `\n  这通常是 npx 缓存目录权限或路径问题。请尝试：\n` +
      `    1. 清理缓存后重试: npm cache clean --force && npx trae-agent-enhancements\n` +
      `    2. 或全局安装: npm i -g trae-agent-enhancements && trae-agent-enhancements\n` +
      `    3. 或手动克隆复制: git clone https://github.com/MorningStar0709/trae-agent-enhancements.git`
    );
  }
}

const __dirname = dirname(fileURLToPath(import.meta.url));
const PKG = JSON.parse(readFileSync(resolve(__dirname, '..', 'package.json'), 'utf8'));
const RULES_SRC = resolve(__dirname, '..', 'rules');
const SKILLS_SRC = resolve(__dirname, '..', 'skills');
const DOCS_SRC = resolve(__dirname, '..', 'docs');
const HOME_DIR = os.homedir();

function getTargetDir(edition) {
  return edition === 'intl'
    ? resolve(HOME_DIR, '.trae')
    : resolve(HOME_DIR, '.trae-cn');
}

function getEditionLabel(edition) {
  return edition === 'intl' ? '国际版（trae.ai）' : '国内版（trae.cn）';
}

function showHelp() {
  console.log(`
  trae-agent-enhancements v${PKG.version} — Trae AI Agent Enhancements

  用法：
    npx trae-agent-enhancements                     交互式选择版本并安装
    npx trae-agent-enhancements --edition cn        国内版（默认），安装到 ~/.trae-cn/
    npx trae-agent-enhancements --edition intl      国际版，安装到 ~/.trae/
    npx trae-agent-enhancements --help              显示帮助
    npx trae-agent-enhancements --version           显示版本

  说明：
    安装到用户主目录：
      国内版（trae.cn） → ~/.trae-cn/rules/ + ~/.trae-cn/skills/
      国际版（trae.ai）  → ~/.trae/rules/  + ~/.trae/skills/

  官方文档：https://docs.trae.cn/ide/skills
  项目：https://github.com/MorningStar0709/trae-agent-enhancements
`);
}

function printSourceInfo() {
  const srcSkillCount = countDirs(SKILLS_SRC);
  const srcRuleCount = countFiles(RULES_SRC);
  const srcDocCount = existsSync(DOCS_SRC) ? countFiles(DOCS_SRC) : 0;
  console.log(`  源: ${srcRuleCount} 条规则, ${srcSkillCount} 个技能${srcDocCount > 0 ? `, ${srcDocCount} 篇文档` : ''}`);
}

function install(edition) {
  const targetDir = getTargetDir(edition);
  const label = getEditionLabel(edition);
  const skillsDest = resolve(targetDir, 'skills');
  const rulesDest = resolve(targetDir, 'rules');

  console.log(`\n  安装到 ${label}: ${targetDir}\n`);

  mkdirSync(skillsDest, { recursive: true });
  copyDirSync(SKILLS_SRC, skillsDest);
  const installedSkillCount = countDirs(skillsDest);
  verifySkillsCopied(countDirs(SKILLS_SRC), skillsDest);
  console.log(`  ✅ 技能: ${installedSkillCount} 个 -> ${skillsDest}`);

  if (existsSync(RULES_SRC)) {
    mkdirSync(rulesDest, { recursive: true });
    copyDirSync(RULES_SRC, rulesDest);
  }
  console.log(`  ✅ 规则: ${countFiles(rulesDest)} 条 -> ${rulesDest}`);

  const dirLabel = edition === 'intl' ? '~/.trae' : '~/.trae-cn';
  const bootstrapPath = generateBootstrapRule(targetDir, `${dirLabel}/rules/`, `${dirLabel}/skills/`);
  console.log(`  ✅ bootstrap: 已生成 -> ${bootstrapPath}`);

  if (existsSync(DOCS_SRC)) {
    const docsDest = resolve(targetDir, 'docs');
    mkdirSync(docsDest, { recursive: true });
    copyDirSync(DOCS_SRC, docsDest);
    console.log(`  ✅ 文档: ${countFiles(docsDest)} 篇 -> ${docsDest}`);
  }

  console.log(`\n  🎉 安装完成！`);
  console.log(`  在 ${label} 中打开任意项目即可使用。\n`);
}

async function promptEdition() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(`  请选择你的 Trae 版本：
    1) 国内版（trae.cn）（默认）— 安装到 ~/.trae-cn/
    2) 国际版（trae.ai）— 安装到 ~/.trae/
    3) 退出

  请输入 [1/2/3]（默认 1）: `, (answer) => {
      rl.close();
      const choice = answer.trim();
      if (choice === '' || choice === '1') resolve('cn');
      else if (choice === '2') resolve('intl');
      else if (choice === '3') resolve('exit');
      else resolve('cn');
    });
  });
}

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    process.exit(0);
  }

  if (args.includes('--version') || args.includes('-v')) {
    console.log(PKG.version);
    process.exit(0);
  }

  console.log(`\n  ╔══════════════════════════════════════════════╗`);
  console.log(`  ║   trae-agent-enhancements v${PKG.version.padEnd(22)}║`);
  console.log(`  ║   Trae AI Agent Enhancements              ║`);
  console.log(`  ╚══════════════════════════════════════════════╝\n`);

  if (!existsSync(SKILLS_SRC)) {
    console.error('  ❌ 错误：skills 源目录不存在，请重新安装 trae-agent-enhancements。');
    process.exit(1);
  }

  printSourceInfo();

  const editionFlagIndex = args.indexOf('--edition');
  const editionFlag = editionFlagIndex >= 0 && editionFlagIndex + 1 < args.length ? args[editionFlagIndex + 1] : null;

  let edition;
  if (editionFlag === 'intl' || editionFlag === 'international') {
    edition = 'intl';
    console.log(`  模式: --edition intl\n`);
  } else if (editionFlag === 'cn') {
    edition = 'cn';
    console.log(`  模式: --edition cn\n`);
  } else {
    console.log('');
    const choice = await promptEdition();
    if (choice === 'exit') {
      console.log(`\n  已退出，未做任何安装。\n`);
      process.exit(0);
    }
    edition = choice;
  }

  install(edition);
}

try {
  await main();
} catch (err) {
  console.error(`\n  ❌ 安装失败: ${err.message}\n`);
  process.exit(1);
}
