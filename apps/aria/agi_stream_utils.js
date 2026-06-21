/* AGI SSE stream utilities for client-side consumption. */

(function (global) {
  function safeJsonParse(s) {
    try {
      return JSON.parse(s);
    } catch (e) {
      return null;
    }
  }

  function parseSSEText(text) {
    if (typeof text !== 'string') return [];
    var events = text.split('\n\n').filter(function (e) { return e.trim(); });
    var deltas = [];
    events.forEach(function (ev) {
      var lines = ev.split('\n');
      for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.indexOf('data: ') === 0) {
          var jsonPart = line.slice(6);
          var payload = safeJsonParse(jsonPart);
          if (payload && payload.delta) deltas.push(payload.delta);
        }
      }
    });
    return deltas;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function prettyPrintDelta(delta) {
    if (!delta || typeof delta !== 'object') return '';
    var t = delta.type;
    var d = delta.data;
    switch (t) {
      case 'analysis':
        return '<div class="agi-analysis">' + escapeHtml(String(d)) + '</div>';
      case 'step':
        return '<div class="agi-step"><pre>' + escapeHtml(JSON.stringify(d, null, 2)) + '</pre></div>';
      case 'output':
        return '<span class="agi-output">' + escapeHtml(String(d)) + '</span>';
      case 'payload':
        return '<div class="agi-payload"><pre>' + escapeHtml(JSON.stringify(d, null, 2)) + '</pre></div>';
      case 'error':
        return '<div class="agi-error">Error: ' + escapeHtml(String(d)) + '</div>';
      default:
        return '<pre class="agi-unknown">' + escapeHtml(JSON.stringify(delta)) + '</pre>';
    }
  }

  global.AGIStreamUtils = {
    parseSSEText: parseSSEText,
    prettyPrintDelta: prettyPrintDelta,
    escapeHtml: escapeHtml,
  };
})(typeof window !== 'undefined' ? window : (typeof global !== 'undefined' ? global : this));
