#!/usr/bin/env node

/**
 * Script untuk memverifikasi semua dependencies terinstall dengan benar
 * Jalankan: node verify-deps.js
 */

const fs = require('fs');
const path = require('path');

const requiredDeps = [
  '@radix-ui/react-slot',
  '@tanstack/react-query',
  'class-variance-authority',
  'clsx',
  'framer-motion',
  'lucide-react',
  'next',
  'next-themes',
  'react',
  'react-dom',
  'react-markdown',
  'tailwind-merge',
  'tailwindcss-animate'
];

console.log('🔍 Checking dependencies...\n');

let allGood = true;

requiredDeps.forEach(dep => {
  try {
    const depPath = path.join(__dirname, 'node_modules', dep);
    if (fs.existsSync(depPath)) {
      console.log(`✅ ${dep}`);
    } else {
      console.log(`❌ ${dep} - NOT FOUND`);
      allGood = false;
    }
  } catch (err) {
    console.log(`❌ ${dep} - ERROR: ${err.message}`);
    allGood = false;
  }
});

console.log('\n' + '='.repeat(50));

if (allGood) {
  console.log('✅ All dependencies are installed correctly!');
  process.exit(0);
} else {
  console.log('❌ Some dependencies are missing!');
  console.log('\nRun: npm install');
  process.exit(1);
}
