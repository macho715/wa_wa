#!/usr/bin/env node
"use strict";

/**
 * MACHO-GPT whatsapp-web.js scraper
 * Supports multi-group polling with optional media collection.
 */

const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const DEFAULT_LIMIT = 50;
const EXIT_CODES = {
  SUCCESS: 0,
  INVALID_ARGS: 2,
  AUTH_FAILURE: 3,
  RUNTIME_ERROR: 4,
};

const stderrLog = (message) => {
  const prefix = new Date().toISOString();
  process.stderr.write(`[${prefix}] ${message}\n`);
};

const parseArguments = (argv) => {
  const options = {
    groups: [],
    limit: DEFAULT_LIMIT,
    includeMedia: false,
    timeout: 300,
    groupLimits: {},
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    switch (token) {
      case "--group":
      case "--groups": {
        const value = argv[index + 1];
        if (!value) {
          throw new Error("Missing value for --group(s)");
        }
        index += 1;
        value
          .split(",")
          .map((entry) => entry.trim())
          .filter((entry) => entry.length > 0)
          .forEach((entry) => options.groups.push(entry));
        break;
      }
      case "--limit": {
        const value = parseInt(argv[index + 1], 10);
        if (Number.isNaN(value) || value <= 0) {
          throw new Error("--limit must be a positive integer");
        }
        options.limit = value;
        index += 1;
        break;
      }
      case "--include-media": {
        options.includeMedia = true;
        break;
      }
      case "--timeout": {
        const value = parseInt(argv[index + 1], 10);
        if (Number.isNaN(value) || value <= 0) {
          throw new Error("--timeout must be a positive integer");
        }
        options.timeout = value;
        index += 1;
        break;
      }
      case "--group-limit": {
        const value = argv[index + 1];
        if (!value || !value.includes("=")) {
          throw new Error("--group-limit requires format <name>=<limit>");
        }
        index += 1;
        const [name, limitValue] = value.split("=");
        const parsed = parseInt(limitValue, 10);
        if (!name || Number.isNaN(parsed) || parsed <= 0) {
          throw new Error("Invalid --group-limit entry");
        }
        options.groupLimits[name.trim()] = parsed;
        break;
      }
      default: {
        options.groups.push(token);
        break;
      }
    }
  }

  options.groups = [...new Set(options.groups)].filter((entry) => entry.length > 0);

  if (options.groups.length === 0) {
    throw new Error("At least one group must be provided");
  }

  return options;
};

const buildClient = () =>
  new Client({
    authStrategy: new LocalAuth({ clientId: "macho-gpt-optimal" }),
    puppeteer: {
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-zygote",
        "--disable-gpu",
      ],
    },
  });

const formatMessage = async (message, includeMedia) => {
  const base = {
    id: message.id.id,
    chatId: message.id._serialized,
    body: message.body || "",
    timestamp: message.timestamp,
    timestampIso: new Date(message.timestamp * 1000).toISOString(),
    from: message.from,
    to: message.to,
    author: message.author || message.from,
    type: message.type,
    isForwarded: Boolean(message.isForwarded),
    hasQuotedMsg: Boolean(message.hasQuotedMsg),
    quotedMsgId: message.quotedMsgId || null,
    fromMe: Boolean(message.fromMe),
  };

  if (includeMedia && message.hasMedia) {
    try {
      const media = await message.downloadMedia();
      if (media) {
        base.media = {
          mimetype: media.mimetype,
          filename: message.id.id,
          size: media.filesize || null,
          data: media.data,
        };
      }
    } catch (error) {
      stderrLog(`Failed to download media for message ${message.id.id}: ${error.message}`);
    }
  }

  return base;
};

const collectGroupMessages = async (client, chat, options) => {
  const limit = options.groupLimits[chat.name] || options.limit;
  stderrLog(`Fetching last ${limit} messages from ${chat.name}`);
  const messages = await chat.fetchMessages({ limit });
  const formatted = [];
  for (const message of messages) {
    // eslint-disable-next-line no-await-in-loop
    formatted.push(await formatMessage(message, options.includeMedia));
  }
  return {
    name: chat.name,
    id: chat.id._serialized,
    isGroup: Boolean(chat.isGroup),
    participants: Array.isArray(chat.participants) ? chat.participants.length : null,
    fetchedAt: new Date().toISOString(),
    messages: formatted,
    summary: {
      totalMessages: formatted.length,
      requestedLimit: limit,
      includeMedia: options.includeMedia,
    },
  };
};

const resolveTargetChats = (chats, targetNames) => {
  const lookup = new Map();
  chats
    .filter((chat) => chat.isGroup)
    .forEach((chat) => {
      lookup.set(chat.name, chat);
    });

  const missing = [];
  const targets = [];
  targetNames.forEach((name) => {
    const chat = lookup.get(name);
    if (chat) {
      targets.push(chat);
    } else {
      missing.push(name);
    }
  });

  return { targets, missing };
};

