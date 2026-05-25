const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => ipcRenderer.sendSync('get-app-version'),
  platform: process.platform,
  checkForUpdates: () => ipcRenderer.send('check-for-updates')
})
