#!/usr/bin/env node
/**
 * WhatsApp Web.js 스크래퍼
 * MACHO-GPT v3.5-optimal WhatsApp Web.js 통합
 * 
 * 사용법: node whatsapp_webjs_scraper.js <group_name> [max_messages]
 * 예시: node whatsapp_webjs_scraper.js "HVDC 물류팀" 50
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

// CLI 인자 처리
const args = process.argv.slice(2);
const groupName = args[0];
const maxMessages = parseInt(args[1]) || 50;
const outputFile = args[2] || null;

if (!groupName) {
    console.error('❌ 사용법: node whatsapp_webjs_scraper.js <group_name> [max_messages] [output_file]');
    console.error('예시: node whatsapp_webjs_scraper.js "HVDC 물류팀" 50');
    process.exit(1);
}

console.log('🚀 MACHO-GPT v3.5-optimal WhatsApp Web.js 스크래퍼 시작');
console.log(`📋 대상 그룹: ${groupName}`);
console.log(`📊 최대 메시지 수: ${maxMessages}`);

// 클라이언트 설정
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "macho-gpt-optimal"
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

// QR 코드 이벤트
client.on('qr', (qr) => {
    console.log('📱 QR 코드를 스캔하여 WhatsApp에 로그인하세요:');
    qrcode.generate(qr, { small: true });
    console.log('⏳ 로그인 대기 중...');
});

// 인증 상태 이벤트
client.on('authenticated', () => {
    console.log('✅ WhatsApp 인증 완료');
});

// 인증 실패 이벤트
client.on('auth_failure', (msg) => {
    console.error('❌ 인증 실패:', msg);
    process.exit(1);
});

// 연결 끊김 이벤트
client.on('disconnected', (reason) => {
    console.log('🔌 연결이 끊어졌습니다:', reason);
});

// 준비 완료 이벤트
client.on('ready', async () => {
    console.log('🎉 WhatsApp Web.js 클라이언트 준비 완료');
    
    try {
        // 채팅 목록 가져오기
        console.log('📋 채팅 목록을 가져오는 중...');
        const chats = await client.getChats();
        
        // 대상 그룹 찾기
        const group = chats.find(chat => 
            chat.isGroup && chat.name === groupName
        );
        
        if (!group) {
            console.error(`❌ 그룹을 찾을 수 없습니다: ${groupName}`);
            console.log('📋 사용 가능한 그룹 목록:');
            const groupChats = chats.filter(chat => chat.isGroup);
            groupChats.forEach(chat => {
                console.log(`  - ${chat.name}`);
            });
            await client.destroy();
            process.exit(1);
        }
        
        console.log(`✅ 그룹 발견: ${group.name}`);
        console.log(`👥 참여자 수: ${group.participants.length}`);
        
        // 메시지 가져오기
        console.log(`📨 최근 ${maxMessages}개 메시지를 가져오는 중...`);
        const messages = await group.fetchMessages({ limit: maxMessages });
        
        console.log(`📊 ${messages.length}개 메시지 수집 완료`);
        
        // 메시지 데이터 변환
        const messageData = messages.map(msg => ({
            id: msg.id.id,
            body: msg.body || '',
            timestamp: msg.timestamp,
            author: msg.author || msg.from,
            from: msg.from,
            to: msg.to,
            type: msg.type,
            isForwarded: msg.isForwarded,
            isStarred: msg.isStarred,
            hasQuotedMsg: msg.hasQuotedMsg,
            quotedMsgId: msg.quotedMsgId,
            media: msg.hasMedia ? {
                mimetype: msg.media.mimetype,
                filename: msg.media.filename,
                size: msg.media.filesize
            } : null
        }));
        
        // 결과 데이터 구성
        const result = {
            status: 'SUCCESS',
            timestamp: new Date().toISOString(),
            group: {
                name: group.name,
                id: group.id.id,
                participants: group.participants.length,
                isGroup: group.isGroup
            },
            messages: messageData,
            summary: {
                total_messages: messageData.length,
                scraped_at: new Date().toISOString(),
                scraper_version: '3.5-optimal-webjs'
            }
        };
        
        // JSON 출력
        const jsonOutput = JSON.stringify(result, null, 2);
        
        if (outputFile) {
            // 파일로 저장
            const outputPath = path.resolve(outputFile);
            fs.writeFileSync(outputPath, jsonOutput, 'utf8');
            console.log(`💾 결과가 파일에 저장되었습니다: ${outputPath}`);
        } else {
            // 콘솔에 출력
            console.log('📄 결과 데이터:');
            console.log(jsonOutput);
        }
        
        console.log('✅ 스크래핑 완료!');
        
    } catch (error) {
        console.error('❌ 스크래핑 중 오류 발생:', error.message);
        process.exit(1);
    } finally {
        // 클라이언트 종료
        await client.destroy();
        console.log('🔌 클라이언트 연결 종료');
    }
});

// 에러 처리
client.on('error', (error) => {
    console.error('❌ 클라이언트 오류:', error);
    process.exit(1);
});

// 프로세스 종료 처리
process.on('SIGINT', async () => {
    console.log('\n⚠️  사용자에 의해 중단됨');
    await client.destroy();
    process.exit(0);
});

// 클라이언트 초기화
console.log('🔄 WhatsApp Web.js 클라이언트 초기화 중...');
client.initialize();
