/* Software rasterizer for the Canvas2D subset used by fishing-sim.html */
function parseColor(c){
  if (typeof c !== 'string') return [0,0,0,1];
  c = c.trim();
  if (c[0] === '#'){
    return [parseInt(c.slice(1,3),16), parseInt(c.slice(3,5),16), parseInt(c.slice(5,7),16), 1];
  }
  let m = c.match(/rgba?\(([^)]+)\)/);
  if (m){
    const p = m[1].split(',').map(Number);
    return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
  }
  return [255, 0, 255, 1];
}

class MiniCanvas {
  constructor(w, h, images){
    this.w = w; this.h = h;
    this.buf = new Uint8ClampedArray(w * h * 4);
    this.images = images;
    this.fillStyle = '#000'; this.strokeStyle = '#000';
    this.globalAlpha = 1; this.globalCompositeOperation = 'source-over';
    this.lineWidth = 1; this.imageSmoothingEnabled = false;
    this.path = [];
  }
  _blend(x, y, r, g, b, a){
    if (x < 0 || y < 0 || x >= this.w || y >= this.h || a <= 0) return;
    x |= 0; y |= 0;
    const i = (y * this.w + x) * 4;
    const dA = this.buf[i + 3] / 255;
    const op = this.globalCompositeOperation;
    if (op === 'source-atop'){
      if (dA <= 0) return;                 /* tint only existing pixels */
    }
    const A = Math.min(1, a * this.globalAlpha);
    if (op === 'multiply'){
      const dr = this.buf[i], dg = this.buf[i+1], db = this.buf[i+2];
      r = r * dr / 255; g = g * dg / 255; b = b * db / 255;
    }
    this.buf[i]   = r * A + this.buf[i]   * (1 - A);
    this.buf[i+1] = g * A + this.buf[i+1] * (1 - A);
    this.buf[i+2] = b * A + this.buf[i+2] * (1 - A);
    this.buf[i+3] = Math.max(dA, A) * 255;
  }
  fillRect(x, y, w, h){
    const c = parseColor(this.fillStyle);
    x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h);
    for (let yy = y; yy < y + h; yy++)
      for (let xx = x; xx < x + w; xx++)
        this._blend(xx, yy, c[0], c[1], c[2], c[3]);
  }
  strokeRect(x, y, w, h){
    const c = parseColor(this.strokeStyle);
    x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h);
    for (let xx = x; xx < x + w; xx++){ this._blend(xx, y, c[0], c[1], c[2], c[3]); this._blend(xx, y + h - 1, c[0], c[1], c[2], c[3]); }
    for (let yy = y; yy < y + h; yy++){ this._blend(x, yy, c[0], c[1], c[2], c[3]); this._blend(x + w - 1, yy, c[0], c[1], c[2], c[3]); }
  }
  beginPath(){ this.path = []; this._cur = null; }
  moveTo(x, y){ this._cur = [[x, y]]; this.path.push(this._cur); }
  lineTo(x, y){ if (!this._cur) this.moveTo(x, y); else this._cur.push([x, y]); }
  closePath(){ if (this._cur && this._cur.length) this._cur.push(this._cur[0].slice()); }
  quadraticCurveTo(cx, cy, x, y){
    const p0 = this._cur[this._cur.length - 1];
    for (let i = 1; i <= 16; i++){
      const t = i / 16, u = 1 - t;
      this._cur.push([u*u*p0[0] + 2*u*t*cx + t*t*x, u*u*p0[1] + 2*u*t*cy + t*t*y]);
    }
  }
  ellipse(cx, cy, rx, ry, rot, a0, a1){
    const pts = [];
    for (let i = 0; i <= 40; i++){
      const a = a0 + (a1 - a0) * i / 40;
      pts.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]);
    }
    this._cur = pts; this.path.push(pts);
    this._ellipseFill = { cx, cy, rx, ry };
  }
  fill(){
    const c = parseColor(this.fillStyle);
    if (this._ellipseFill && this.path.length === 1){
      const e = this._ellipseFill;
      for (let yy = Math.floor(e.cy - e.ry); yy <= e.cy + e.ry; yy++)
        for (let xx = Math.floor(e.cx - e.rx); xx <= e.cx + e.rx; xx++){
          const dx = (xx + 0.5 - e.cx) / e.rx, dy = (yy + 0.5 - e.cy) / e.ry;
          if (dx*dx + dy*dy <= 1) this._blend(xx, yy, c[0], c[1], c[2], c[3]);
        }
      this._ellipseFill = null;
      return;
    }
    /* even-odd scanline polygon fill */
    for (const poly of this.path){
      let miny = 1e9, maxy = -1e9;
      poly.forEach(p => { miny = Math.min(miny, p[1]); maxy = Math.max(maxy, p[1]); });
      for (let yy = Math.floor(miny); yy <= Math.ceil(maxy); yy++){
        const xs = [];
        for (let i = 0; i < poly.length - 1; i++){
          const [x1, y1] = poly[i], [x2, y2] = poly[i + 1];
          if ((y1 <= yy + 0.5 && y2 > yy + 0.5) || (y2 <= yy + 0.5 && y1 > yy + 0.5))
            xs.push(x1 + (yy + 0.5 - y1) / (y2 - y1) * (x2 - x1));
        }
        xs.sort((a, b) => a - b);
        for (let i = 0; i + 1 < xs.length; i += 2)
          for (let xx = Math.floor(xs[i]); xx <= Math.floor(xs[i + 1]); xx++)
            this._blend(xx, yy, c[0], c[1], c[2], c[3]);
      }
    }
  }
  stroke(){
    const c = parseColor(this.strokeStyle);
    for (const poly of this.path)
      for (let i = 0; i < poly.length - 1; i++){
        const [x1, y1] = poly[i], [x2, y2] = poly[i + 1];
        const n = Math.max(1, Math.ceil(Math.max(Math.abs(x2 - x1), Math.abs(y2 - y1)) * 2));
        for (let k = 0; k <= n; k++)
          this._blend(Math.round(x1 + (x2 - x1) * k / n), Math.round(y1 + (y2 - y1) * k / n), c[0], c[1], c[2], c[3]);
      }
  }
  clearRect(x, y, w, h){
    for (let yy = y; yy < y + h; yy++)
      for (let xx = x; xx < x + w; xx++){
        if (xx < 0 || yy < 0 || xx >= this.w || yy >= this.h) continue;
        const i = (yy * this.w + xx) * 4;
        this.buf[i] = this.buf[i+1] = this.buf[i+2] = this.buf[i+3] = 0;
      }
  }
  drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh){
    let src = null;
    if (img && img.buf) src = img;                            /* MiniCanvas source */
    else if (img && img._ctx && img._ctx.buf) src = img._ctx; /* canvas-element stub */
    else if (img && img._raw) src = { buf: img._raw.data, w: img._raw.w, h: img._raw.h };
    if (!src) return;
    if (sw !== undefined && dx !== undefined){                /* 9-arg: (srect, drect) */
      for (let yy = 0; yy < dh; yy++)
        for (let xx = 0; xx < dw; xx++){
          const sxx = Math.floor(sx + xx * sw / dw), syy = Math.floor(sy + yy * sh / dh);
          const i = (syy * src.w + sxx) * 4;
          const a = src.buf[i + 3] / 255;
          if (a > 0) this._blend(dx + xx, dy + yy, src.buf[i], src.buf[i+1], src.buf[i+2], a);
        }
      return;
    }
    /* 3-arg: (img, x, y) */
    const ox = sx | 0, oy = sy | 0;
    for (let yy = 0; yy < src.h; yy++)
      for (let xx = 0; xx < src.w; xx++){
        const i = (yy * src.w + xx) * 4;
        const a = src.buf[i + 3] / 255;
        if (a > 0) this._blend(ox + xx, oy + yy, src.buf[i], src.buf[i+1], src.buf[i+2], a);
      }
  }
  ppm(){
    const head = Buffer.from(`P6\n${this.w} ${this.h}\n255\n`);
    const rgb = Buffer.alloc(this.w * this.h * 3);
    for (let i = 0, j = 0; i < this.buf.length; i += 4, j += 3){
      rgb[j] = this.buf[i]; rgb[j+1] = this.buf[i+1]; rgb[j+2] = this.buf[i+2];
    }
    return Buffer.concat([head, rgb]);
  }
}
module.exports = { MiniCanvas, parseColor };
