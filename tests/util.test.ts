import promisePool, {mutex, sleep} from "../src/util/promise-pool";
import {Streamer} from "../src/util/streamer";


describe('Utility Tests', () => {
    it("promise pool throttles", async () => {
        const st = Date.now();
        let i = 8;
        const mk = (end: any) => {
            // burn one second pretending to do things.
            i-=1
            if (i < 0) return end();

            return sleep(1000);
        };

        await promisePool(mk, 2);
        expect(Date.now() - st).toBeGreaterThan(3999); // Took at least the correct amount of time.
        expect(Date.now() - st).toBeLessThan(5000); // Took at most the correct amount of time.
    });

    it('streamer delay', async() => {
        class Test {
            @Streamer.delay(1000)
            items: any[] = [];
            @Streamer.delay(1000)
            delayedItems: any[] = [];
            @Streamer.delay(1)
            other = true;
            nested = {
                test: 1,
                b: ['y']
            }
        }
        const streamer = new Streamer(new Test());
        const s = streamer.state;
        const spy = jest.fn();

        streamer.setSender(spy);

        s.items = [];
        s.items.push('ok');  // skipped
        s.delayedItems.push('delay me');
        s.other = false; // skipped
        s.other = true;
        s.nested.test = 100;
        s.nested.b.push('new');  // skipped
        delete s.nested.b;

        await sleep(500);
        expect(spy).toBeCalledTimes(3);  // Ensure that delayed updates are still pending.
        await sleep(1000);

        expect(spy).toBeCalledTimes(5);  // Ensure that all updates have gone through.
        expect(spy.mock.calls).toEqual([
            [{"deleted": false, "path": ["other"], "value": true}],
            [{"deleted": false, "path": ["nested", "test"], "value": 100}],
            [{"deleted": true, "path": ["nested", "b"]}],
            [{"deleted": false, "path": ["items"], "value": ["ok"]}],
            [{"deleted": false, "path": ["delayedItems", 0], "value": "delay me"}]
        ]);
        // @ts-ignore
        expect(streamer.pending).toEqual({ delayedItems: {}, nested: {} });
    });

    it('streamer debounce', async() => {
        class Test {
            @Streamer.throttle(10)
            items: any[] = [];
        }
        const streamer = new Streamer(new Test());
        const s = streamer.state;
        const spy = jest.fn();

        streamer.setSender(spy);

        s.items.push(1);
        await sleep(500)
        expect(spy).toBeCalledTimes(1);

        s.items.push('a');
        s.items.push('b');  // Pushed after the first alert, should flag as "dirty".
        await sleep(500);
        expect(spy).toBeCalledTimes(3);
    });

    it('streamer custom-metadata', async() => {
        class Test {
            @Streamer.delay(400)
            @Streamer.customMetadata('test')
            items: any[] = [];
        }
        const streamer = new Streamer(new Test());
        const s = streamer.state;
        let data: any = [];

        streamer.setSender((d)=>data.push(d.customMetadata));

        s.items.push(1);
        await sleep(100);
        expect(data.length).toEqual(0);
        await sleep(500);
        expect(data).toEqual(['test']);
    });

    it('mutex should work', async() => {
        let running = false;
        const fn = async (val: number) => {
            expect(running).toBeFalsy();
            running = true;
            await sleep(100);
            running = false;
            return val;
        }
        const mt = mutex(fn);
        const proms = [];
        const st = Date.now();
        for (let i = 0; i < 10; i++) {
            proms.push(mt(i));
        }
        const res = await Promise.all(proms);
        expect(Date.now() - st).toBeGreaterThan(999);
        expect(res).toMatchObject([0,1,2,3,4,5,6,7,8,9]);
    });
})
