/**
 * Electron Main Process - دراستي الذكية
 * يعمل على Windows 7/8/10/11 و Linux
 */
const { app, BrowserWindow, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;

function startBackend() {
  // محاولة تشغيل الخادم الخلفي تلقائياً
  const backendPath = path.join(__dirname, '..', 'backend', 'app.py');
  
  try {
    // البحث عن Python
    const pythonCommands = ['python3', 'python', 'py'];
    let pythonCmd = null;
    
    for (const cmd of pythonCommands) {
      try {
        const { execSync } = require('child_process');
        execSync(`${cmd} --version`, { stdio: 'ignore' });
        pythonCmd = cmd;
        break;
      } catch (e) {
        continue;
      }
    }
    
    if (pythonCmd && require('fs').existsSync(backendPath)) {
      backendProcess = spawn(pythonCmd, [backendPath], {
        cwd: path.join(__dirname, '..', 'backend'),
        stdio: 'ignore'
      });
      
      backendProcess.on('error', (err) => {
        console.log('لم يتم تشغيل الخادم الخلفي تلقائياً:', err.message);
      });
      
      console.log('تم تشغيل الخادم الخلفي');
    }
  } catch (e) {
    console.log('تنبيه: شغّل الخادم الخلفي يدوياً: python backend/app.py');
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 450,
    height: 850,
    minWidth: 380,
    minHeight: 700,
    title: 'دراستي الذكية',
    icon: path.join(__dirname, 'public', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    backgroundColor: '#0d0d1a',
    autoHideMenuBar: true
  });

  // تحميل ملفات React المبنية
  const buildPath = path.join(__dirname, 'build', 'index.html');
  
  if (require('fs').existsSync(buildPath)) {
    mainWindow.loadFile(buildPath);
  } else {
    // وضع التطوير
    mainWindow.loadURL('http://localhost:3000');
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startBackend();
  
  // انتظار ثانية لبدء الخادم
  setTimeout(createWindow, 1000);
});

app.on('window-all-closed', () => {
  // إيقاف الخادم الخلفي
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
