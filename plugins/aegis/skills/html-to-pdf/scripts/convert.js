/**
 * html-to-pdf / scripts/convert.js
 *
 * HTML 파일을 텍스트, hyperlink, 이미지, 디자인 모두 보존하는 PDF로 변환.
 * Playwright headless + page.pdf() 직접 호출.
 *
 * CLI 사용법:
 *   node convert.js --input=/path/to/file.html --output=/path/to/file.pdf [옵션...]
 *
 * Node 모듈로 require해서 함수 호출:
 *   const { htmlToPdf } = require('./convert');
 *   await htmlToPdf({ inputPath: '...', outputPath: '...' });
 *
 * 사전 요구 사항:
 *   npm install playwright
 *   npx playwright install chromium
 *
 * 검증 도구 (선택):
 *   sudo apt install poppler-utils
 */

'use strict';

const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs');

// ---------------------------------------------------------------------------
// Playwright 동적 로드 (경로에 의존하지 않고 portably 탐색)
// ---------------------------------------------------------------------------

function loadPlaywright() {
  const candidates = ['playwright', 'playwright-core'];
  for (const pkg of candidates) {
    try {
      return require(pkg);
    } catch (_err) {
      // 다음 후보 시도
    }
  }
  console.error('[html-to-pdf] Playwright를 찾을 수 없습니다.');
  console.error('설치 방법:');
  console.error('  npm install playwright');
  console.error('  npx playwright install chromium');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// 옵션 파서 (CLI args → 객체)
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const opts = {};
  for (const arg of argv.slice(2)) {
    const match = arg.match(/^--([^=]+)(?:=(.*))?$/);
    if (!match) continue;
    const key = match[1];
    const val = match[2] !== undefined ? match[2] : 'true';
    opts[key] = val;
  }
  return opts;
}

function resolvePageSize(sizeStr) {
  const presets = {
    '16:9': { width: '13.333in', height: '7.5in' },
    'A4': { width: '8.27in', height: '11.69in' },
    'A3': { width: '11.69in', height: '16.54in' },
  };
  if (presets[sizeStr]) return presets[sizeStr];
  // 사용자 정의: "WxH" 형식 (예: "10in x 7in" 또는 "10inx7in")
  const match = sizeStr.replace(/\s/g, '').match(/^(.+)x(.+)$/i);
  if (match) return { width: match[1], height: match[2] };
  console.warn(`[html-to-pdf] 알 수 없는 page-size: "${sizeStr}". 16:9 기본값 사용.`);
  return presets['16:9'];
}

// ---------------------------------------------------------------------------
// 핵심 변환 함수
// ---------------------------------------------------------------------------

/**
 * @param {object} options
 * @param {string}  options.inputPath               - HTML 파일 절대 경로 (필수)
 * @param {string}  [options.outputPath]            - 출력 PDF 경로 (기본: inputPath 확장자 .pdf)
 * @param {string}  [options.pageSize='16:9']       - '16:9' | 'A4' | 'A3' | 'WxH'
 * @param {boolean} [options.landscape=true]        - 가로 방향
 * @param {string}  [options.margin='0']            - 여백 (예: '0' 또는 '10px')
 * @param {string}  [options.pageBreakSelector='.slide-wrapper'] - 페이지 분리 셀렉터
 * @param {number}  [options.fontWaitMs=2500]       - 폰트 로드 추가 대기 (ms)
 * @param {boolean} [options.printBackground=true]  - 배경 이미지, 배경색 출력
 * @param {boolean} [options.noValidation=false]    - 검증 단계 생략
 * @param {number}  [options.timeout=90000]         - 페이지 로드 타임아웃 (ms)
 * @returns {Promise<{outputPath: string, validationResult: object}>}
 */
