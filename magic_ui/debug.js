const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  
  // Capture all console messages
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

  console.log("Navigating to http://localhost:8502...");
  await page.goto('http://localhost:8502', { waitUntil: 'networkidle2' });

  // Wait for the admin tab to be clickable
  console.log("Looking for Admin tab...");
  await page.waitForTimeout(2000);
  
  // To avoid complex selectors, we can just grab all iframes and see if they contain errors
  console.log("Checking iframes...");
  const frames = page.frames();
  for (const frame of frames) {
    console.log("Frame URL:", frame.url());
    if (frame.url().includes('component/magic_hub')) {
      const content = await frame.content();
      console.log("Magic Hub iframe found! Size:", content.length);
      // Let's print a small snippet
      console.log("Content snippet:", content.substring(0, 500));
    }
  }

  await browser.close();
})();
