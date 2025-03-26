const fs = require('fs-extra');
const path = require('path');

const sourceDir = path.join(__dirname, '../../data');
const targetDir = path.join(__dirname, '../public/data');

async function copyData() {
  try {
    await fs.copy(sourceDir, targetDir);
    console.log('Data directory copied successfully!');
  } catch (err) {
    console.error('Error copying data directory:', err);
    process.exit(1);
  }
}

copyData(); 