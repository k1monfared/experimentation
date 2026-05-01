// Tiny pure-JS helpers used by the playground widgets.
// Mirrors a subset of expkit logic so the widgets stay self-contained.

(function (global) {
  "use strict";

  // Mulberry32: a small deterministic PRNG so widgets are reproducible.
  function mulberry32(seed) {
    let s = seed >>> 0;
    return function () {
      s |= 0; s = (s + 0x6D2B79F5) | 0;
      let t = Math.imul(s ^ (s >>> 15), 1 | s);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // log gamma via Stirling series (good for x > 1)
  function logGamma(x) {
    const c = [
      76.18009172947146, -86.50532032941677, 24.01409824083091,
      -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5,
    ];
    let xx = x;
    let y = x;
    let tmp = x + 5.5;
    tmp -= (x + 0.5) * Math.log(tmp);
    let ser = 1.000000000190015;
    for (let j = 0; j < 6; j++) { y += 1; ser += c[j] / y; }
    return -tmp + Math.log((2.5066282746310005 * ser) / xx);
  }

  function logBeta(a, b) { return logGamma(a) + logGamma(b) - logGamma(a + b); }

  // Regularized incomplete beta function via continued fraction.
  function betaI(x, a, b) {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    const bt = Math.exp(-logBeta(a, b) + a * Math.log(x) + b * Math.log(1 - x));
    if (x < (a + 1) / (a + b + 2)) return (bt * betacf(x, a, b)) / a;
    return 1 - (bt * betacf(1 - x, b, a)) / b;
  }
  function betacf(x, a, b) {
    const MAXIT = 200;
    const EPS = 3e-7;
    let qab = a + b, qap = a + 1, qam = a - 1;
    let c = 1, d = 1 - (qab * x) / qap;
    if (Math.abs(d) < 1e-30) d = 1e-30;
    d = 1 / d;
    let h = d;
    for (let m = 1; m <= MAXIT; m++) {
      const m2 = 2 * m;
      let aa = (m * (b - m) * x) / ((qam + m2) * (a + m2));
      d = 1 + aa * d; if (Math.abs(d) < 1e-30) d = 1e-30;
      c = 1 + aa / c; if (Math.abs(c) < 1e-30) c = 1e-30;
      d = 1 / d; h *= d * c;
      aa = (-(a + m) * (qab + m) * x) / ((a + m2) * (qap + m2));
      d = 1 + aa * d; if (Math.abs(d) < 1e-30) d = 1e-30;
      c = 1 + aa / c; if (Math.abs(c) < 1e-30) c = 1e-30;
      d = 1 / d;
      const del = d * c; h *= del;
      if (Math.abs(del - 1) < EPS) return h;
    }
    return h;
  }

  // Beta(a, b) PDF
  function betaPdf(x, a, b) {
    if (x <= 0 || x >= 1) return 0;
    return Math.exp((a - 1) * Math.log(x) + (b - 1) * Math.log(1 - x) - logBeta(a, b));
  }

  // Beta(a, b) inverse CDF via bisection. Slow but adequate for plotting.
  function betaIcdf(p, a, b) {
    if (p <= 0) return 0;
    if (p >= 1) return 1;
    let lo = 0, hi = 1;
    for (let i = 0; i < 60; i++) {
      const mid = (lo + hi) / 2;
      if (betaI(mid, a, b) < p) lo = mid; else hi = mid;
    }
    return (lo + hi) / 2;
  }

  // Binomial PMF
  function binomPmf(k, n, p) {
    if (k < 0 || k > n) return 0;
    if (p === 0) return k === 0 ? 1 : 0;
    if (p === 1) return k === n ? 1 : 0;
    return Math.exp(
      logGamma(n + 1) - logGamma(k + 1) - logGamma(n - k + 1) +
      k * Math.log(p) + (n - k) * Math.log(1 - p)
    );
  }

  // Two-sided exact binomial p-value (sum of probabilities <= P(observed) under null).
  function binomTestExact(k, n, p0 = 0.5) {
    const obs = binomPmf(k, n, p0);
    let sum = 0;
    const tol = 1e-12;
    for (let i = 0; i <= n; i++) {
      const pi = binomPmf(i, n, p0);
      if (pi <= obs + tol) sum += pi;
    }
    return Math.min(1, sum);
  }

  // Wilson score CI for a single proportion at level (default 0.95).
  function wilsonCi(k, n, level = 0.95) {
    if (n === 0) return [0, 1];
    const z = level === 0.95 ? 1.959963984540054 : Math.sqrt(2) * 1; // approximate
    const p = k / n;
    const denom = 1 + (z * z) / n;
    const center = (p + (z * z) / (2 * n)) / denom;
    const half = (z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n))) / denom;
    return [Math.max(0, center - half), Math.min(1, center + half)];
  }

  // Simple plotting primitives -- assume canvas already sized in CSS pixels.
  // The caller provides a coordinate system (x in [xmin, xmax], y in [ymin, ymax]).
  function makeAxes(ctx, w, h, opts) {
    const padL = opts.padL || 50, padR = opts.padR || 16, padT = opts.padT || 24, padB = opts.padB || 36;
    const xmin = opts.xmin, xmax = opts.xmax, ymin = opts.ymin, ymax = opts.ymax;
    function sx(x) { return padL + ((x - xmin) / (xmax - xmin)) * (w - padL - padR); }
    function sy(y) { return h - padB - ((y - ymin) / (ymax - ymin)) * (h - padT - padB); }
    return { sx, sy, padL, padR, padT, padB };
  }
  function clearCanvas(ctx, w, h) {
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, w, h);
  }
  function drawAxes(ctx, axes, w, h, opts) {
    ctx.strokeStyle = "#bbb"; ctx.lineWidth = 1; ctx.beginPath();
    ctx.moveTo(axes.padL, axes.padT); ctx.lineTo(axes.padL, h - axes.padB);
    ctx.lineTo(w - axes.padR, h - axes.padB); ctx.stroke();
    ctx.fillStyle = "#444"; ctx.font = "12px system-ui, sans-serif"; ctx.textAlign = "center";
    if (opts.xlabel) ctx.fillText(opts.xlabel, (axes.padL + (w - axes.padR)) / 2, h - 8);
    ctx.save(); ctx.translate(14, (axes.padT + (h - axes.padB)) / 2); ctx.rotate(-Math.PI / 2);
    if (opts.ylabel) ctx.fillText(opts.ylabel, 0, 0);
    ctx.restore();
    if (opts.title) { ctx.font = "bold 13px system-ui, sans-serif"; ctx.fillText(opts.title, w / 2, 16); }
  }
  function plotLine(ctx, axes, xs, ys, color, lw = 1.6) {
    ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.beginPath();
    for (let i = 0; i < xs.length; i++) {
      const x = axes.sx(xs[i]), y = axes.sy(ys[i]);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  function plotBand(ctx, axes, xs, lo, hi, color, alpha = 0.18) {
    ctx.fillStyle = hexToRgba(color, alpha);
    ctx.beginPath();
    for (let i = 0; i < xs.length; i++) ctx.lineTo(axes.sx(xs[i]), axes.sy(hi[i]));
    for (let i = xs.length - 1; i >= 0; i--) ctx.lineTo(axes.sx(xs[i]), axes.sy(lo[i]));
    ctx.closePath(); ctx.fill();
  }
  function hexToRgba(hex, a) {
    const h = hex.replace("#", "");
    const n = parseInt(h.length === 3 ? h.split("").map(c => c + c).join("") : h, 16);
    const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  }
  function plotHLine(ctx, axes, w, y, color, dash = [4, 4]) {
    ctx.save(); ctx.strokeStyle = color; ctx.setLineDash(dash); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(axes.padL, axes.sy(y)); ctx.lineTo(w - axes.padR, axes.sy(y)); ctx.stroke();
    ctx.restore();
  }
  function plotVLine(ctx, axes, h, x, color, dash = [4, 4]) {
    ctx.save(); ctx.strokeStyle = color; ctx.setLineDash(dash); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(axes.sx(x), axes.padT); ctx.lineTo(axes.sx(x), h - axes.padB); ctx.stroke();
    ctx.restore();
  }

  // Resize a canvas for crisp rendering on hi-DPI screens.
  function fitCanvas(canvas, cssWidth, cssHeight) {
    const dpr = window.devicePixelRatio || 1;
    canvas.style.width = cssWidth + "px";
    canvas.style.height = cssHeight + "px";
    canvas.width = Math.round(cssWidth * dpr);
    canvas.height = Math.round(cssHeight * dpr);
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return ctx;
  }

  global.expkitWidget = {
    mulberry32, betaI, betaPdf, betaIcdf,
    binomPmf, binomTestExact, wilsonCi,
    makeAxes, clearCanvas, drawAxes, plotLine, plotBand, plotHLine, plotVLine,
    fitCanvas, hexToRgba,
    palette: {
      frequentist: "#1f77b4",
      bayesian: "#d62728",
      muted: "#888888",
      highlight: "#2ca02c",
    },
  };
})(window);
