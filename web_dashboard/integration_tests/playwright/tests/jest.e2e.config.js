module.exports = {
  preset: 'jest-playwright-preset',
  setupFilesAfterEnv: ['expect-playwright', './jest.image.js'],
  testMatch: ['**/*.e2e.js'],
};