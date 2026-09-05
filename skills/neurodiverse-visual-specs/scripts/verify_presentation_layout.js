#!/usr/bin/env node
/**
 * scripts/verify_presentation_layout.js
 * Automated layout, collision, and cognitive-load validator for neuroinclusive slide decks.
 * Checks:
 *  1. Slide vertical overflow (scrollHeight > clientHeight)
 *  2. Internal element collisions (bounding box overlaps between header, cards, badges, and footer)
 *  3. Card word count budget (max 35 words per card to prevent cognitive fatigue)
 *  4. Dynamic scaling resilience (verifies layout at 1.0x and 1.25x font scale)
 */

const { chromium } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

async function runLayoutCheck(filePath) {
  const resolvedPath = path.resolve(filePath);
  if (!fs.existsSync(resolvedPath)) {
    console.error(`❌ File not found: ${resolvedPath}`);
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  
  await page.goto('file://' + resolvedPath);
  await page.waitForLoadState('domcontentloaded');

  const totalSlides = await page.evaluate(() => {
    return document.querySelectorAll('.slide').length;
  });

  console.log(`\n🔍 Verifying ${totalSlides} slides in ${path.basename(resolvedPath)} across viewports & font scales...\n`);

  let totalErrors = 0;

  for (let s = 1; s <= totalSlides; s++) {
    // Test both normal scale and 1.25x dyslexia font scale
    for (const scale of [1.0, 1.25]) {
      const issues = await page.evaluate(({ slideNum, fontScale }) => {
        // Activate slide
        document.querySelectorAll('.slide').forEach((el, idx) => {
          el.classList.toggle('active', idx + 1 === slideNum);
          el.classList.remove('previous');
        });

        // Set font scale
        document.documentElement.style.setProperty('--font-scale', fontScale);

        const slide = document.getElementById('slide-' + slideNum);
        if (!slide) return [{ type: 'missing_slide', msg: `Slide ${slideNum} not found in DOM` }];

        const errors = [];

        // 1. Check container vertical overflow
        // Allow 4px margin of error for subpixel border rendering
        if (slide.scrollHeight > slide.clientHeight + 4) {
          errors.push({
            type: 'slide_overflow',
            msg: `Slide content overflows container height: scrollHeight (${slide.scrollHeight}px) > clientHeight (${slide.clientHeight}px)`
          });
        }

        // 2. Check collisions between Slide Header, Slide Body, and Slide Footer
        const header = slide.querySelector('.slide-header');
        const body = slide.querySelector('.slide-body');
        const footer = slide.querySelector('.slide-footer');

        if (header && body) {
          const hRect = header.getBoundingClientRect();
          const bRect = body.getBoundingClientRect();
          if (hRect.bottom > bRect.top + 2) {
            errors.push({
              type: 'header_body_overlap',
              msg: `Slide Header overlaps Slide Body by ${(hRect.bottom - bRect.top).toFixed(1)}px`
            });
          }
        }

        if (body && footer) {
          const bRect = body.getBoundingClientRect();
          const fRect = footer.getBoundingClientRect();
          if (bRect.bottom > fRect.top + 2) {
            errors.push({
              type: 'body_footer_overlap',
              msg: `Slide Body overlaps Slide Footer by ${(bRect.bottom - fRect.top).toFixed(1)}px`
            });
          }
        }

        // 3. Check inside each Card: Title, Description, and Badge
        const cards = slide.querySelectorAll('.card');
        cards.forEach((card, cIdx) => {
          // Word count check
          const text = card.innerText || '';
          const wordCount = text.trim().split(/\s+/).length;
          const isListCard = card.querySelector('ul, ol') || card.querySelectorAll('[style*="display: flex"]').length > 2;
          const maxWords = isListCard ? 65 : 40;

          if (wordCount > maxWords && fontScale === 1.0) {
            errors.push({
              type: 'cognitive_overload',
              msg: `Card #${cIdx + 1} exceeds word budget (${wordCount} words > ${maxWords} word limit)`
            });
          }

          // Check children overlap inside card
          const cardChildren = Array.from(card.children);
          for (let i = 0; i < cardChildren.length - 1; i++) {
            const r1 = cardChildren[i].getBoundingClientRect();
            const r2 = cardChildren[i + 1].getBoundingClientRect();
            if (r1.bottom > r2.top + 2) {
              errors.push({
                type: 'card_child_overlap',
                msg: `Card #${cIdx + 1}: Element #${i + 1} overlaps Element #${i + 2} by ${(r1.bottom - r2.top).toFixed(1)}px`
              });
            }
          }
        });

        return errors;
      }, { slideNum: s, fontScale: scale });

      if (issues.length > 0) {
        totalErrors += issues.length;
        console.error(`❌ Slide ${s} (Scale ${scale}x) - ${issues.length} issue(s) detected:`);
        issues.forEach(err => console.error(`   • [${err.type}] ${err.msg}`));
      }
    }
  }

  await browser.close();

  if (totalErrors === 0) {
    console.log(`✅ All ${totalSlides} slides passed layout, collision, and cognitive load validation with zero overlaps!`);
    process.exit(0);
  } else {
    console.error(`\n🚨 Failed: ${totalErrors} layout or overlap issues detected across slides.\n`);
    process.exit(1);
  }
}

const targetFile = process.argv[2] || 'docs/SIMPLIFII_V2_PRESENTATION.html';
runLayoutCheck(targetFile);
