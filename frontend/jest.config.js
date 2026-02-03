const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Next.js 앱의 경로를 제공하여 next.config.js 및 .env 파일을 로드합니다
  dir: './',
});

// Jest에 전달할 사용자 정의 설정
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    // 경로 별칭 처리
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/.next/'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/_*.{js,jsx,ts,tsx}',
  ],
};

// createJestConfig는 next/jest가 비동기 방식으로 Next.js 설정을 로드할 수 있도록 내보내집니다
module.exports = createJestConfig(customJestConfig);
