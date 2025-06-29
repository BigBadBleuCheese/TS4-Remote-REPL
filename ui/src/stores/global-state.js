import { createGlobalState, useStorage } from '@vueuse/core';

export const usePersistedState = createGlobalState(() => useStorage('ts4-remote-repl', {
    code: '# Python code',
    mode: 'eval',
}, localStorage));
