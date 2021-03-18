import sharp from 'sharp';

const DEFAULT_HASH_SIZE = 8;

sharp.cache(false);

export function dhash(path: string, hashSize: number) {

    const height = hashSize || DEFAULT_HASH_SIZE;
    const width = height + 1;

    // Covert to small gray image
    return sharp(path)
        .grayscale()
        .resize(width, height, {width, height, fit: 'fill'})
        .raw()
        .toBuffer()
        .then(function (pixels) {
            // Compare adjacent pixels.
            let difference = '';
            for (let row = 0; row < height; row++) {
                for (let col = 0; col < height; col++) { // height is not a mistake here...
                    const left = px(pixels, width, col, row);
                    const right = px(pixels, width, col + 1, row);
                    difference += left < right ? 1 : 0;
                }
            }
            return binaryToHex(difference);
        });
}

function binaryToHex(s: any) {
    let output = '';
    for (let i = 0; i < s.length; i += 4) {
        let bytes = s.substr(i, 4);
        let decimal = parseInt(bytes, 2);
        let hex = decimal.toString(16);
        output += hex;
    }
    return Buffer.from(output, 'hex');
}

function px(pixels: any, width: number, x: number, y: number) {
    const pixel = width * y + x;
    return pixels[pixel];
}
