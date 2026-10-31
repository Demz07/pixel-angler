const fs = require('fs'), vm = require('vm');
const { MiniCanvas } = require('/home/user/assets/minicanvas.js');

const html = fs.readFileSync('/home/user/fishing-sim.html', 'utf8');
let js = html.match(/<script>([\s\S]*)<\/script>/)[1];
js += `
;globalThis.__test = {
  get state(){ return state; }, action, setBite(dt){ biteAt = tNow + dt; },
  setT(v){ T = v; }, get caught(){ return caught; }, setMove(d){ moveDir = d; }, dbg(){ return { panel: !!uiPanelImg._raw, plaque: !!uiPlaqueImg._raw, bg: !!bgImg._raw, panelW: uiPanelImg.width }; }
};`;

const raws = JSON.parse(fs.readFileSync('/home/user/assets/frames.raw.json', 'utf8'));
const rawsF = JSON.parse(fs.readFileSync('/home/user/assets/frames-fish.raw.json', 'utf8'));
const rawsW = JSON.parse(fs.readFileSync('/home/user/assets/frames-wait.raw.json', 'utf8'));
const rawsBG = [JSON.parse(fs.readFileSync('/home/user/assets/bg.raw.json', 'utf8'))];
const rawsI = JSON.parse(fs.readFileSync('/home/user/assets/fish-icons.raw.json', 'utf8'));
const rawsBN = [JSON.parse(fs.readFileSync('/home/user/assets/bg-night.raw.json', 'utf8'))];
const rawsWk = JSON.parse(fs.readFileSync('/home/user/assets/frames-walk.raw.json', 'utf8'));
const rawsUI = JSON.parse(fs.readFileSync('/home/user/assets/ui.raw.json', 'utf8'));
const rawsFA = JSON.parse(fs.readFileSync('/home/user/assets/fa.raw.json', 'utf8'));
const rawsSH = JSON.parse(fs.readFileSync('/home/user/assets/shore.raw.json', 'utf8'));
const rawsFO = JSON.parse(fs.readFileSync('/home/user/assets/frames-fish-orig.raw.json', 'utf8'));
const rawsWO = JSON.parse(fs.readFileSync('/home/user/assets/frames-wait-orig.raw.json', 'utf8'));
const ALL_RAW = raws.concat(rawsF).concat(rawsW).concat(rawsI).concat(rawsBG).concat(rawsBN).concat(rawsWk.L).concat(rawsWk.R).concat(rawsFO).concat(rawsWO).concat([rawsUI.panel, rawsUI.plaque]).concat(rawsFA).concat(rawsSH);
ALL_RAW.forEach(r => { r.data = Buffer.from(r.data, 'base64'); });
const ALL_FRAMES = JSON.parse(html.match(/const FRAMES = (\[[^\]]*\]);/s)[1])
  .concat(JSON.parse(html.match(/const FISH_FRAMES = (\[[^\]]*\]);/s)[1]))
  .concat(JSON.parse(html.match(/const WAIT_FRAMES = (\[[^\]]*\]);/s)[1]))
  .concat(JSON.parse(html.match(/const FISH_ICONS = (\[[^\]]*\]);/s)[1]))
  .concat([html.match(/const BG_SRC = "([^"]*)";/)[1]])
  .concat([html.match(/const BG_NIGHT_SRC = "([^"]*)";/)[1]])
  .concat(JSON.parse(html.match(/const WALK = (\{.*?\});/s)[1]).framesL)
  .concat(JSON.parse(html.match(/const WALK = (\{.*?\});/s)[1]).framesR)
  .concat(JSON.parse(html.match(/const FISHR = (\{.*?\});/s)[1]).framesR)
  .concat(JSON.parse(html.match(/const WAITR = (\{.*?\});/s)[1]).framesR)
  .concat([html.match(/const UI_PANEL_SRC = "([^"]*)";/)[1]])
  .concat([html.match(/const UI_PLAQUE_SRC = "([^"]*)";/)[1]])
  .concat(Object.values(JSON.parse(html.match(/const FA_SRC = (\{.*?\});/s)[1])))
  .concat([html.match(/const SHORE_SRC = "([^"]*)";/)[1], html.match(/const SHORE_N_SRC = "([^"]*)";/)[1]]);

class Img {
  set src(v){ const i = ALL_FRAMES.indexOf(v); if (i >= 0) this._raw = ALL_RAW[i]; }
  get src(){ return ''; }
  get complete(){ return !!this._raw; }
  get width(){ return this._raw ? this._raw.w : 0; }
  get height(){ return this._raw ? this._raw.h : 0; }
}

const mc = new MiniCanvas(320, 180);
const elems = {};
class Elem {
  constructor(id){ this.id = id; this.style = { setProperty(k, v){ this[k] = v; } }; this.children = []; this.textContent = ''; }
  get classList(){
    if (!this._cl) this._cl = { _s:new Set(),
      toggle:(c,on)=>{ if(on===undefined) on=!this._cl._s.has(c); on?this._cl._s.add(c):this._cl._s.delete(c); },
      add:c=>this._cl._s.add(c), remove:c=>this._cl._s.delete(c), contains:c=>this._cl._s.has(c) };
    return this._cl;
  }
  set innerHTML(v){} get innerHTML(){ return ''; }
  querySelector(){ return new Elem('q'); }
  getContext(){ if (!this._ctx) this._ctx = new MC2(this.width || 320, this.height || 180); return this._ctx; }
  addEventListener(ev, fn){ (this._h ||= {})[ev] = fn; }
  prepend(c){ this.children.unshift(c); }
  appendChild(c){ this.children.push(c); }
  get lastChild(){ const c = this.children[this.children.length-1]; if (c) c.remove = () => this.children.pop(); return c; }
  remove(){}
}
function byId(id){
  if (!elems[id]){
    elems[id] = new Elem(id);
    if (id === 'game') elems[id].getContext = () => mc;
  }
  return elems[id];
}
const { MiniCanvas: MC2 } = require('/home/user/assets/minicanvas.js');

let rafCb = null, simTime = 0;
const sandbox = {
  console, Math, JSON, setTimeout: () => 0, setInterval: () => 0,
  performance: { now: () => simTime },
  requestAnimationFrame: cb => { rafCb = cb; },
  Image: Img,
  document: { getElementById: byId, createElement: TAG => new Elem(TAG), querySelectorAll: () => [],
    body: { classList: { _s: new Set(['titleMode']),
      contains(c){ return this._s.has(c); }, add(c){ this._s.add(c); }, remove(c){ this._s.delete(c); },
      toggle(c, on){ if (on === undefined) on = !this._s.has(c); on ? this._s.add(c) : this._s.delete(c); return on; } } } },
  Float32Array,
};
class FakeAC {
  constructor(){ this.currentTime = 0; this.sampleRate = 8000; this.state = 'running'; this.destination = {}; }
  resume(){}
  createGain(){ return { gain: { value: 0, setValueAtTime(){}, exponentialRampToValueAtTime(){} }, connect(){} }; }
  createOscillator(){ return { type: '', frequency: { setValueAtTime(){}, exponentialRampToValueAtTime(){} }, connect(){}, start(){}, stop(){} }; }
  createBuffer(ch, n){ return { getChannelData: () => new Float32Array(n) }; }
  createBufferSource(){ return { buffer: null, connect(){}, start(){} }; }
  createBiquadFilter(){ return { type: '', frequency: { value: 0 }, connect(){} }; }
  createDelay(){ return { delayTime: { value: 0 }, connect(){} }; }
}
sandbox.window = sandbox;
sandbox.window.AudioContext = FakeAC;
sandbox.window.addEventListener = () => {};
sandbox.window.matchMedia = () => ({ matches:false });
vm.createContext(sandbox);
vm.runInContext(js, sandbox);
const T = sandbox.__test;

function step(ms){
  const end = simTime + ms;
  while (simTime < end){ simTime += 16; const cb = rafCb; rafCb = null; cb(simTime); }
}
function shot(name){
  fs.writeFileSync('/home/user/assets/shots/' + name + '.ppm', Buffer.from(mc.ppm()));
  console.log('shot', name, 'state=' + T.state);
}
fs.mkdirSync('/home/user/assets/shots', { recursive: true });
console.log('DBG', JSON.stringify(T.dbg()));

step(1500);            shot('1_idle_day');
T.action(); step(280);   shot('2_cast_windup');
step(520);
T.setBite(1.2); step(700); shot('3_wait_side');
T.setBite(0.05); step(120); shot('4_bite');
T.action(); step(450);   shot('5_reel_side');
step(1000);              shot('6_panel');
T.action(); T.setT(0.75); step(400); shot('7_night');
T.setT(0.52); step(300); shot('8_dusk');
T.setT(0.14); T.setMove(-1); step(500); shot('9_walk');
T.setMove(1); step(600); T.setMove(0); step(100);   /* turn around: face right */
T.action(); step(900); shot('10_wait_right');   /* cast while facing right */
T.action(); T.setT(0.06); T.setMove(0); step(500); shot('11_sunrise');  /* sun low behind ridge */
T.action(); step(300);
console.log('done');
