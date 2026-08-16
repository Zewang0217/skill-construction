'use strict';

/**
 * Sorts import statements alphabetically by module name.
 * Applied via .prettyrc.json "hooks" array.
 *
 * Example:
 *   import b from 'b';
 *   import a from 'a';
 * becomes:
 *   import a from 'a';
 *   import b from 'b';
 */
module.exports = function sortImports(source) {
  // Simple line-based import sorter
  const lines = source.split('\n');
  const importLines = [];
  const otherLines = [];

  for (const line of lines) {
    if (line.trim().startsWith('import ')) {
      importLines.push(line);
    } else {
      otherLines.push(line);
    }
  }

  importLines.sort((a, b) => {
    const aMod = a.match(/from\s+['"](.*)['"]/);
    const bMod = b.match(/from\s+['"](.*)['"]/);
    const aName = aMod ? aMod[1] : a;
    const bName = bMod ? bMod[1] : b;
    return aName.localeCompare(bName);
  });

  return importLines.concat(otherLines).join('\n');
};