// Renders the fixed narrator "Amar" into 4 PNG states.
// Usage: node build_mascot.js  (needs: npm i @resvg/resvg-js)
const fs = require('fs');
const path = require('path');
const { Resvg } = require('@resvg/resvg-js');

const tpl = fs.readFileSync(path.join(__dirname, 'mascot_template.svg'), 'utf8');

const EYES_OPEN = `
  <ellipse cx="245" cy="280" rx="30" ry="36" fill="#fff"/>
  <ellipse cx="355" cy="280" rx="30" ry="36" fill="#fff"/>
  <circle cx="250" cy="286" r="19" fill="#2B1B12"/>
  <circle cx="350" cy="286" r="19" fill="#2B1B12"/>
  <circle cx="257" cy="278" r="7" fill="#fff"/>
  <circle cx="357" cy="278" r="7" fill="#fff"/>`;
const EYES_BLINK = `
  <path d="M215 286 Q245 300 275 286" stroke="#2B1B12" stroke-width="8" fill="none" stroke-linecap="round"/>
  <path d="M325 286 Q355 300 385 286" stroke="#2B1B12" stroke-width="8" fill="none" stroke-linecap="round"/>`;
const MOUTH_CLOSED = `
  <path d="M262 350 Q300 380 338 350" stroke="#7A2E1D" stroke-width="8" fill="none" stroke-linecap="round"/>`;
const MOUTH_OPEN = `
  <path d="M258 345 Q300 345 342 345 Q338 405 300 408 Q262 405 258 345 Z" fill="#7A2E1D"/>
  <path d="M276 388 Q300 372 324 388 Q314 404 300 405 Q286 404 276 388 Z" fill="#E86A6A"/>
  <rect x="270" y="345" width="60" height="10" rx="4" fill="#fff"/>`;

const states = {
  idle: [EYES_OPEN, MOUTH_CLOSED],
  talk: [EYES_OPEN, MOUTH_OPEN],
  blink: [EYES_BLINK, MOUTH_CLOSED],
  blink_talk: [EYES_BLINK, MOUTH_OPEN],
};

for (const [name, [eyes, mouth]] of Object.entries(states)) {
  const svg = tpl.replace('{EYES}', eyes).replace('{MOUTH}', mouth);
  const png = new Resvg(svg, { fitTo: { mode: 'width', value: 600 }, background: 'rgba(0,0,0,0)' }).render().asPng();
  fs.writeFileSync(path.join(__dirname, `amar_${name}.png`), png);
  console.log('wrote', `amar_${name}.png`);
}
