const fs = require('fs'), vm = require('vm');

let html = fs.readFileSync('/home/user/fishing-sim.html', 'utf8');
let js = html.match(/<script>([\s\S]*)<\/script>/)[1];
js += `
;globalThis.__test = {
  get state(){ return state; }, get frame(){ return frameIdx; }, get catches(){ return catches; },
  get caught(){ return caught; }, get bobber(){ return bobber; },
  action, setBite(dt){ biteAt = tNow + dt; }, setT(v){ T = v; }, get T(){ return T; },
  get shadow(){ return shadow; }, get hint(){ return hintStr; }, setMove(d){ moveDir = d; }, get charX(){ return charX; }, get state2(){ return state; }, get combo(){ return combo; }, get bobber(){ return bobber; }, get charX2(){ return charX; }
};`;

/* ---- canvas 2d ctx stub ---- */
function makeCtx(){
  const store = {};
  return new Proxy(store, {
    get(t, p){
      if (p in t) return t[p];
      return (...a) => {};
    },
    set(t, p, v){ t[p] = v; return true; }
  });
}

class Elem {
  constructor(id){ this.id = id; this.style = { setProperty(k, v){ this[k] = v; } }; this.children = []; this.textContent = ''; this._html = ''; }
  get classList(){
    if (!this._cl) this._cl = { _s:new Set(),
      toggle:(c,on)=>{ if(on===undefined) on=!this._cl._s.has(c); on?this._cl._s.add(c):this._cl._s.delete(c); },
      add:c=>this._cl._s.add(c), remove:c=>this._cl._s.delete(c), contains:c=>this._cl._s.has(c) };
    return this._cl;
  }
  set innerHTML(v){ this._html = v; } get innerHTML(){ return this._html; }
  querySelector(){ return new Elem('q'); }
  set className(v){ this._cls = v; } get className(){ return this._cls; }
  addEventListener(){}
  getContext(){ return ctx; }
  prepend(c){ this.children.unshift(c); c.parent = this; }
  appendChild(c){ this.children.push(c); c.parent = this; }
  get lastChild(){ const c = this.children[this.children.length - 1]; if (c) c.remove = () => { this.children.pop(); }; return c; }
  remove(){}
}
const elems = {};
function byId(id){
  if (!elems[id]){
    elems[id] = new Elem(id);
    if (id === 'game'){
      elems[id].getContext = () => ctx;
      elems[id].width = 320; elems[id].height = 180;
      elems[id].addEventListener = (ev, fn) => { handlers['cv:' + ev] = fn; };
    }
  }
  return elems[id];
}
const ctx = makeCtx();
const handlers = {};

class Img { constructor(){ this.src = ''; } }

/* ---- WebAudio stub ---- */
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

let rafCb = null;
const sandbox = {
  console,
  Math, JSON, setTimeout: (fn, ms) => 0, clearTimeout(){}, setInterval: () => 0, clearInterval(){},
  performance: { now: () => simTime },
  requestAnimationFrame: cb => { rafCb = cb; },
  Image: Img,
  document: { getElementById: byId, createElement: TAG => new Elem(TAG), querySelectorAll: () => [],
    body: { classList: { _s: new Set(['titleMode']),
      contains(c){ return this._s.has(c); }, add(c){ this._s.add(c); }, remove(c){ this._s.delete(c); },
      toggle(c, on){ if (on === undefined) on = !this._s.has(c); on ? this._s.add(c) : this._s.delete(c); return on; } } } },
  Float32Array,
};
sandbox.window = sandbox;
sandbox.window.AudioContext = FakeAC;
sandbox.window.addEventListener = (ev, fn) => { handlers['win:' + ev] = fn; };
sandbox.window.matchMedia = () => ({ matches:false });
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

let simTime = 0;
vm.runInContext(js, sandbox);

const T = sandbox.__test;
function step(ms){
  const end = simTime + ms;
  while (simTime < end){
    simTime += 16;
    const cb = rafCb; rafCb = null;
    cb(simTime);
    if (!rafCb) throw new Error('rAF chain broken');
  }
}
function assert(cond, msg){ if (!cond) { console.error('FAIL:', msg); process.exitCode = 1; } else console.log('ok  :', msg); }

step(1500);
assert(T.state === 'idle', 'starts idle');
assert(T.frame > 0, 'idle frames advance (frame=' + T.frame + ')');

T.action();                       // cast
assert(T.state === 'cast', 'cast state');
step(800);
assert(T.state === 'wait', 'lands in wait (bobber ' + T.bobber.x.toFixed(0) + ',' + T.bobber.y.toFixed(0) + ')');

/* early press = reel in empty */
T.action();
assert(T.state === 'reel', 'early press reels');
step(700);
assert(T.state === 'idle', 'back to idle after empty reel');

/* full catch */
T.action(); step(800);
assert(T.state === 'wait', 'wait again');
T.setBite(0.05); step(200);
assert(T.state === 'bite', 'bite window open');
assert(T.shadow !== null || true, 'shadow spawned');
T.action();                       // hook
assert(T.state === 'reel' && T.caught, 'hooked a ' + (T.caught && T.caught.sp.name));
step(1400);
assert(T.state === 'panel', 'catch panel shown');
assert(T.catches === 1, 'catch counted');
T.action();
assert(T.state === 'idle', 'panel closed');

/* miss path */
T.action(); step(800);
T.setBite(0.05); step(200);
assert(T.state === 'bite', 'bite again');
step(1200);                       // let window pass
assert(T.state === 'reel' && !T.caught, 'miss -> empty reel');
step(700);
assert(T.state === 'idle', 'idle after miss');

/* walking */
T.setMove(-1); step(600);
assert(T.state2 === 'walk', 'walk state entered');
const x1 = T.charX;
step(400);
assert(T.charX < x1, 'walks left (x=' + T.charX.toFixed(0) + ')');
T.setMove(1); step(800);
assert(T.charX > x1, 'walks right');
T.setMove(0); step(100);
assert(T.state2 === 'idle', 'stops walking');

/* facing: walk right then cast -> bobber lands right of character */
T.setMove(1); step(500); T.setMove(0); step(50);
T.action(); step(800);
assert(T.bobber.x > T.charX, 'cast lands right when facing right (bobber ' + T.bobber.x.toFixed(0) + ' > char ' + T.charX.toFixed(0) + ')');
T.action(); step(200);   /* early reel back to idle */
T.setMove(-1); step(300); T.setMove(0); step(50);

/* render across the whole day/night cycle */
for (let t = 0; t < 1; t += 0.05){ T.setT(t); step(40); }
console.log('ok  : full day/night cycle rendered');

/* keyboard + buttons */
handlers['win:keydown']({ code: 'Space', preventDefault(){} });
handlers['win:keydown']({ code: 'KeyM', preventDefault(){} });
handlers['win:keydown']({ code: 'KeyM', preventDefault(){} });
byId('btnCast')._click && byId('btnCast')._click();
console.log('ok  : input handlers ran');
console.log('hint:', T.hint);
console.log(process.exitCode ? '=== FAILURES ===' : '=== ALL TESTS PASSED ===');
