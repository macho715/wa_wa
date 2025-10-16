#!/usr/bin/env node
/**
 * Node.js 환경 확인 스크립트
 * MACHO-GPT v3.5-optimal WhatsApp Web.js 통합
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Node.js 환경 확인 중...\n');

// Node.js 버전 확인
try {
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);

    console.log(`✅ Node.js 버전: ${nodeVersion}`);

    if (majorVersion < 14) {
        console.log('❌ Node.js 14.0.0 이상이 필요합니다.');
        process.exit(1);
    } else {
        console.log('✅ Node.js 버전 요구사항 충족');
    }
} catch (error) {
    console.log('❌ Node.js 버전 확인 실패:', error.message);
    process.exit(1);
}

// npm 버전 확인
try {
    const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
    console.log(`✅ npm 버전: ${npmVersion}`);
} catch (error) {
    console.log('❌ npm 확인 실패:', error.message);
    process.exit(1);
}

// package.json 존재 확인
const packageJsonPath = path.join(__dirname, 'package.json');
if (fs.existsSync(packageJsonPath)) {
    console.log('✅ package.json 파일 존재');
} else {
    console.log('❌ package.json 파일이 없습니다.');
    process.exit(1);
}

// node_modules 확인
const nodeModulesPath = path.join(__dirname, 'node_modules');
if (fs.existsSync(nodeModulesPath)) {
    console.log('✅ node_modules 디렉토리 존재');

    // 필수 패키지 확인
    const requiredPackages = ['whatsapp-web.js', 'qrcode-terminal', 'puppeteer'];
    let allPackagesInstalled = true;

    for (const pkg of requiredPackages) {
        const pkgPath = path.join(nodeModulesPath, pkg);
        if (fs.existsSync(pkgPath)) {
            console.log(`✅ ${pkg} 설치됨`);
        } else {
            console.log(`❌ ${pkg} 설치되지 않음`);
            allPackagesInstalled = false;
        }
    }

    if (!allPackagesInstalled) {
        console.log('\n📦 의존성 패키지 설치가 필요합니다.');
        console.log('다음 명령어를 실행하세요: npm install');
        process.exit(1);
    }
} else {
    console.log('❌ node_modules 디렉토리가 없습니다.');
    console.log('다음 명령어를 실행하세요: npm install');
    process.exit(1);
}

console.log('\n🎉 Node.js 환경이 정상적으로 설정되었습니다!');
console.log('WhatsApp Web.js 스크래퍼를 사용할 수 있습니다.');
