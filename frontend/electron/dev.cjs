const { spawn } = require('child_process')
const path = require('path')

const electronPath = require('electron')

const child = spawn(electronPath, [path.join(__dirname, 'main.cjs'), '--no-sandbox'], {
  stdio: 'inherit',
  env: { ...process.env, ELECTRON_DISABLE_SECURITY_WARNINGS: 'true' }
})

child.on('exit', (code) => {
  process.exit(code)
})

process.on('SIGINT', () => {
  child.kill()
  process.exit(0)
})