const shutdown = async (client, code = EXIT_CODES.SUCCESS) => {
  try {
    await client.destroy();
  } catch (error) {
    stderrLog(`Failed to destroy client cleanly: ${error.message}`);
  }
  process.exit(code);
};

const main = async () => {
  let options;
  try {
    options = parseArguments(process.argv.slice(2));
  } catch (error) {
    stderrLog(`Argument parsing failed: ${error.message}`);
    process.stdout.write(
      JSON.stringify(
        {
          status: "FAIL",
          error: error.message,
          timestamp: new Date().toISOString(),
        },
        null,
        2,
      ),
    );
    process.exit(EXIT_CODES.INVALID_ARGS);
    return;
  }

  const client = buildClient();

  client.on("qr", (qr) => {
    stderrLog("Scan the QR code to authenticate / QR 코드를 스캔하세요");
    qrcode.generate(qr, { small: true }, (qrCodeString) => {
      process.stderr.write(`${qrCodeString}\n`);
    });
  });

  client.on("authenticated", () => {
    stderrLog("Authentication successful / 인증 완료");
  });

  client.on("auth_failure", async (message) => {
    if (readyTimer) {
      clearTimeout(readyTimer);
      readyTimer = null;
    }
    stderrLog(`Authentication failed: ${message}`);
    process.stdout.write(
      JSON.stringify(
        {
          status: "FAIL",
          error: message,
          timestamp: new Date().toISOString(),
        },
        null,
        2,
      ),
    );
    await shutdown(client, EXIT_CODES.AUTH_FAILURE);
  });

  client.on("disconnected", (reason) => {
    stderrLog(`Client disconnected: ${reason}`);
  });

  let readyTimer;

  client.on("ready", async () => {
    if (readyTimer) {
      clearTimeout(readyTimer);
      readyTimer = null;
    }
    stderrLog("Client is ready, loading chats");
    const result = {
      status: "SUCCESS",
      backend: "webjs",
      timestamp: new Date().toISOString(),
      groups: [],
      errors: [],
    };

    try {
      const chats = await client.getChats();
      const { targets, missing } = resolveTargetChats(chats, options.groups);

      missing.forEach((name) => {
        result.errors.push({ group: name, reason: "GROUP_NOT_FOUND" });
      });

      for (const chat of targets) {
        try {
          // eslint-disable-next-line no-await-in-loop
          const groupResult = await collectGroupMessages(client, chat, options);
          result.groups.push(groupResult);
        } catch (error) {
          stderrLog(`Failed to collect messages for ${chat.name}: ${error.message}`);
          result.errors.push({ group: chat.name, reason: error.message });
        }
      }

      process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
      await shutdown(client, EXIT_CODES.SUCCESS);
    } catch (error) {
      stderrLog(`Unexpected runtime error: ${error.message}`);
      process.stdout.write(
        JSON.stringify(
          {
            status: "FAIL",
            error: error.message,
            timestamp: new Date().toISOString(),
          },
          null,
          2,
        ),
      );
      await shutdown(client, EXIT_CODES.RUNTIME_ERROR);
    }
  });

  process.on("SIGINT", async () => {
    if (readyTimer) {
      clearTimeout(readyTimer);
      readyTimer = null;
    }
    stderrLog("Received SIGINT, shutting down");
    await shutdown(client, EXIT_CODES.SUCCESS);
  });

  process.on("SIGTERM", async () => {
    if (readyTimer) {
      clearTimeout(readyTimer);
      readyTimer = null;
    }
    stderrLog("Received SIGTERM, shutting down");
    await shutdown(client, EXIT_CODES.SUCCESS);
  });

  try {
    stderrLog("Initializing whatsapp-web.js client");
    readyTimer = setTimeout(() => {
      stderrLog("Initialization timeout reached");
      process.stdout.write(
        JSON.stringify(
          {
            status: "FAIL",
            error: "Initialization timeout",
            timestamp: new Date().toISOString(),
          },
          null,
          2,
        ),
      );
      shutdown(client, EXIT_CODES.RUNTIME_ERROR);
    }, options.timeout * 1000);
    client.initialize();
  } catch (error) {
    stderrLog(`Failed to initialize client: ${error.message}`);
    process.stdout.write(
      JSON.stringify(
        {
          status: "FAIL",
          error: error.message,
          timestamp: new Date().toISOString(),
        },
        null,
        2,
      ),
    );
    process.exit(EXIT_CODES.RUNTIME_ERROR);
  }
};

main().catch((error) => {
  stderrLog(`Unhandled exception: ${error.message}`);
  process.stdout.write(
    JSON.stringify(
      {
        status: "FAIL",
        error: error.message,
        timestamp: new Date().toISOString(),
      },
      null,
      2,
    ),
  );
  process.exit(EXIT_CODES.RUNTIME_ERROR);
});
