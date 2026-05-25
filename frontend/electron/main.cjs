const { app, BrowserWindow, session, dialog, ipcMain } = require('electron')
const path = require('path')

const isDev = !app.isPackaged

let mainWindow = null

ipcMain.on('get-app-version', (event) => {
  event.returnValue = app.getVersion()
})

if (!isDev) {
  try {
    const { autoUpdater } = require('electron-updater')
    autoUpdater.autoDownload = false
    autoUpdater.autoInstallOnAppQuit = true

    autoUpdater.on('update-available', (info) => {
      dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: '发现新版本',
        message: `发现新版本 v${info.version}，是否立即下载？`,
        buttons: ['下载', '稍后提醒'],
        defaultId: 0,
        cancelId: 1
      }).then(({ response }) => {
        if (response === 0) {
          autoUpdater.downloadUpdate()
        }
      })
    })

    autoUpdater.on('update-downloaded', (info) => {
      dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: '更新已下载',
        message: `新版本 v${info.version} 已下载完成，重启应用以完成安装。`,
        buttons: ['立即重启', '稍后'],
        defaultId: 0,
        cancelId: 1
      }).then(({ response }) => {
        if (response === 0) {
          autoUpdater.quitAndInstall()
        }
      })
    })

    autoUpdater.on('error', (err) => {
      console.error('Auto-update error:', err.message)
    })

    autoUpdater.on('download-progress', (progressInfo) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.setProgressBar(progressInfo.percent / 100)
      }
    })

    ipcMain.on('check-for-updates', () => {
      autoUpdater.checkForUpdates().catch(() => {})
    })

    app.on('ready', () => {
      setTimeout(() => {
        autoUpdater.checkForUpdates().catch(() => {})
      }, 5000)
    })
  } catch (e) {
    console.log('electron-updater not available, skipping auto-update')
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    title: 'Txtovideo Studio',
    icon: path.join(__dirname, 'icon.svg'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.cjs')
    }
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})

app.whenReady().then(() => {
  createWindow()

  session.defaultSession.on('will-download', (event, item) => {
    const downloadsPath = app.getPath('downloads')
    const filePath = dialog.showSaveDialogSync(mainWindow, {
      defaultPath: path.join(downloadsPath, item.getFilename()),
      title: '保存文件'
    })
    if (filePath) {
      item.setSavePath(filePath)
    } else {
      item.cancel()
    }
  })
})
