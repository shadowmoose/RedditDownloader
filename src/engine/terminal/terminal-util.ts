import readline from 'readline';

export async function simplePrompt(text: string): Promise<string> {
    return new Promise(res => {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        rl.question(text+' ', function(r: string) {
            res(r);
            rl.close();
        });
    })
}
