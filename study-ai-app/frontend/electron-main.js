/**
 * Electron Main Process
 * لتشغيل التطبيق على Windows 7/8/10/11
 *
 * التشغيل:
 * 1. npm run build
 * 2. npx electron .
 */
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 420,
    height: 800,
    minWidth: 380,
    minHeight: 700,
    title: 'دراستي الذكية',
    icon: path.join(__dirname, 'public', 'favicon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    backgroundColor: '#0d0d1a'
  });

  // تحميل ملفات React المبنية
  win.loadFile(path.join(__dirname, 'build', 'index.html'));

  // إخفاء شريط القوائم
  win.setMenuBarVisibility(false);
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
