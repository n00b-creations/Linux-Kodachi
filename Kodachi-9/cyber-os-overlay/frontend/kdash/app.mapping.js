(function (root) {
  'use strict';
  const CATEGORIES = Object.freeze(['home', 'system', 'vcs', 'network', 'ui', 'misc']);
  const CATEGORY_SET = new Set(CATEGORIES);
  function unquote(value) {
    const trimmed = value.trim();
    if (trimmed.length >= 2 && ((trimmed[0] === '"' && trimmed[trimmed.length - 1] === '"') || (trimmed[0] === "'" && trimmed[trimmed.length - 1] === "'"))) return trimmed.slice(1, -1);
    return trimmed;
  }
  function parseNodeMap(text) {
    if (typeof text !== 'string') throw new TypeError('Mapping must be text.');
    const lines = text.split(/\r?\n/);
    const hasSection = lines.some(function (line) { return /^\s*node_map\s*:\s*(?:#.*)?$/.test(line); });
    let inNodeMap = !hasSection;
    const map = Object.create(null);
    for (const line of lines) {
      const content = line.split('#', 1)[0];
      const trimmed = content.trim();
      if (!trimmed) continue;
      if (/^node_map\s*:$/.test(trimmed)) { inNodeMap = true; continue; }
      if (hasSection && inNodeMap && !/^\s/.test(line)) inNodeMap = false;
      if (!inNodeMap) continue;
      const colon = trimmed.indexOf(':');
      if (colon <= 0) throw new Error('Expected node_fragment: category.');
      const key = unquote(trimmed.slice(0, colon));
      const category = unquote(trimmed.slice(colon + 1)).toLowerCase();
      if (!key || /[\r\n]/.test(key)) throw new Error('Mapping node names cannot be empty or multiline.');
      if (!CATEGORY_SET.has(category)) throw new Error('Unsupported category: ' + category);
      map[key] = category;
    }
    return map;
  }
  function categoryForNode(name, map) {
    const lowerName = String(name || '').toLowerCase();
    for (const entry of Object.entries(map || {})) {
      const fragment = entry[0];
      if (fragment && lowerName.includes(fragment.toLowerCase())) return entry[1];
    }
    return null;
  }
  function stringifyNodeMap(map) {
    const lines = ['# Node-name fragments mapped to dashboard categories', 'node_map:'];
    for (const entry of Object.entries(map || {})) {
      const key = entry[0];
      const category = String(entry[1] || '').toLowerCase();
      if (!key || /[\r\n]/.test(key) || key.includes(':') || key.includes('#')) throw new Error('Node names cannot contain newlines, colons, or # characters.');
      if (!CATEGORY_SET.has(category)) throw new Error('Unsupported category: ' + category);
      lines.push('  ' + key + ': ' + category);
    }
    return lines.join('\n') + '\n';
  }
  root.KdashMapping = Object.freeze({categories:CATEGORIES, parseNodeMap:parseNodeMap, categoryForNode:categoryForNode, stringifyNodeMap:stringifyNodeMap});
})(globalThis);
