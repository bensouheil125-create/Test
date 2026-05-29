import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.studyai.app',
  appName: 'دراستي الذكية',
  webDir: 'build',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#0d0d1a',
      showSpinner: true,
      spinnerColor: '#6c63ff'
    }
  }
};

export default config;
