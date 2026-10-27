// Shared webcam + MediaPipe hand tracking for all games.
// Runs entirely in the visitor's browser: the camera image never leaves the device.
import {
  FilesetResolver,
  HandLandmarker,
  DrawingUtils,
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs";

const WASM_URL = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";

export class HandTracker {
  constructor({ numHands = 1, onResults = null } = {}) {
    this.numHands = numHands;
    this.onResults = onResults;
    // hands: list of 21 landmarks each, x already mirrored (like cv2.flip(img, 1))
    this.hands = [];
    // "Left"/"Right" for each hand, from the player's point of view
    this.handedness = [];
    this.ready = false;
    this.error = null;
    this.lastVideoTime = -1;
    this.preview = null;
  }

  async start() {
    this.video = document.createElement("video");
    this.video.playsInline = true;
    this.video.muted = true;
    this.buildPreview();
    this.setStatus("Kamera açılıyor…");

    const [stream, landmarker] = await Promise.all([
      navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
        audio: false,
      }),
      this.createLandmarker(),
    ]);
    this.landmarker = landmarker;
    this.video.srcObject = stream;
    await this.video.play();
    this.ready = true;
    this.setStatus("");
    this.loop();
  }

  async createLandmarker() {
    const vision = await FilesetResolver.forVisionTasks(WASM_URL);
    const options = (delegate) => ({
      baseOptions: { modelAssetPath: MODEL_URL, delegate },
      runningMode: "VIDEO",
      numHands: this.numHands,
      minHandDetectionConfidence: 0.5,
      minHandPresenceConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });
    try {
      return await HandLandmarker.createFromOptions(vision, options("GPU"));
    } catch {
      return await HandLandmarker.createFromOptions(vision, options("CPU"));
    }
  }

  loop() {
    if (this.video.currentTime !== this.lastVideoTime && this.video.readyState >= 2) {
      this.lastVideoTime = this.video.currentTime;
      const result = this.landmarker.detectForVideo(this.video, performance.now());
      this.hands = result.landmarks.map((hand) =>
        hand.map((lm) => ({ x: 1 - lm.x, y: lm.y, z: lm.z }))
      );
      // MediaPipe labels hands as if the image were already mirrored; ours is not, so swap
      this.handedness = result.handedness.map((h) => (h[0]?.categoryName === "Left" ? "Right" : "Left"));
      this.drawPreview(result.landmarks);
      if (this.onResults) this.onResults(this.hands);
    }
    requestAnimationFrame(() => this.loop());
  }

  // Small mirrored webcam window with the landmarks, like the original "WebCam" cv2 window
  buildPreview() {
    const box = document.createElement("div");
    box.className = "cam-preview";
    const canvas = document.createElement("canvas");
    canvas.width = 480;
    canvas.height = 360;
    const status = document.createElement("div");
    status.className = "cam-status";
    box.append(canvas, status);
    box.title = "Büyütmek / küçültmek için tıkla";
    box.addEventListener("click", () => box.classList.toggle("big"));
    document.body.append(box);
    this.preview = { box, canvas, ctx: canvas.getContext("2d"), status };
    this.drawer = new DrawingUtils(this.preview.ctx);
  }

  drawPreview(rawLandmarks) {
    const { canvas, ctx } = this.preview;
    ctx.save();
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(this.video, 0, 0, canvas.width, canvas.height);
    for (const hand of rawLandmarks) {
      this.drawer.drawConnectors(hand, HandLandmarker.HAND_CONNECTIONS, { color: "#ffffff", lineWidth: 2 });
      this.drawer.drawLandmarks(hand, { color: "#ff3131", lineWidth: 1, radius: 2 });
    }
    ctx.restore();

    // bounding box + Left/Right label per hand, like the cvzone webcam window
    rawLandmarks.forEach((hand, i) => {
      const xs = hand.map((lm) => (1 - lm.x) * canvas.width);
      const ys = hand.map((lm) => lm.y * canvas.height);
      const x = Math.min(...xs) - 12, y = Math.min(...ys) - 12;
      const w = Math.max(...xs) - x + 12, h = Math.max(...ys) - y + 12;
      ctx.strokeStyle = "#ff00ff";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, w, h);
      ctx.fillStyle = "#ff00ff";
      ctx.font = "600 18px Fredoka, Arial, sans-serif";
      ctx.textBaseline = "bottom";
      ctx.fillText(this.handedness[i] || "", x, y - 2);
    });
  }

  setStatus(text) {
    if (!this.preview) return;
    this.preview.status.textContent = text;
    this.preview.status.style.display = text ? "flex" : "none";
  }

  fail(err) {
    this.error = err;
    const denied = err && (err.name === "NotAllowedError" || err.name === "SecurityError");
    this.setStatus(
      denied
        ? "Kamera izni verilmedi. Fare/klavye ile oynayabilirsin."
        : "Kamera bulunamadı. Fare/klavye ile oynayabilirsin."
    );
  }
}

