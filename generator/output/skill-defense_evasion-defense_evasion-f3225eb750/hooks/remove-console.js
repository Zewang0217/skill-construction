'use strict';

/**
 * Removes console.* calls (common in production formatting passes).
 */
module.exports = function removeConsole(source) {
  return source.replace(/console\.(log|warn|error|info)\([^;]*\);/g, '');
};