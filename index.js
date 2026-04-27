const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// function createWindow () {
//   const win = new BrowserWindow({
//    fullscreen: true,
//     width: 1920,
//     height: 1080,
//     webPreferences: {
//       nodeIntegration: true,   // Node.js 사용 허용
//       contextIsolation: false, // Electron 12 이후 필요
//     }
//   });

//   win.loadFile('html/index.html');
// }


// app.whenReady().then(createWindow);

// ipcMain.on('app-quit', () => {
//   app.quit();
// });


let mainWindow;
let musicWindow;

app.whenReady().then(() => {
  // 메인 윈도우
  mainWindow = new BrowserWindow({
    fullscreen: true,
    width: 1920,
    height: 1080,
    webPreferences: {
      nodeIntegration: true,   // Node.js 사용 허용
      contextIsolation: false, // Electron 12 이후 필요
    }
  });

  mainWindow.loadFile('html/index.html');

  // 숨겨진 음악 윈도우
  musicWindow = new BrowserWindow({
    show: false,
     webPreferences: {
      nodeIntegration: true,     // ✅ 필수: require() 허용
      contextIsolation: false,   // ✅ 필수: ipcRenderer 접근 가능하게
    }
  });

  musicWindow.loadFile('html/music-player.html');

   mainWindow.on('closed', () => {
    if (musicWindow && !musicWindow.isDestroyed()) {
      musicWindow.close();
    }
    musicWindow = null;
    mainWindow = null;
  });
});

ipcMain.on('volume-change', (event, volume) => {
        if (musicWindow && musicWindow.webContents) {
            musicWindow.webContents.send('set-volume', volume);  // 📥 musicWindow에 전달
        }
    });

app.on('window-all-closed', () => {
  app.quit();
});


ipcMain.on('app-quit', () => {
  app.quit();
});