async function htmlToPdf({
  inputPath,
  outputPath,
  pageSize = '16:9',
  landscape = true,
  margin = '0',
  pageBreakSelector = '.slide-wrapper',
  fontWaitMs = 2500,
  printBackground = true,
  noValidation = false,
  timeout = 90000,
} = {}) {
  if (!inputPath) throw new Error('inputPath는 필수입니다.');

  const absInput = path.resolve(inputPath);
  if (!fs.existsSync(absInput)) {
    throw new Error(`입력 파일을 찾을 수 없습니다: ${absInput}`);
  }

  const resolvedOutput = outputPath
    ? path.resolve(outputPath)
    : absInput.replace(/\.html?$/i, '') + '.pdf';

  const { width, height } = resolvePageSize(pageSize);

  const marginObj =
    margin === '0' || margin === 0
      ? { top: 0, right: 0, bottom: 0, left: 0 }
      : { top: margin, right: margin, bottom: margin, left: margin };

  const pw = loadPlaywright();

  console.log(`[html-to-pdf] 시작: ${absInput}`);

  const browser = await pw.chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('file://' + absInput, { waitUntil: 'networkidle', timeout });
    console.log('[html-to-pdf] 페이지 로드 완료');

    // 인쇄 CSS: 풀 채움, 그림자/테두리/여백 제거, 페이지 분리
    await page.addStyleTag({
      content: `
        @page { size: ${width} ${height}; margin: 0; padding: 0; }
        @media print {
          html, body {
            margin: 0 !important; padding: 0 !important;
            background: white !important;
            width: ${width} !important;
          }
          .controls, .dl-btn, body > h1, body > p, body > header, .slide-label {
            display: none !important;
          }
          ${pageBreakSelector} {
            margin: 0 !important; padding: 0 !important;
            page-break-after: always; break-after: page;
            width: ${width} !important; height: ${height} !important;
            box-shadow: none !important; border: none !important;
            border-radius: 0 !important;
            overflow: hidden !important; display: block !important;
          }
          ${pageBreakSelector}:last-child {
            page-break-after: auto; break-after: auto;
          }
          .slide {
            margin: 0 !important; padding: 0 !important;
            width: ${width} !important; height: ${height} !important;
            box-shadow: none !important; border: none !important;
            border-radius: 0 !important;
            overflow: hidden !important;
            page-break-inside: avoid; break-inside: avoid;
          }
        }
      `,
    });

    // 스크린 CSS: 미리보기 UI 요소 숨김 + 그림자 제거
    await page.addStyleTag({
      content: `
        .controls, .dl-btn, body > h1, body > p, .slide-label {
          display: none !important;
        }
        html, body {
          margin: 0 !important; padding: 0 !important;
          background: white !important;
        }
        ${pageBreakSelector}, .slide {
          box-shadow: none !important; border: none !important;
          border-radius: 0 !important;
          margin: 0 !important; padding: 0 !important;
        }
      `,
    });

    // 한글 웹폰트 로드 완료 대기
    await page.evaluate(() => document.fonts.ready);
    if (fontWaitMs > 0) {
      await page.waitForTimeout(fontWaitMs);
      console.log(`[html-to-pdf] 폰트 대기 ${fontWaitMs}ms 완료`);
    }

    await page.pdf({
      path: resolvedOutput,
      width,
      height,
      landscape,
      printBackground,
      preferCSSPageSize: true,
      margin: marginObj,
    });

    console.log(`[html-to-pdf] PDF 저장 완료: ${resolvedOutput}`);
  } finally {
    await browser.close();
  }

  // 검증
  let validationResult = {};
  if (!noValidation) {
    validationResult = validatePdf(resolvedOutput);
  }

  return { outputPath: resolvedOutput, validationResult };
}

// ---------------------------------------------------------------------------
// 검증 함수 (poppler-utils 없으면 graceful degradation)
// ---------------------------------------------------------------------------

