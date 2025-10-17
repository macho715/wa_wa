#!/usr/bin/env node
/**
 * whatsapp-web.js 기반 그룹 스크래퍼입니다. (KR) WhatsApp Web.js based group scraper. (EN)
 *
 * Usage:
 *   node whatsapp_webjs_scraper.js "Group Name" [max_messages]
 *   node whatsapp_webjs_scraper.js "Group A,Group B" 75
 *   node whatsapp_webjs_scraper.js "ALL" 50
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const path = require('path');

const args = process.argv.slice(2);
const groupSpec = args[0];
const maxMessages = Number.parseInt(args[1] || '50', 10);

const log = (...messages) => console.error(...messages);

if (!groupSpec) {
  log('❌ Usage: node whatsapp_webjs_scraper.js "<group|group1,group2|ALL>" [max_messages]');
  process.exitCode = 1;
  process.stdout.write(
    JSON.stringify({
      status: 'FAIL',
      error: 'GROUP_SPEC_MISSING',
      meta: {
        reason: 'Group specification argument is required.',
      },
    }),
  );
  process.exit();
}

const normaliseGroupSpec = (spec) => {
  if (!spec) {
    return [];
  }
  if (spec.trim().toUpperCase() === 'ALL') {
    return null;
  }
  try {
    if (spec.trim().startsWith('[')) {
      const parsed = JSON.parse(spec);
      if (Array.isArray(parsed)) {
        return parsed.map((value) => String(value).trim()).filter(Boolean);
      }
    }
  } catch (error) {
    log('⚠️  Failed to parse JSON group specification:', error.message);
  }
  return spec
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
};

const requestedGroups = normaliseGroupSpec(groupSpec);

const toIsoString = (timestamp) => {
  if (!timestamp) {
    return null;
  }
  const milliseconds = Number(timestamp) * 1000;
  return new Date(milliseconds).toISOString();
};

const emitResult = (payload, exitCode = 0) => {
  process.stdout.write(JSON.stringify(payload));
  process.exitCode = exitCode;
};

const client = new Client({
  authStrategy: new LocalAuth({ clientId: 'macho-gpt-optimal' }),
  puppeteer: {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
    ],
  },
});

client.on('qr', (qr) => {
  log('📱 Scan the QR code to authenticate.');
  qrcode.generate(qr, { small: true });
});

client.on('authenticated', () => {
  log('✅ Authentication successful.');
});

client.on('auth_failure', (message) => {
  log('❌ Authentication failure:', message);
});

client.on('ready', async () => {
  log('🚀 whatsapp-web.js client ready.');
  const groupsPayload = [];

  try {
    const chats = await client.getChats();
    const groupChats = chats.filter((chat) => chat.isGroup);

    const targets =
      requestedGroups === null
        ? groupChats
        : groupChats.filter((chat) => requestedGroups.includes(chat.name));

    if (!targets.length) {
      emitResult(
        {
          status: 'FAIL',
          error: 'GROUP_NOT_FOUND',
          meta: {
            requested: requestedGroups,
            available_groups: groupChats.map((chat) => chat.name),
          },
        },
        1,
      );
      await client.destroy();
      return;
    }

    for (const group of targets) {
      log(`📨 Fetching up to ${maxMessages} messages from ${group.name}`);
      const messages = await group.fetchMessages({ limit: maxMessages });
      const serialisedMessages = [];

      for (const message of messages) {
        serialisedMessages.push({
          id: message.id.id,
          body: message.body || '',
          timestamp_unix: message.timestamp,
          timestamp_iso: toIsoString(message.timestamp),
          author: message.author || message.from,
          from: message.from,
          to: message.to,
          type: message.type,
          has_media: Boolean(message.hasMedia),
          quoted_msg_id: message.quotedMsgId || null,
          is_forwarded: Boolean(message.isForwarded),
          is_starred: Boolean(message.isStarred),
        });
      }

      groupsPayload.push({
        name: group.name,
        id: group.id._serialized,
        participants: Array.isArray(group.participants)
          ? group.participants.length
          : null,
        messages: serialisedMessages,
        summary: {
          total_messages: serialisedMessages.length,
          fetched_at: new Date().toISOString(),
        },
      });
    }

    emitResult({
      status: 'SUCCESS',
      groups: groupsPayload,
      meta: {
        backend: 'webjs',
        scraped_at: new Date().toISOString(),
        requested_groups: requestedGroups,
        max_messages: maxMessages,
        working_directory: path.resolve('.'),
      },
    });
  } catch (error) {
    log('❌ Error while scraping:', error.message);
    emitResult(
      {
        status: 'FAIL',
        error: error.message,
      },
      1,
    );
  } finally {
    await client.destroy();
    log('🔌 Client connection closed.');
  }
});

client.on('disconnected', (reason) => {
  log('🔌 Client disconnected:', reason);
});

client.on('error', (error) => {
  log('❌ Client error:', error.message || error);
});

client.initialize();