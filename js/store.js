(function () {
  const fs = require('fs');
  const path = require('path');

  const STATE_DIR = 'C:/drawing_data';
  const STATE_FILE = path.join(STATE_DIR, 'state.json');

  function readAll() {
    try {
      if (fs.existsSync(STATE_FILE)) {
        return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
      }
    } catch (e) {
      console.warn('상태 로드 실패:', e);
    }
    return {};
  }

  function writeAll(state) {
    try {
      fs.mkdirSync(STATE_DIR, { recursive: true });
      fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
    } catch (e) {
      console.warn('상태 저장 실패:', e);
    }
  }

  window.persistentStorage = {
    getItem(key) {
      const state = readAll();
      if (key in state) {
        const v = state[key];
        return v === null || v === undefined ? null : String(v);
      }
      return null;
    },
    setItem(key, value) {
      const state = readAll();
      state[key] = value;
      writeAll(state);
    },
    removeItem(key) {
      const state = readAll();
      delete state[key];
      writeAll(state);
    }
  };
})();