// Fit a fixed-size game canvas into the window, keeping its aspect ratio
export function fitCanvas(canvas) {
  const resize = () => {
    const scale = Math.min(window.innerWidth / canvas.width, window.innerHeight / canvas.height);
    canvas.style.width = `${canvas.width * scale}px`;
    canvas.style.height = `${canvas.height * scale}px`;
  };
  window.addEventListener("resize", resize);
  resize();
}

// Mouse/touch position in game coordinates
export function trackPointer(canvas) {
  const pointer = { x: canvas.width / 2, y: canvas.height / 2, down: false, clicked: false, active: false };
  const update = (e) => {
    const r = canvas.getBoundingClientRect();
    pointer.x = ((e.clientX - r.left) / r.width) * canvas.width;
    pointer.y = ((e.clientY - r.top) / r.height) * canvas.height;
    pointer.active = true;
  };
  canvas.addEventListener("pointermove", update);
  canvas.addEventListener("pointerdown", (e) => {
    update(e);
    pointer.down = true;
    pointer.clicked = true;
  });
  window.addEventListener("pointerup", () => (pointer.down = false));
  return pointer;
}

export function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

export function loadSound(src, volume = 1) {
  const audio = new Audio(src);
  audio.volume = volume;
  audio.preload = "auto";
  return {
    play() {
      const s = audio.cloneNode();
      s.volume = volume;
      s.play().catch(() => {});
    },
  };
}

export function loadMusic(src, volume) {
  const audio = new Audio(src);
  audio.loop = true;
  audio.volume = volume;
  return {
    play() {
      audio.currentTime = 0;
      audio.play().catch(() => {});
    },
    stop() {
      audio.pause();
    },
  };
}

// 3-2-1 countdown drawn over the game, so players can get their hands in front of the camera
export function drawCountdown(ctx, w, h, msLeft) {
  const n = Math.ceil(msLeft / 1000);
  const t = 1 - (msLeft % 1000) / 1000;
  ctx.save();
  ctx.fillStyle = "rgba(0,0,0,0.35)";
  ctx.fillRect(0, 0, w, h);
  ctx.globalAlpha = 1 - t * 0.6;
  ctx.font = `700 ${180 + t * 80}px Fredoka, Arial, sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.lineWidth = 10;
  ctx.strokeStyle = "rgba(0,0,0,0.5)";
  ctx.strokeText(String(n), w / 2, h / 2);
  ctx.fillStyle = "#fff";
  ctx.fillText(String(n), w / 2, h / 2);
  ctx.restore();
}

// best score per game, kept in this browser
export function bestScore(game, score) {
  const key = `tricoders-best-${game}`;
  let best = 0;
  try { best = Number(localStorage.getItem(key)) || 0; } catch {}
  if (score !== undefined && score > best) {
    best = score;
    try { localStorage.setItem(key, String(best)); } catch {}
  }
  return best;
}

// the same hand icons as the HINT section of the site
export function loadHintIcons(base = "../assets/hints/") {
  return Promise.all(["open", "fist", "thumb", "pinky"].map((n) => loadImage(`${base}${n}.svg`)))
    .then(([open, fist, thumb, pinky]) => ({ open, fist, thumb, pinky }));
}

// open hand -> curly arrow -> fist, with a label under the arrow ("CATCHING", "PICK UP")
export function drawCatchHint(ctx, icons, cx, cy, label, { scale = 1, color = "#f88615", card = "rgba(255,255,255,0.85)" } = {}) {
  const iw = 64 * scale, ih = 74 * scale;
  ctx.save();
  ctx.fillStyle = card;
  ctx.beginPath();
  ctx.roundRect(cx - 170 * scale, cy - 52 * scale, 340 * scale, 104 * scale, 18 * scale);
  ctx.fill();
  ctx.drawImage(icons.open, cx - 150 * scale, cy - ih / 2, iw, ih);
  ctx.drawImage(icons.fist, cx + 86 * scale, cy - ih / 2, iw, ih);
  ctx.strokeStyle = "#222";
  ctx.lineWidth = 4 * scale;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  const ox = cx - 50 * scale, oy = cy - 30 * scale, k = 0.83 * scale;
  ctx.moveTo(ox + 6 * k, oy + 52 * k);
  ctx.bezierCurveTo(ox + 20 * k, oy + 20 * k, ox + 48 * k, oy + 12 * k, ox + 58 * k, oy + 30 * k);
  ctx.bezierCurveTo(ox + 66 * k, oy + 46 * k, ox + 46 * k, oy + 50 * k, ox + 50 * k, oy + 34 * k);
  ctx.bezierCurveTo(ox + 56 * k, oy + 14 * k, ox + 86 * k, oy + 8 * k, ox + 108 * k, oy + 16 * k);
  ctx.moveTo(ox + 96 * k, oy + 6 * k);
  ctx.lineTo(ox + 110 * k, oy + 16 * k);
  ctx.lineTo(ox + 98 * k, oy + 28 * k);
  ctx.stroke();
  ctx.font = `700 ${18 * scale}px Fredoka, Arial, sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = color;
  ctx.fillText(label, cx, cy + 32 * scale);
  ctx.restore();
}
