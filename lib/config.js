// lib/config.js
// Shared configuration for LDR components

const config = {
  DEFAULT_PORT: 3333,
  DEFAULT_HOST: 'localhost'
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = config;
} else if (typeof window !== 'undefined') {
  window.LdrConfig = config;
}
