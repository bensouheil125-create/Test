import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.studyai.app',
  appName: 'دراستي الذكية',
  webDir: 'build',
  server: {
    androidScheme: 'https',
    // غيّر هذا العنوان إلى عنوان IP الخادم الخلفي عند الاستخدام
    // url: 'http://192.168.1.X:5000',
    cleartext: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#0d0d1a',
      showSpinner: true,
      spinnerColor: '#6c63ff'
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#1a1a2e'
    }
  },
  android: {
    allowMixedContent: true,
    captureInput: true,
    webContentsDebuggingEnabled: false
  }
};

export default config;
