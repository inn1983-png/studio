const fs = require('fs')
const path = require('path')

const distElectron = path.join(__dirname, '..', 'dist-electron')

if (!fs.existsSync(distElectron)) {
  fs.mkdirSync(distElectron, { recursive: true })
}

fs.copyFileSync(
  path.join(__dirname, '..', 'electron', 'main.cjs'),
  path.join(distElectron, 'main.cjs')
)

fs.copyFileSync(
  path.join(__dirname, '..', 'electron', 'preload.cjs'),
  path.join(distElectron, 'preload.cjs')
)

console.log('Electron files copied to dist-electron/')
