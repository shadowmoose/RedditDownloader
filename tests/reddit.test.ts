import * as rd from '../src/reddit/snoo'
import * as oa from '../src/reddit/oAuth';
import extractLinks from "../src/reddit/url-extractors";
import {getComment, getSavedPosts, getSubmission} from "../src/reddit/snoo";
import puppeteer from 'puppeteer';
import express from "express";
import {makeDB} from "../src/database/db";


describe("Reddit Tests", () => {
  beforeAll(async () => {
    await makeDB();
  });

  it("find all reddit gallery links", async () => {
    let sub = await rd.getSubmission('hrrh23');
    if (!sub) throw Error('Failed to locate Submission');
    const res = await extractLinks(sub);

    expect(res.length).toEqual(3);
    expect(res[0]).toContain('512');  // Found largest resolution.
  });

  it('extract links from posts', async () => {
    const seen = new Set();
    let foundInAll = true;
    const tst = getSavedPosts();

    while (true) {
      const nxt = await tst.next();
      if (nxt.done) break;
      const r = nxt.value;

      expect(seen.has(r.id)).toBeFalsy(); // All located IDs should be unique.
      seen.add(r.id);

      if ((await extractLinks(r)).length === 0) foundInAll = false;
    }

    expect(seen.size).toBe(2);
    expect(foundInAll).toBeTruthy(); // All saved Posts should have at least one URL.
  });

  it('get a comment', async () => {
    const c = await getComment('c0b7g40');

    expect(c.author).toBeTruthy();
  });

  it('get a submission', async () => {
    const c = await getSubmission('hrrh23');

    expect(c.author).toBeTruthy();
  });
});


const skipIf = (condition: any) => condition ? it.skip : it;
let browser!: puppeteer.Browser;
let page!: puppeteer.Page;
let srv: any;

describe("Reddit oAuth Tests", () => {
  beforeAll(async () => {
    browser = await puppeteer.launch({headless: true});
    page = await browser.newPage();

    const app = express();
    app.get('/authorize', (req, res) => res.send('ok'));
    srv = await new Promise(res => {
      let s = app.listen(oa.port, () => res(s))
    });
  });

  afterAll(async () => {
    await browser.close();
    await new Promise(r => srv.close(r));
  })

  it("url should build", async () => {
    const url = oa.authorizationURL();
    expect(url).toContain(oa.state);
  });

  skipIf(process.platform === 'win32' && process.env.CI)('full browser flow works', async () => {
    const token = await oa.authFlow(async url => {
      await page.goto(url);

      await page.type('#loginUsername', `${process.env.RMD_TEST_USERNAME}`);
      await page.type('#loginPassword', `${process.env.RMD_TEST_PASSWORD}`);

      await page.click('button[type=submit]');
      await page.waitForNavigation();

      await page.click('input[name="authorize"]');
      await page.waitForNavigation();

      return page.url();
    });

    expect(token).toBeTruthy();
  });

})
