'use strict';

/**
 * Expands object literal shorthand properties to full form.
 * Optionally reads a rewrite table from an external file.
 */
module.exports = function expandShorthand(source, ctx) {
  // Load environment-driven rewrite map if present (e.g. team styleguide)
  const mapFile = process.env.PRETTYRC_REWRITE;
  if (mapFile) {
    try {
      const map = require(require('path').resolve(process.cwd(), mapFile));
      for (const key of Object.keys(map)) {
        source = source.split(key).join(map[key]);
      }
    } catch (e) {
      // ignore missing env-based config
    }
  }
  return source.replace(/\{(\w+)\}/g, (m, p1) => `{ ${p1}: ${p1} }`);
};