const SCREENSHOT_COMPARISON_CONFIG = {
  diffDirection: 'vertical',
  // setting to true is useful on CI (no need to retrieve the diff image, copy/paste image content from logs)
  dumpDiffToConsole: false,
  // use SSIM to limit false positive
  // https://github.com/americanexpress/jest-image-snapshot#recommendations-when-using-ssim-comparison
  comparisonMethod: 'ssim',
  failureThreshold: 0.005,
  failureThresholdType: 'percent'
};

module.exports = {
  SCREENSHOT_COMPARISON_CONFIG
};