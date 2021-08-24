import * as rd from '../src/engine/reddit/snoo'
import * as oa from '../src/engine/reddit/oAuth';
import extractLinks from "../src/engine/reddit/url-extractors";
import {getComment, getSavedPosts, getSubmission} from "../src/engine/reddit/snoo";
import puppeteer from 'puppeteer';
import express from "express";
import * as ps from '../src/engine/reddit/pushshift';
import {forGen} from "../src/engine/util/generator-util";
import {makeDB} from "../src/engine/database/db";


describe("Reddit Tests", () => {
  beforeEach(async () => {
    const conn = await makeDB();
    await conn.synchronize(true);  // Rerun sync to drop & recreate existing tables.
  });

  it("builds reddit gallery link", async () => {
    let sub = await rd.getSubmission('hrrh23');
    if (!sub) throw Error('Failed to locate Submission');
    const res = await extractLinks(sub);

    expect(res.length).toEqual(1);
    expect(res[0]).toEqual('https://www.reddit.com/gallery/hrrh23');  // Found largest resolution.
  });

  it('extract links from posts', async () => {
    const seen = new Set();
    let foundInAll = true;
    const tst = getSavedPosts(0);

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

  it("find selfpost urls", async () => {
    let sub = await getSubmission('ffit3j');
    if (!sub) throw Error('Failed to locate Submission');
    const res = await extractLinks(sub);

    expect(res.length).toEqual(39);
  })
});


describe('PushShift Tests', () => {
  it('User ps comments', async() => {
    const seen = new Set();
    const count = await forGen(ps.getUserComments('theshadowmoose'), p => {
      expect(seen.has(p.id)).toBeFalsy();  // No duplicates should be yielded per-scan.
      seen.add(p.id);
    });

    expect(count).toBeGreaterThan(190);
  });

  it("builds ps reddit gallery link", async () => {
    let sub = await ps.getSubmission('hrrh23');
    if (!sub) throw Error('Failed to locate Submission');
    const res = await extractLinks(sub);

    expect(res.length).toEqual(1);
    expect(res[0]).toEqual('https://www.reddit.com/gallery/hrrh23');  // Found largest resolution.
  });

  it('User ps submissions', async() => {
    const seen = new Set();
    const count = await forGen(ps.getUserSubmissions('theshadowmoose'), p => {
      expect(seen.has(p.id)).toBeFalsy();  // No duplicates should be yielded per-scan.
      seen.add(p.id);
    });

    expect(count).toBeGreaterThan(7);
  })

  it('Subreddit ps submissions', async() => {
    const count = await forGen(ps.getSubredditSubmissions('pathofexile', 10), _p => {});

    expect(count).toEqual(10);
  })

  it("find ps selfpost urls", async () => {
    let sub = await ps.getSubmission('ffit3j');
    if (!sub) throw Error('Failed to locate Submission');
    const res = await extractLinks(sub);

    expect(res.length).toEqual(30);
  })

  it("find comment link", async () => {
    let comm = await ps.getComment('fenll1l');
    if (!comm) throw Error('Failed to locate Comment');
    const res = await extractLinks(comm);

    expect(res.length).toEqual(1);
    expect(res[0]).toEqual('https://github.com/shadowmoose/RedditDownloader');
  })

  it("submissions are equal", async () => {
    let pssub: any = await ps.getSubmission('8ewkx2');
    let rsub: any = await getSubmission('8ewkx2');

    delete pssub['loadedData'];
    delete rsub['loadedData'];
    delete pssub['firstFoundUTC'];
    delete rsub['firstFoundUTC'];
    delete pssub['score'];
    delete rsub['score'];
    delete pssub['fromPushshift'];
    delete rsub['fromPushshift'];

    expect(JSON.stringify(pssub, null, 4)).toEqual(JSON.stringify(rsub, null, 4));
  })

  it("comments are equal", async () => {
    let pssub: any = await ps.getComment('egna1xi');
    let rsub: any = await getComment('egna1xi');

    delete pssub['loadedData'];
    delete rsub['loadedData'];
    delete pssub['firstFoundUTC'];
    delete rsub['firstFoundUTC'];
    delete pssub['score'];
    delete rsub['score'];
    delete pssub['fromPushshift'];
    delete rsub['fromPushshift'];

    expect(JSON.stringify(pssub, null, 4)).toEqual(JSON.stringify(rsub, null, 4));
  })
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
