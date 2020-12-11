const dhash = require('dhash-image');
const blocked = require('blocked-at')

const imagePath = "C:\\Users\\ShadowMoose\\Pictures\\World Map - Edited.png";
const image2 = "C:\\Users\\ShadowMoose\\Pictures\\D&D Campaign Map.jpg";

blocked((time, stack) => {
	console.log(`Blocked for ${time}ms, operation started here:`, stack)
}, {threshold: 4})


console.time('dhash');
dhash(imagePath, 8).then(async res => {
	console.timeEnd('dhash');
	const hex = res.toString('hex');
	const hex2 = (await dhash(image2, 8)).toString('hex');
	console.log('d-hash-1:', hex, hex.length);
	console.log('d-hash-2:', hex2, hex2.length);
	console.log('Hamming:', hammingDist(hex, hex2))
}).catch(console.error);


const fs = require('fs');
const crypto = require('crypto');


function checksumFile(hashName, path) {
	return new Promise((resolve, reject) => {
		const hash = crypto.createHash(hashName);
		const stream = fs.createReadStream(path);
		stream.on('error', err => reject(err));
		stream.on('data', chunk => hash.update(chunk));
		stream.on('end', () => resolve(hash.digest('hex')));
	});
}

checksumFile('sha256', imagePath).then (hash => {
	console.log('Full hash:', hash, hash.length);
})


function hammingDist(str1, str2) {
	let diff = 0;
	for (let idx = 0; idx < str1.length; idx ++) {
		if (str1[idx] !== str2[idx]) diff++;
	}
	return diff;
}