function validatePdf(pdfPath) {
  const result = {
    fileSize: null,
    pages: null,
    pageSize: null,
    textChars: null,
    hyperlinkCount: null,
    warnings: [],
  };

  // 파일 크기
  try {
    const stat = fs.statSync(pdfPath);
    result.fileSize = (stat.size / (1024 * 1024)).toFixed(2) + 'MB';
    console.log(`[검증] 파일 크기: ${result.fileSize}`);
  } catch (err) {
    result.warnings.push(`파일 크기 확인 실패: ${err.message}`);
  }

  // pdfinfo
  if (commandExists('pdfinfo')) {
    try {
      const info = execSync(`pdfinfo "${pdfPath}" 2>/dev/null`, { encoding: 'utf8' });
      const pagesMatch = info.match(/Pages:\s+(\d+)/);
      const sizeMatch = info.match(/Page size:\s+([^\n]+)/);
      result.pages = pagesMatch ? parseInt(pagesMatch[1], 10) : null;
      result.pageSize = sizeMatch ? sizeMatch[1].trim() : null;
      console.log(`[검증] 페이지 수: ${result.pages}, 크기: ${result.pageSize}`);
    } catch (err) {
      result.warnings.push(`pdfinfo 실행 실패: ${err.message}`);
    }
  } else {
    result.warnings.push('pdfinfo 없음 (apt install poppler-utils). 페이지 수 확인 생략.');
  }

  // pdftotext
  if (commandExists('pdftotext')) {
    try {
      const text = execSync(`pdftotext "${pdfPath}" - 2>/dev/null`, { encoding: 'utf8' });
      result.textChars = text.trim().length;
      if (result.textChars === 0) {
        result.warnings.push('텍스트 추출 0건. PNG 캡처 흐름으로 변환됐을 가능성 있음. troubleshooting.md "텍스트 깨짐" 섹션 참조.');
      }
      console.log(`[검증] 텍스트 추출: ${result.textChars}자`);
    } catch (err) {
      result.warnings.push(`pdftotext 실행 실패: ${err.message}`);
    }
  } else {
    result.warnings.push('pdftotext 없음 (apt install poppler-utils). 텍스트 추출 확인 생략.');
  }

  // pdftohtml (hyperlink 확인)
  if (commandExists('pdftohtml')) {
    try {
      const tmpBase = `/tmp/html_to_pdf_check_${Date.now()}`;
      execSync(`pdftohtml -xml "${pdfPath}" "${tmpBase}" 2>/dev/null`);
      const xmlPath = tmpBase + '.xml';
      if (fs.existsSync(xmlPath)) {
        const xmlContent = fs.readFileSync(xmlPath, 'utf8');
        const matches = xmlContent.match(/<a /g);
        result.hyperlinkCount = matches ? matches.length : 0;
        if (result.hyperlinkCount === 0) {
          result.warnings.push('hyperlink 0건. <a href> annotation 누락. troubleshooting.md "hyperlink 손실" 섹션 참조.');
        }
        console.log(`[검증] hyperlink: ${result.hyperlinkCount}개`);
        // 임시 파일 정리
        try { execSync(`rm -f "${tmpBase}"* 2>/dev/null`); } catch (_) { /* 무시 */ }
      }
    } catch (err) {
      result.warnings.push(`pdftohtml 실행 실패: ${err.message}`);
    }
  } else {
    result.warnings.push('pdftohtml 없음 (apt install poppler-utils). hyperlink 확인 생략.');
  }

  return result;
}

function commandExists(cmd) {
  try {
    execSync(`which ${cmd} 2>/dev/null`, { stdio: 'pipe' });
    return true;
  } catch (_err) {
    return false;
  }
}

// ---------------------------------------------------------------------------
// CLI 진입점
// ---------------------------------------------------------------------------

async function main() {
  const opts = parseArgs(process.argv);

  if (!opts.input) {
    console.error('사용법: node convert.js --input=<html경로> [--output=<pdf경로>] [옵션...]');
    console.error('');
    console.error('옵션:');
    console.error('  --input=<경로>                HTML 파일 경로 (필수)');
    console.error('  --output=<경로>               출력 PDF 경로 (기본: input에 .pdf)');
    console.error('  --page-size=<크기>            16:9 | A4 | A3 | WxH (기본: 16:9)');
    console.error('  --landscape=<bool>            true|false (기본: true)');
    console.error('  --page-break-selector=<css>   페이지 분리 셀렉터 (기본: .slide-wrapper)');
    console.error('  --font-wait-ms=<ms>           폰트 대기 시간 (기본: 2500)');
    console.error('  --no-validation               검증 단계 생략');
    process.exit(1);
  }

  try {
    const { outputPath, validationResult } = await htmlToPdf({
      inputPath: opts.input,
      outputPath: opts.output,
      pageSize: opts['page-size'] || '16:9',
      landscape: opts.landscape !== 'false',
      pageBreakSelector: opts['page-break-selector'] || '.slide-wrapper',
      fontWaitMs: opts['font-wait-ms'] ? parseInt(opts['font-wait-ms'], 10) : 2500,
      printBackground: opts['print-background'] !== 'false',
      noValidation: opts['no-validation'] === 'true',
      timeout: opts.timeout ? parseInt(opts.timeout, 10) : 90000,
    });

    console.log('');
    console.log('=== 변환 완료 ===');
    console.log(`출력: ${outputPath}`);
    if (validationResult.fileSize) console.log(`크기: ${validationResult.fileSize}`);
    if (validationResult.pages !== null) console.log(`페이지: ${validationResult.pages}`);
    if (validationResult.textChars !== null) console.log(`텍스트: ${validationResult.textChars}자`);
    if (validationResult.hyperlinkCount !== null) console.log(`hyperlink: ${validationResult.hyperlinkCount}개`);
    if (validationResult.warnings && validationResult.warnings.length > 0) {
      console.log('');
      console.log('=== 경고 ===');
      for (const w of validationResult.warnings) console.warn(`WARN: ${w}`);
    }
  } catch (err) {
    console.error(`[html-to-pdf] 오류: ${err.message}`);
    process.exit(1);
  }
}

// 직접 실행 시 main() 호출
if (require.main === module) {
  main();
}

module.exports = { htmlToPdf };
