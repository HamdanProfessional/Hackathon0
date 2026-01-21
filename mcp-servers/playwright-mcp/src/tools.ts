/**
 * MCP Tool Definitions for Playwright Browser Automation
 */

import { BrowserManager } from "./browser.js";

export interface Tool {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, {
      type: string;
      description: string;
    }>;
    required?: string[];
  };
  handler: (browser: BrowserManager, args: any) => Promise<string>;
}

export const tools: Tool[] = [
  {
    name: "navigate",
    description: "Navigate to a URL in the browser",
    inputSchema: {
      type: "object",
      properties: {
        url: {
          type: "string",
          description: "URL to navigate to",
        },
        waitUntil: {
          type: "string",
          description: "Wait condition: load, domcontentloaded, networkidle",
        },
      },
      required: ["url"],
    },
    handler: async (browser, args) => {
      const page = await browser.getCurrentPage();
      const waitUntil: string = args.waitUntil || "load";

      await page.goto(args.url, { waitUntil });
      const title = await page.title();

      return `Navigated to: ${title} (${args.url})`;
    },
  },

  {
    name: "get_page_text",
    description: "Extract all visible text from the current page",
    inputSchema: {
      type: "object",
      properties: {},
    },
    handler: async (browser) => {
      const page = await browser.getCurrentPage();
      const text = await page.evaluate(() => document.body.innerText);

      const charCount = text.length;
      const wordCount = text.split(/\s+/).filter((w: string) => w.length > 0).length;

      return `Page text (${charCount} chars, ${wordCount} words):\n\n${text.substring(0, 5000)}${text.length > 5000 ? '\n\n[...truncated...]' : ''}`;
    },
  },

  {
    name: "click",
    description: "Click an element by CSS selector",
    inputSchema: {
      type: "object",
      properties: {
        selector: {
          type: "string",
          description: "CSS selector for the element to click",
        },
        button: {
          type: "string",
          description: "Mouse button: left, right, or middle",
        },
      },
      required: ["selector"],
    },
    handler: async (browser, args) => {
      const page = await browser.getCurrentPage();

      await page.waitForSelector(args.selector, { timeout: 5000 });
      await page.click(args.selector, {
        button: args.button || 'left',
      });

      return `Clicked element: ${args.selector}`;
    },
  },

  {
    name: "type",
    description: "Type text into an element",
    inputSchema: {
      type: "object",
      properties: {
        selector: {
          type: "string",
          description: "CSS selector for the element",
        },
        text: {
          type: "string",
          description: "Text to type",
        },
        clear: {
          type: "boolean",
          description: "Clear the field before typing",
        },
        slow: {
          type: "boolean",
          description: "Type character by character with delay",
        },
      },
      required: ["selector", "text"],
    },
    handler: async (browser, args) => {
      const page = await browser.getCurrentPage();

      await page.waitForSelector(args.selector, { timeout: 5000 });

      if (args.clear) {
        await page.fill(args.selector, '');
      }

      if (args.slow) {
        await page.type(args.selector, args.text, { delay: 50 });
      } else {
        await page.fill(args.selector, args.text);
      }

      return `Typed text into: ${args.selector}`;
    },
  },

  {
    name: "snapshot",
    description: "Get accessibility tree snapshot of the current page",
    inputSchema: {
      type: "object",
      properties: {},
    },
    handler: async (browser) => {
      const page = await browser.getCurrentPage();
      const snapshot = await page.accessibility.snapshot();

      return `Page accessibility snapshot:\n\n${JSON.stringify(snapshot, null, 2)}`;
    },
  },

  {
    name: "evaluate",
    description: "Execute JavaScript in the page context",
    inputSchema: {
      type: "object",
      properties: {
        code: {
          type: "string",
          description: "JavaScript code to execute",
        },
      },
      required: ["code"],
    },
    handler: async (browser, args) => {
      const page = await browser.getCurrentPage();
      const result = await page.evaluate(args.code);

      return `Evaluation result: ${JSON.stringify(result, null, 2)}`;
    },
  },

  {
    name: "wait_for",
    description: "Wait for a condition or time",
    inputSchema: {
      type: "object",
      properties: {
        selector: {
          type: "string",
          description: "CSS selector to wait for",
        },
        time: {
          type: "number",
          description: "Time to wait in milliseconds",
        },
      },
    },
    handler: async (browser, args) => {
      const page = await browser.getCurrentPage();

      if (args.selector) {
        await page.waitForSelector(args.selector, { timeout: 30000 });
        return `Waited for selector: ${args.selector}`;
      } else if (args.time) {
        await page.waitForTimeout(args.time);
        return `Waited ${args.time}ms`;
      } else {
        throw new Error('Must specify either selector or time');
      }
    },
  },

  {
    name: "screenshot",
    description: "Take a screenshot of the current page",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "File path to save screenshot (relative or absolute)",
        },
        fullPage: {
          type: "boolean",
          description: "Take full page screenshot (including scroll)",
        },
      },
      required: ["path"],
    },
    handler: async (browser, args) => {
      const page = await browser.getCurrentPage();

      await page.screenshot({
        path: args.path,
        fullPage: args.fullPage ?? false,
      });

      return `Screenshot saved to: ${args.path}`;
    },
  },

  {
    name: "extract_links",
    description: "Extract all links from the current page",
    inputSchema: {
      type: "object",
      properties: {},
    },
    handler: async (browser) => {
      const page = await browser.getCurrentPage();
      const links = await page.evaluate(() => {
        const linkElements = document.querySelectorAll('a[href]');
        return Array.from(linkElements).map((a, index: number) => ({
          href: (a as any).href || '',
          text: (a as any).textContent?.trim() || '',
          title: (a as any).title || '',
        }));
      });

      const linkList = links.map((l: any, i: number) =>
        `${i + 1}. ${l.text || l.href} (${l.href})`
      ).join('\n');
      const count = links.length;

      return `Found ${count} links:\n\n${linkList}`;
    },
  },

  {
    name: "search_google",
    description: "Search Google and return result links",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query",
        },
        results: {
          type: "number",
          description: "Maximum number of results (default: 10)",
        },
      },
      required: ["query"],
    },
    handler: async (browser, args) => {
      const page = await browser.getCurrentPage();

      // Navigate to Google
      const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(args.query)}&tbs=qdr:d30`;
      await page.goto(searchUrl, { waitUntil: 'domcontentloaded' });

      // Wait for results
      await page.waitForSelector('div#search', { timeout: 10000 });

      // Extract search results
      const results = await page.evaluate(() => {
        const resultDivs = document.querySelectorAll('div.g');
        return Array.from(resultDivs).map((div, index: number) => {
          const linkEl = div.querySelector('a') as HTMLAnchorElement | null;
          const titleEl = div.querySelector('h3');

          if (linkEl && titleEl) {
            return {
              url: linkEl.href,
              title: titleEl.textContent?.trim() || '',
              snippet: div.textContent?.replace(titleEl.textContent || '', '').trim().substring(0, 200),
            };
          }
          return null;
        }).filter((r) => r !== null);
      });

      const maxResults = args.results || 10;
      const limitedResults = results.slice(0, maxResults);

      const resultList = limitedResults.map((r: any, i: number) =>
        `${i + 1}. ${r.title}\n   ${r.url}\n   ${r.snippet}`
      ).join('\n\n');

      return `Found ${limitedResults.length} search results:\n\n${resultList}`;
    },
  },
];
