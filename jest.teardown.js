const fs = require('fs');

// Clean up all staged test data after all tests finish.

module.exports = async() => {
	// directory path
	const dir = './temp-test-data';

	if (!fs.existsSync(dir)) return;

	// delete directory recursively
	await fs.promises.rmdir(dir, { recursive: true }).catch(console.warn);
}
