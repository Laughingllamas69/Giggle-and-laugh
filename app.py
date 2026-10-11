"""
Giggle and Laugh 😂 — Your Daily Dose of Happiness
A fun, lighthearted wellness & entertainment portal for everyone.
"""

import os
import json
import hashlib
import hmac
from datetime import datetime
import pandas as pd
import streamlit as st
import random
import streamlit.components.v1 as components
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# --- Configuration Constants ---

def config_value(name, default):
    environment_value = os.getenv(name)
    if environment_value:
        return environment_value
    try:
        return st.secrets.get(name, default)
    except st.errors.StreamlitSecretNotFoundError:
        return default


MONGO_URI = config_value("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = config_value("MONGO_DB_NAME", "giggle_laugh")
APP_ADMIN_PASSWORD = config_value("APP_ADMIN_PASSWORD", "")
APP_TITLE = "Giggle and Laugh 😂"
APP_SUBTITLE = "Your Personal Hub for Fun, Games, and Good Vibes"

# --- Jokes Database ---
JOKES_LIST = [
    {"category": "Puns", "text": "I used to be addicted to soap, but I'm clean now."},
    {"category": "Tech", "text": "Why do programmers prefer dark mode? Because light attracts bugs."},
    {"category": "Animals", "text": "What do you call a fake noodle? An Impasta."},
    {"category": "Work", "text": "I told my boss three companies were after me and I needed a raise to stay. He asked which companies. I said: Electricity, Water, and Gas."},
    {"category": "Science", "text": "Why can't you trust an atom? They make up everything."},
    {"category": "Food", "text": "Why did the coffee file a police report? It got mugged."},
    {"category": "General", "text": "Parallel lines have so much in common. It's a shame they'll never meet."},
    {"category": "Animals", "text": "What do you call a bear with no teeth? A gummy bear."},
    {"category": "Tech", "text": "There are 10 types of people in the world: those who understand binary, and those who don't."},
    {"category": "General", "text": "I'm reading a book about anti-gravity. It's impossible to put down!"},
    {"category": "Food", "text": "Why did the tomato turn red? Because it saw the salad dressing."},
    {"category": "General", "text": "What do you call a lazy kangaroo? A pouch potato."},
]

# --- Meme Data ---
MEME_TEMPLATES = [
    {"title": "Distracted Boyfriend", "desc": "Me looking at dessert when I said I'm on a diet.", "emoji": "👀🍰"},
    {"title": "Drake Hotline Bling", "desc": "Working Hard: ❌ | Taking a Nap: ✅", "emoji": "🙅‍♂️😴"},
    {"title": "Two Buttons", "desc": "Sleep Early vs. Watch One More Episode", "emoji": "😵💤📺"},
    {"title": "Expanding Brain", "desc": "Coffee → Espresso → Caffeine IV Drip", "emoji": "🧠☕⚡"},
    {"title": "This is Fine", "desc": "Me when the deadline is tomorrow but today is fine.", "emoji": "🔥🐶☕"},
    {"title": "Change My Mind", "desc": "Pineapple belongs on pizza. Change my mind.", "emoji": "🍕🤔"},
]

# --- Games HTML (Clicker Game) ---
GAMES_HTML = """
<div style="text-align:center; font-family: 'Nunito', sans-serif; padding: 20px;">
    <h3>🎮 Super Clicker!</h3>
    <p>How many times can you click it?</p>
    <button onclick="increment()" id="clickBtn" style="font-size: 24px; padding: 20px 40px; background-color: #FF6B35; color: white; border: none; border-radius: 50%; cursor: pointer; box-shadow: 0 6px #c44d28; transition: all 0.1s;">
        CLICK ME
    </button>
    <h2 id="count" style="margin-top: 20px; color: #2D2A32;">0</h2>
    <script>
        let count = 0;
        function increment() {
            count++;
            document.getElementById('count').innerText = count;
            const btn = document.getElementById('clickBtn');
            // Random color change
            const colors = ['#FF6B35', '#4CC9F0', '#F72585', '#4361EE', '#7209B7'];
            const shadows = ['#c44d28', '#3ab0d9', '#c4176b', '#3548c2', '#5a078d'];
            const rand = Math.floor(Math.random() * colors.length);
            btn.style.backgroundColor = colors[rand];
            btn.style.boxShadow = '0 6px ' + shadows[rand];
        }
    </script>
</div>
"""

FLAPPY_HTML = """
<div style="font-family:Arial,sans-serif;color:#282522;text-align:center;background:#fff5e8;padding:14px;border:2px solid #282522;border-radius:14px">
    <div style="font-weight:800;font-size:20px;margin:2px 0 10px">Flap Dash</div>
    <canvas id="flapCanvas" width="720" height="360" aria-label="Flap Dash game" tabindex="0" style="display:block;width:100%;max-width:720px;height:auto;margin:auto;border:2px solid #282522;border-radius:10px;touch-action:manipulation"></canvas>
    <div style="display:flex;justify-content:center;align-items:center;gap:14px;flex-wrap:wrap;margin-top:10px">
        <button id="flapStart" style="font-weight:800;padding:9px 16px;border:2px solid #282522;border-radius:10px;background:#ffd24c;cursor:pointer">Start / Restart</button>
        <span>Space, ↑, or tap to flap</span>
    </div>
</div>
<script>
(() => {
    const canvas = document.getElementById('flapCanvas');
    const ctx = canvas.getContext('2d');
    const bird = { x: 150, y: 170, vy: 0, radius: 13 };
    let pipes = [], frame = 0, score = 0, started = false, over = false;
    function reset() {
        bird.y = 170; bird.vy = 0; pipes = []; frame = 0; score = 0;
        started = true; over = false;
    }
    function flap() {
        if (!started || over) reset();
        bird.vy = -7.2;
    }
    document.getElementById('flapStart').addEventListener('click', reset);
    canvas.addEventListener('pointerdown', flap);
    window.addEventListener('keydown', event => {
        if (event.code === 'Space' || event.code === 'ArrowUp') {
            event.preventDefault(); flap();
        }
    });
    function draw() {
        ctx.fillStyle = '#bdeee8'; ctx.fillRect(0, 0, 720, 360);
        ctx.fillStyle = '#fff4c7';
        ctx.beginPath(); ctx.arc(610, 58, 28, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#fff';
        for (const cloud of [[90, 65], [360, 105], [560, 150]]) {
            ctx.beginPath(); ctx.ellipse(cloud[0], cloud[1], 34, 11, 0, 0, Math.PI * 2); ctx.fill();
        }
        for (const pipe of pipes) {
            ctx.fillStyle = '#238b57';
            ctx.fillRect(pipe.x, 0, 48, pipe.top);
            ctx.fillRect(pipe.x - 5, pipe.top - 15, 58, 15);
            ctx.fillRect(pipe.x, pipe.bottom, 48, 360 - pipe.bottom);
            ctx.fillRect(pipe.x - 5, pipe.bottom, 58, 15);
        }
        ctx.fillStyle = '#f06b45';
        ctx.beginPath(); ctx.arc(bird.x, bird.y, bird.radius, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(bird.x + 5, bird.y - 4, 4, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#282522'; ctx.beginPath(); ctx.arc(bird.x + 6, bird.y - 4, 1.6, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#ffd24c'; ctx.beginPath(); ctx.moveTo(bird.x + 11, bird.y + 2); ctx.lineTo(bird.x + 21, bird.y + 5); ctx.lineTo(bird.x + 11, bird.y + 8); ctx.fill();
        ctx.fillStyle = '#f3c65b'; ctx.fillRect(0, 340, 720, 20);
        ctx.fillStyle = '#282522'; ctx.font = 'bold 22px Arial'; ctx.fillText('Score: ' + score, 18, 30);
        if (!started || over) {
            ctx.fillStyle = 'rgba(255,250,241,.88)'; ctx.fillRect(150, 125, 420, 90);
            ctx.fillStyle = '#282522'; ctx.textAlign = 'center'; ctx.font = 'bold 24px Arial';
            ctx.fillText(over ? 'Oof! Score: ' + score : 'Ready to flap?', 360, 164);
            ctx.font = '16px Arial'; ctx.fillText(over ? 'Tap or press Start to fly again' : 'Tap Start, then flap through the gaps', 360, 193);
            ctx.textAlign = 'left';
        }
    }
    function step() {
        if (started && !over) {
            frame++;
            bird.vy += 0.42; bird.y += bird.vy;
            if (frame % 92 === 0) {
                const top = 48 + Math.random() * 145;
                pipes.push({ x: 740, top, bottom: top + 112, scored: false });
            }
            for (const pipe of pipes) {
                pipe.x -= 2.8;
                if (!pipe.scored && pipe.x + 48 < bird.x) { pipe.scored = true; score++; }
                const overlapsX = bird.x + bird.radius > pipe.x && bird.x - bird.radius < pipe.x + 48;
                if (overlapsX && (bird.y - bird.radius < pipe.top || bird.y + bird.radius > pipe.bottom)) over = true;
            }
            pipes = pipes.filter(pipe => pipe.x > -65);
            if (bird.y < 0 || bird.y + bird.radius > 340) over = true;
        }
        draw(); requestAnimationFrame(step);
    }
    draw(); requestAnimationFrame(step);
})();
</script>
"""

RUNNER_HTML = """
<div id="templeGame" class="temple-game">
    <canvas id="templeCanvas" aria-label="Temple Dash 3D endless runner"></canvas>
    <div class="temple-vignette"></div>
    <header class="temple-hud">
        <div class="temple-brand"><span class="brand-mark">✦</span><span>TEMPLE<br><b>DASH</b></span></div>
        <div class="stat-pill"><small>DISTANCE</small><strong id="distanceValue">0 <i>m</i></strong></div>
        <div class="stat-pill relic-stat"><small>RELICS</small><strong><span>◆</span> <b id="relicValue">0</b></strong></div>
        <button id="pauseButton" class="pause-button" aria-label="Pause game" title="Pause">Ⅱ</button>
    </header>
    <div class="temple-progress"><span id="progressBar"></span></div>
    <div class="temple-toast" id="powerToast">RELIC FOUND</div>
    <section id="startOverlay" class="temple-overlay">
        <div class="overlay-card">
            <span class="eyebrow">THE LOST GARDEN</span>
            <h2 id="overlayTitle">TEMPLE<br><em>DASH</em></h2>
            <p id="overlayCopy">The guardian is awake. Grab relics, dodge the ruins, and find your way out.</p>
            <button id="runStart" class="start-run">ENTER THE TEMPLE <span>↗</span></button>
            <div class="control-hint">← → SWITCH LANES <b>·</b> ↑ JUMP <b>·</b> ↓ SLIDE</div>
        </div>
    </section>
    <div class="temple-controls" aria-label="Touch game controls">
        <button data-move="left" aria-label="Move left">‹</button>
        <button data-move="jump" aria-label="Jump">JUMP</button>
        <button data-move="slide" aria-label="Slide">SLIDE</button>
        <button data-move="right" aria-label="Move right">›</button>
    </div>
    <div class="temple-footer"><span>AN ORIGINAL ENDLESS RUNNER</span><span>BEST <b id="bestValue">0 m</b></span></div>
</div>
<style>
    * { box-sizing: border-box; }
    .temple-game { position: relative; width: 100%; height: min(680px, 100vh); min-height: 500px; overflow: hidden; border: 1px solid rgba(255,232,179,.55); border-radius: 18px; background: #183d35; color: #fff3d6; font-family: Georgia, 'Times New Roman', serif; isolation: isolate; }
    #templeCanvas { position: absolute; inset: 0; display: block; width: 100%; height: 100%; outline: none; }
    .temple-vignette { position:absolute; inset:0; pointer-events:none; background:linear-gradient(180deg,rgba(14,31,27,.48),transparent 29%,transparent 62%,rgba(14,31,27,.46)); }
    .temple-hud { position:absolute; z-index:2; top:16px; left:18px; right:18px; display:flex; align-items:center; gap:10px; }
    .temple-brand { display:flex; align-items:center; gap:8px; margin-right:auto; color:#fff1cd; font-size:12px; line-height:.92; font-weight:bold; letter-spacing:1.6px; text-shadow:0 2px 12px #152722; }
    .temple-brand b { color:#efbd69; }
    .brand-mark { display:grid; place-items:center; width:32px; height:32px; border:1px solid #eabd68; border-radius:50%; color:#f8d887; font-size:18px; }
    .stat-pill { min-width:96px; padding:7px 12px; border:1px solid rgba(255,237,196,.44); border-radius:10px; background:rgba(19,42,36,.68); backdrop-filter:blur(8px); text-align:center; font-family:Arial,sans-serif; }
    .stat-pill small { display:block; color:#e0c99a; font-size:9px; font-weight:700; letter-spacing:1.3px; }
    .stat-pill strong { display:block; margin-top:2px; color:#fff5df; font-size:17px; }
    .stat-pill i { color:#d7c79e; font-size:11px; font-style:normal; }
    .relic-stat strong span { color:#f5c34f; }
    .pause-button { display:grid; place-items:center; width:38px; height:38px; border:1px solid rgba(255,237,196,.55); border-radius:50%; background:rgba(19,42,36,.75); color:#fff3d6; font-size:16px; cursor:pointer; }
    .temple-progress { position:absolute; z-index:2; top:70px; left:18px; right:18px; height:3px; overflow:hidden; background:rgba(255,242,208,.28); }
    .temple-progress span { display:block; width:0; height:100%; background:#f4c457; box-shadow:0 0 12px #ffc857; }
    .temple-overlay { position:absolute; z-index:4; inset:0; display:grid; place-items:center; padding:78px 18px 56px; background:linear-gradient(90deg,rgba(13,33,29,.78),rgba(13,33,29,.16)); transition:opacity .25s ease,visibility .25s ease; }
    .temple-overlay.hidden { opacity:0; visibility:hidden; pointer-events:none; }
    .overlay-card { width:min(430px,100%); margin-right:auto; padding:22px clamp(18px,5vw,42px); }
    .eyebrow { color:#efd08b; font:700 10px Arial,sans-serif; letter-spacing:2.8px; }
    .overlay-card h2 { margin:12px 0; color:#fff0cc; font-size:clamp(42px,8vw,78px); line-height:.78; letter-spacing:0; text-shadow:0 4px 24px rgba(4,18,14,.38); }
    .overlay-card h2 em { color:#e9b55d; font-style:normal; }
    .overlay-card p { max-width:330px; color:#e5ddc8; font:14px/1.55 Arial,sans-serif; }
    .start-run { display:flex; align-items:center; justify-content:space-between; gap:22px; min-width:210px; margin-top:20px; padding:13px 16px; border:0; border-radius:3px; background:#dca94e; color:#25382b; font:800 12px Arial,sans-serif; letter-spacing:1.2px; cursor:pointer; box-shadow:0 4px 0 #8d6732; }
    .start-run span { font-size:18px; }
    .start-run:hover { background:#f0c66e; transform:translateY(-1px); }
    .control-hint { margin-top:18px; color:#d8d2be; font:700 9px Arial,sans-serif; letter-spacing:1px; }
    .control-hint b { padding:0 4px; color:#edc46c; }
    .temple-controls { position:absolute; z-index:3; right:18px; bottom:44px; display:flex; align-items:center; gap:7px; }
    .temple-controls button { min-width:46px; height:42px; border:1px solid rgba(255,237,196,.52); border-radius:8px; background:rgba(20,44,38,.72); color:#fff0cc; font:700 10px Arial,sans-serif; cursor:pointer; touch-action:manipulation; }
    .temple-controls button:first-child,.temple-controls button:last-child { min-width:40px; font:30px Georgia,serif; }
    .temple-controls button:active { background:#dca94e; color:#25382b; }
    .temple-footer { position:absolute; z-index:2; right:18px; bottom:14px; left:18px; display:flex; justify-content:space-between; color:#eee0bd; font:700 8px Arial,sans-serif; letter-spacing:1.4px; text-shadow:0 1px 8px #142722; }
    .temple-footer b { color:#f1c767; }
    .temple-toast { position:absolute; z-index:3; top:92px; left:50%; transform:translate(-50%,-8px); opacity:0; padding:7px 12px; border:1px solid #f2c45b; background:rgba(25,52,43,.9); color:#ffdc86; font:700 10px Arial,sans-serif; letter-spacing:1.4px; transition:.2s ease; }
    .temple-toast.show { opacity:1; transform:translate(-50%,0); }
    @media (max-width:640px) {
        .temple-game { height: min(680px, 100vh); min-height: 500px; border-radius:12px; }
        .temple-hud { top:12px; left:10px; right:10px; gap:6px; }
        .temple-brand { font-size:9px; letter-spacing:1px; }
        .brand-mark { width:28px; height:28px; }
        .stat-pill { min-width:72px; padding:6px 8px; }
        .stat-pill strong { font-size:14px; }
        .pause-button { width:34px; height:34px; }
        .temple-progress { top:62px; left:10px; right:10px; }
        .overlay-card { margin:0; padding:14px 6px; }
        .overlay-card h2 { font-size:clamp(38px, 15vw, 54px); }
        .temple-controls { right:50%; bottom:44px; transform:translateX(50%); gap:5px; }
        .temple-controls button { min-width:44px; height:44px; }
        .temple-controls button:first-child,.temple-controls button:last-child { min-width:38px; }
        .temple-footer { right:10px; bottom:12px; left:10px; font-size:7px; letter-spacing:.8px; }
    }
    @media (max-width:420px) {
        .temple-hud { left:8px; right:8px; gap:4px; }
        .temple-brand { gap:0; }
        .temple-brand > span:not(.brand-mark) { display:none; }
        .brand-mark { width:25px; height:25px; }
        .stat-pill { min-width:48px; padding:4px; }
        .stat-pill small { font-size:7px; letter-spacing:.7px; }
        .stat-pill strong { font-size:12px; }
        .pause-button { width:30px; height:30px; }
        .temple-progress { top:54px; }
    }
</style>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js';

const shell = document.getElementById('templeGame');
const canvas = document.getElementById('templeCanvas');
const startOverlay = document.getElementById('startOverlay');
const overlayTitle = document.getElementById('overlayTitle');
const overlayCopy = document.getElementById('overlayCopy');
const distanceValue = document.getElementById('distanceValue');
const relicValue = document.getElementById('relicValue');
const bestValue = document.getElementById('bestValue');
const progressBar = document.getElementById('progressBar');
const toast = document.getElementById('powerToast');
const lanePositions = [-2.25, 0, 2.25];

const scene = new THREE.Scene();
scene.background = new THREE.Color('#71937a');
scene.fog = new THREE.Fog('#71937a', 24, 76);
const camera = new THREE.PerspectiveCamera(54, 1, 0.1, 120);
camera.position.set(0, 6.1, 10.5);
camera.lookAt(0, 1.25, -7);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

scene.add(new THREE.HemisphereLight('#d8ebc8', '#45382d', 2.2));
const sun = new THREE.DirectionalLight('#ffe1a0', 3.2);
sun.position.set(-7, 12, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -11; sun.shadow.camera.right = 11;
sun.shadow.camera.top = 14; sun.shadow.camera.bottom = -8;
scene.add(sun);

const mats = {
    path: new THREE.MeshStandardMaterial({ color: '#aa875d', roughness: 1 }),
    tile: new THREE.MeshStandardMaterial({ color: '#b99a6d', roughness: .92 }),
    tileAlt: new THREE.MeshStandardMaterial({ color: '#947451', roughness: 1 }),
    gold: new THREE.MeshStandardMaterial({ color: '#e6b94e', metalness: .65, roughness: .28, emissive: '#68440d', emissiveIntensity: .35 }),
    stone: new THREE.MeshStandardMaterial({ color: '#8a775d', roughness: .94 }),
    stoneLight: new THREE.MeshStandardMaterial({ color: '#baa47a', roughness: .9 }),
    leaf: new THREE.MeshStandardMaterial({ color: '#315d43', roughness: .95 }),
    leafLight: new THREE.MeshStandardMaterial({ color: '#6d8c4b', roughness: .95 }),
    torch: new THREE.MeshStandardMaterial({ color: '#ff9a3d', emissive: '#ff641e', emissiveIntensity: 2.1 }),
    coral: new THREE.MeshStandardMaterial({ color: '#d85c43', roughness: .78 }),
    teal: new THREE.MeshStandardMaterial({ color: '#2c766d', roughness: .8 }),
    dark: new THREE.MeshStandardMaterial({ color: '#302b25', roughness: .95 }),
    skin: new THREE.MeshStandardMaterial({ color: '#ba815f', roughness: .83 }),
    cloth: new THREE.MeshStandardMaterial({ color: '#d8bc82', roughness: .9 })
};

function block(parent, geometry, material, x, y, z, cast = true) {
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(x, y, z);
    mesh.castShadow = cast;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
}

const path = block(scene, new THREE.BoxGeometry(7.8, .48, 68), mats.path, 0, -.33, -27, false);
path.receiveShadow = true;
const slabGeometry = new THREE.BoxGeometry(2.48, .1, 3.72);
const tileRuns = [];
for (let row = 0; row < 18; row++) {
    for (let lane = 0; lane < 3; lane++) {
        const material = (row + lane) % 3 === 0 ? mats.tileAlt : mats.tile;
        const slab = block(scene, slabGeometry, material, lanePositions[lane], -.04, -54 + row * 3.8, false);
        slab.userData.baseZ = slab.position.z;
        tileRuns.push(slab);
    }
}
for (const edgeX of [-3.98, 3.98]) {
    const rail = block(scene, new THREE.BoxGeometry(.28, .24, 68), mats.stone, edgeX, .05, -27, false);
    rail.receiveShadow = true;
}

const scenery = [];
function makeTempleSide(x, z, palm = false) {
    const group = new THREE.Group();
    group.position.set(x, 0, z);
    const sign = Math.sign(x);
    if (palm) {
        block(group, new THREE.CylinderGeometry(.16, .24, 3.4, 7), mats.stone, 0, 1.65, 0);
        for (let leafIndex = 0; leafIndex < 6; leafIndex++) {
            const angle = leafIndex * Math.PI / 3;
            const frond = block(group, new THREE.ConeGeometry(.28, 2.6, 5), leafIndex % 2 ? mats.leaf : mats.leafLight, Math.cos(angle) * .8, 3.1, Math.sin(angle) * .8);
            frond.rotation.z = -Math.cos(angle) * .9;
            frond.rotation.x = Math.sin(angle) * .6;
        }
        block(group, new THREE.IcosahedronGeometry(.7, 0), mats.leaf, sign * .9, 1.0, -.1);
    } else {
        block(group, new THREE.BoxGeometry(1.45, .38, 1.45), mats.stoneLight, 0, .18, 0);
        block(group, new THREE.BoxGeometry(.88, 3.0, .88), mats.stone, 0, 1.8, 0);
        block(group, new THREE.BoxGeometry(1.3, .3, 1.3), mats.stoneLight, 0, 3.35, 0);
        block(group, new THREE.BoxGeometry(1.02, .22, 1.02), mats.stone, 0, 3.62, 0);
        block(group, new THREE.BoxGeometry(.34, .8, .34), mats.dark, -sign * .4, 2.0, .12, false);
        const torchCup = block(group, new THREE.CylinderGeometry(.12, .2, .5, 7), mats.dark, -sign * .4, 3.02, .12);
        torchCup.rotation.z = .08;
        const flame = block(group, new THREE.IcosahedronGeometry(.18, 1), mats.torch, -sign * .4, 3.42, .12, false);
        flame.scale.set(.8, 1.55, .8);
        flame.userData.flicker = true;
        block(group, new THREE.IcosahedronGeometry(.8, 0), mats.leaf, sign * 1.15, .6, -.35, false);
        block(group, new THREE.IcosahedronGeometry(.56, 0), mats.leafLight, sign * 1.48, 1.15, .1, false);
    }
    scene.add(group);
    scenery.push(group);
}
for (let index = 0; index < 8; index++) {
    const z = -49 + index * 8.3;
    makeTempleSide(-5.0, z, index % 2 === 1);
    makeTempleSide(5.0, z + 4.15, index % 2 === 0);
}

const player = new THREE.Group();
const torso = new THREE.Group();
player.add(torso);
block(torso, new THREE.CapsuleGeometry(.36, .68, 4, 8), mats.coral, 0, 1.18, 0);
block(torso, new THREE.BoxGeometry(.54, .58, .3), mats.teal, 0, 1.13, .03);
block(torso, new THREE.BoxGeometry(.39, .48, .26), mats.dark, 0, .56, .02);
block(torso, new THREE.BoxGeometry(.48, .54, .3), mats.teal, 0, 1.19, .32);
block(torso, new THREE.BoxGeometry(.29, .28, .06), mats.gold, 0, 1.24, .5);
block(torso, new THREE.BoxGeometry(.07, .46, .08), mats.dark, -.2, 1.18, .49, false);
block(torso, new THREE.BoxGeometry(.07, .46, .08), mats.dark, .2, 1.18, .49, false);
block(torso, new THREE.CylinderGeometry(.1, .1, .5, 10), mats.coral, 0, 1.58, .4).rotation.x = Math.PI / 2;
block(torso, new THREE.SphereGeometry(.3, 16, 12), mats.skin, 0, 1.93, -.02);
block(torso, new THREE.SphereGeometry(.31, 12, 7, 0, Math.PI * 2, 0, Math.PI * .52), mats.dark, 0, 2.03, -.04);
block(torso, new THREE.TorusGeometry(.3, .055, 6, 14, Math.PI), mats.gold, 0, 1.98, .03);
block(torso, new THREE.CylinderGeometry(.34, .3, .1, 12), mats.gold, 0, 2.12, .01);
block(torso, new THREE.SphereGeometry(.27, 12, 8, 0, Math.PI * 2, 0, Math.PI * .48), mats.coral, 0, 2.19, -.01);
const scarf = block(torso, new THREE.BoxGeometry(.55, .14, .12), mats.gold, 0, 1.64, .04);
scarf.rotation.z = -.08;
const scarfTail = block(torso, new THREE.BoxGeometry(.13, .55, .08), mats.gold, 0, 1.54, .48);
scarfTail.rotation.x = .28;
const leftArm = new THREE.Group(); leftArm.position.set(-.43, 1.42, 0); torso.add(leftArm);
block(leftArm, new THREE.CapsuleGeometry(.12, .48, 3, 6), mats.coral, 0, -.28, 0);
block(leftArm, new THREE.SphereGeometry(.12, 10, 8), mats.skin, 0, -.59, .02);
const rightArm = new THREE.Group(); rightArm.position.set(.43, 1.42, 0); torso.add(rightArm);
block(rightArm, new THREE.CapsuleGeometry(.12, .48, 3, 6), mats.coral, 0, -.28, 0);
block(rightArm, new THREE.SphereGeometry(.12, 10, 8), mats.skin, 0, -.59, .02);
const leftLeg = new THREE.Group(); leftLeg.position.set(-.18, .47, 0); torso.add(leftLeg);
block(leftLeg, new THREE.CapsuleGeometry(.13, .42, 3, 6), mats.dark, 0, -.2, 0);
block(leftLeg, new THREE.BoxGeometry(.28, .16, .46), mats.stoneLight, 0, -.49, -.12);
const rightLeg = new THREE.Group(); rightLeg.position.set(.18, .47, 0); torso.add(rightLeg);
block(rightLeg, new THREE.CapsuleGeometry(.13, .42, 3, 6), mats.dark, 0, -.2, 0);
block(rightLeg, new THREE.BoxGeometry(.28, .16, .46), mats.stoneLight, 0, -.49, -.12);
scene.add(player);
player.position.set(0, 0, 2.0);

function makeObstacle(kind, lane, z) {
    const group = new THREE.Group();
    group.position.set(lanePositions[lane], 0, z);
    if (kind === 'barrier') {
        block(group, new THREE.BoxGeometry(1.45, .78, .62), mats.stone, 0, .45, 0);
        block(group, new THREE.BoxGeometry(1.58, .18, .72), mats.gold, 0, .85, 0);
        for (let mark = -1; mark <= 1; mark++) block(group, new THREE.BoxGeometry(.08, .46, .64), mats.stoneLight, mark * .42, .43, .02, false);
    } else {
        block(group, new THREE.BoxGeometry(.2, 2.25, .3), mats.stoneLight, -.68, 1.1, 0);
        block(group, new THREE.BoxGeometry(.2, 2.25, .3), mats.stoneLight, .68, 1.1, 0);
        block(group, new THREE.BoxGeometry(1.58, .3, .38), mats.stone, 0, 2.12, 0);
        block(group, new THREE.BoxGeometry(1.1, .12, .42), mats.gold, 0, 1.91, 0, false);
    }
    scene.add(group);
    return { group, lane, kind, hit: false };
}

function makeRelic(lane, z) {
    const group = new THREE.Group();
    group.position.set(lanePositions[lane], 1.18, z);
    const ring = block(group, new THREE.TorusGeometry(.31, .085, 8, 18), mats.gold, 0, 0, 0, false);
    ring.rotation.y = .18;
    block(group, new THREE.OctahedronGeometry(.17, 0), mats.gold, 0, 0, 0, false);
    const glow = new THREE.PointLight('#ffc84d', 1.2, 3);
    group.add(glow);
    scene.add(group);
    return { group, lane, collected: false };
}

let obstacles = [];
let relics = [];
let active = false;
let paused = false;
let gameOver = false;
let currentLane = 1;
let jumpTime = 0;
let slideTime = 0;
let spawnClock = .7;
let elapsed = 0;
let distance = 0;
let relicCount = 0;
let best = Number(localStorage.getItem('templeDashBest') || 0);
let toastClock = 0;
bestValue.textContent = best + ' m';

function clearRunObjects(list) {
    for (const item of list) scene.remove(item.group);
    list.length = 0;
}

function beginRun() {
    clearRunObjects(obstacles);
    clearRunObjects(relics);
    active = true; paused = false; gameOver = false;
    currentLane = 1; jumpTime = 0; slideTime = 0; spawnClock = .75;
    elapsed = 0; distance = 0; relicCount = 0;
    player.position.x = 0; player.position.y = 0; player.scale.y = 1;
    distanceValue.innerHTML = '0 <i>m</i>';
    relicValue.textContent = '0';
    progressBar.style.width = '0%';
    overlayTitle.innerHTML = 'TEMPLE<br><em>DASH</em>';
    overlayCopy.textContent = 'The guardian is awake. Grab relics, dodge the ruins, and find your way out.';
    startOverlay.classList.add('hidden');
    pauseButton.textContent = 'Ⅱ';
}

function finishRun() {
    active = false; gameOver = true;
    const finalDistance = Math.floor(distance);
    if (finalDistance > best) {
        best = finalDistance;
        localStorage.setItem('templeDashBest', String(best));
        bestValue.textContent = best + ' m';
    }
    overlayTitle.innerHTML = 'THE TEMPLE<br><em>CLAIMS YOU</em>';
    overlayCopy.textContent = `${finalDistance} m escaped · ${relicCount} relics found. The guardian is still waiting.`;
    document.getElementById('runStart').innerHTML = 'RUN IT BACK <span>↗</span>';
    startOverlay.classList.remove('hidden');
}

function perform(action) {
    if (!active) return;
    if (action === 'left') currentLane = Math.max(0, currentLane - 1);
    if (action === 'right') currentLane = Math.min(2, currentLane + 1);
    if (action === 'jump' && jumpTime <= 0 && slideTime <= 0) jumpTime = .82;
    if (action === 'slide' && slideTime <= 0 && jumpTime <= 0) slideTime = .72;
}

document.getElementById('runStart').addEventListener('click', () => {
    if (paused) {
        paused = false;
        pauseButton.textContent = 'Ⅱ';
        startOverlay.classList.add('hidden');
    } else beginRun();
});
document.querySelectorAll('[data-move]').forEach(button => button.addEventListener('click', () => perform(button.dataset.move)));
document.getElementById('pauseButton').addEventListener('click', () => {
    if (!active && !paused) return;
    paused = !paused;
    pauseButton.textContent = paused ? '▶' : 'Ⅱ';
    if (paused) {
        overlayTitle.innerHTML = 'TAKE A<br><em>BREATHER</em>';
        overlayCopy.textContent = 'Your escape is paused. The guardian can wait a moment.';
        document.getElementById('runStart').innerHTML = 'KEEP RUNNING <span>↗</span>';
        startOverlay.classList.remove('hidden');
    } else {
        startOverlay.classList.add('hidden');
    }
});
window.addEventListener('keydown', event => {
    const actions = { ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', ArrowUp: 'jump', Space: 'jump', ArrowDown: 'slide', KeyS: 'slide' };
    if (actions[event.code]) { event.preventDefault(); perform(actions[event.code]); }
    if (event.code === 'Escape' && active) document.getElementById('pauseButton').click();
});

const clock = new THREE.Clock();
function showRelicToast() {
    toast.classList.add('show');
    toastClock = .8;
}

function updateGame(delta) {
    if (!active || paused) return;
    elapsed += delta;
    const speed = 13 + Math.min(distance * .035, 9);
    distance += delta * speed * .36;
    distanceValue.innerHTML = `${Math.floor(distance)} <i>m</i>`;
    progressBar.style.width = `${Math.min(distance / 850 * 100, 100)}%`;
    spawnClock -= delta;
    if (spawnClock <= 0) {
        const lane = Math.floor(Math.random() * 3);
        if (Math.random() < .7) obstacles.push(makeObstacle(Math.random() < .64 ? 'barrier' : 'gate', lane, -42));
        else {
            const coinLane = Math.floor(Math.random() * 3);
            for (let coin = 0; coin < 4; coin++) relics.push(makeRelic(coinLane, -37 - coin * 2.1));
        }
        spawnClock = Math.max(.72, 1.28 - distance / 900) + Math.random() * .42;
    }

    for (const slab of tileRuns) {
        slab.position.z += speed * delta;
        if (slab.position.z > 7) slab.position.z -= 68.4;
    }
    for (const prop of scenery) {
        prop.position.z += speed * delta;
        if (prop.position.z > 12) prop.position.z -= 66.4;
        for (const child of prop.children) if (child.userData.flicker) child.scale.y = 1.4 + Math.sin(elapsed * 17 + prop.position.z) * .25;
    }
    player.position.x += (lanePositions[currentLane] - player.position.x) * Math.min(delta * 12, 1);
    camera.position.x += (player.position.x * .18 - camera.position.x) * Math.min(delta * 2.5, 1);
    camera.lookAt(player.position.x * .12, 1.25, -7);
    if (jumpTime > 0) {
        jumpTime = Math.max(0, jumpTime - delta);
        player.position.y = Math.sin((.82 - jumpTime) / .82 * Math.PI) * 1.55;
    } else player.position.y = 0;
    if (slideTime > 0) {
        slideTime = Math.max(0, slideTime - delta);
        player.scale.y = .62;
    } else player.scale.y = 1;
    const runCycle = Math.sin(elapsed * (slideTime > 0 ? 4 : 13));
    leftLeg.rotation.x = runCycle * (slideTime > 0 ? .12 : .58);
    rightLeg.rotation.x = -runCycle * (slideTime > 0 ? .12 : .58);
    leftArm.rotation.x = -runCycle * .55;
    rightArm.rotation.x = runCycle * .55;
    scarfTail.rotation.z = Math.sin(elapsed * 12) * .14;
    torso.rotation.z += (currentLane - 1) * delta * .12;
    torso.rotation.z *= .985;

    for (const obstacle of obstacles) {
        obstacle.group.position.z += speed * delta;
        if (!obstacle.hit && obstacle.group.position.z > 1.25 && obstacle.group.position.z < 2.25 && obstacle.lane === currentLane) {
            obstacle.hit = true;
            const avoided = obstacle.kind === 'barrier' ? jumpTime > .1 : slideTime > .1;
            if (!avoided) finishRun();
        }
    }
    obstacles = obstacles.filter(obstacle => {
        if (obstacle.group.position.z > 12) { scene.remove(obstacle.group); return false; }
        return true;
    });
    for (const relic of relics) {
        relic.group.position.z += speed * delta;
        relic.group.rotation.y += delta * 2.5;
        relic.group.position.y = 1.2 + Math.sin(elapsed * 5 + relic.group.position.z) * .12;
        if (!relic.collected && relic.group.position.z > 1.15 && relic.group.position.z < 2.6 && relic.lane === currentLane) {
            relic.collected = true; relicCount++; relicValue.textContent = String(relicCount); scene.remove(relic.group); showRelicToast();
        }
    }
    relics = relics.filter(relic => {
        if (relic.collected || relic.group.position.z > 12) { scene.remove(relic.group); return false; }
        return true;
    });
    if (toastClock > 0) { toastClock -= delta; if (toastClock <= 0) toast.classList.remove('show'); }
}

function resize() {
    const width = Math.max(1, shell.clientWidth);
    const height = Math.max(1, shell.clientHeight);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(shell);
resize();

function animate() {
    const delta = Math.min(clock.getDelta(), .05);
    updateGame(delta);
    renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
</script>
"""

# --- Database Functions ---

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    mongo_client.admin.command("ping")
    mongo_db = mongo_client[MONGO_DB_NAME]
    MONGO_AVAILABLE = True
except Exception:
    mongo_client = None
    mongo_db = None
    MONGO_AVAILABLE = False


def init_db():
    if mongo_db is None:
        return
    mongo_db.mood_logs.create_index([("user_id", 1), ("timestamp", 1)])
    mongo_db.memes.create_index([("created_at", -1)])
    mongo_db.jokes.create_index([("created_at", -1)])


def save_community_meme(meme):
    if mongo_db is None:
        return False
    try:
        mongo_db.memes.insert_one({**meme, "created_at": datetime.now().isoformat(timespec="seconds")})
        return True
    except PyMongoError:
        return False


def get_community_memes():
    if mongo_db is None:
        return None
    try:
        return list(
            mongo_db.memes.find({}, {"title": 1, "desc": 1, "image": 1, "user_id": 1, "created_at": 1})
            .sort("created_at", -1)
        )
    except PyMongoError:
        return None


def save_community_joke(joke):
    if mongo_db is None:
        return False
    try:
        mongo_db.jokes.insert_one({**joke, "created_at": datetime.now().isoformat(timespec="seconds")})
        return True
    except PyMongoError:
        return False


def get_community_jokes():
    if mongo_db is None:
        return None
    try:
        return list(
            mongo_db.jokes.find({}, {"category": 1, "text": 1, "user_id": 1, "created_at": 1})
            .sort("created_at", -1)
        )
    except PyMongoError:
        return None


def update_community_meme(post_id, title, description):
    if mongo_db is None:
        return False
    try:
        result = mongo_db.memes.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"title": title.strip(), "desc": description.strip()}},
        )
        return result.matched_count == 1
    except (PyMongoError, ValueError):
        return False


def delete_community_meme(post_id):
    if mongo_db is None:
        return False
    try:
        return mongo_db.memes.delete_one({"_id": ObjectId(post_id)}).deleted_count == 1
    except (PyMongoError, ValueError):
        return False


def update_community_joke(post_id, category, text):
    if mongo_db is None:
        return False
    try:
        result = mongo_db.jokes.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"category": category, "text": text.strip()}},
        )
        return result.matched_count == 1
    except (PyMongoError, ValueError):
        return False


def delete_community_joke(post_id):
    if mongo_db is None:
        return False
    try:
        return mongo_db.jokes.delete_one({"_id": ObjectId(post_id)}).deleted_count == 1
    except (PyMongoError, ValueError):
        return False


def save_mood_log(user_id, mood_score, recommendation):
    if mongo_db is None:
        return
    mongo_db.mood_logs.insert_one(
        {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "mood_score": mood_score,
            "recommendation": recommendation,
        }
    )


def get_user_history(user_id):
    if mongo_db is None:
        return pd.DataFrame(columns=["id", "user_id", "timestamp", "mood_score", "recommendation"])

    documents = list(mongo_db.mood_logs.find({"user_id": user_id}).sort("timestamp", 1))
    rows = []
    for doc in documents:
        rows.append(
            {
                "id": str(doc.get("_id")),
                "user_id": doc.get("user_id"),
                "timestamp": doc.get("timestamp"),
                "mood_score": doc.get("mood_score"),
                "recommendation": doc.get("recommendation"),
            }
        )
    return pd.DataFrame(rows)

def hash_pseudonym(raw_id: str) -> str:
    raw_id = raw_id.strip().lower()
    return "FUN-" + hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:8].upper()

# --- UI Helpers ---

def inject_css():
    """Injects custom CSS for the fun theme."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Fredoka:wght@500;600;700&display=swap');

    .stApp {
        background:
            radial-gradient(ellipse at 4% 4%, rgba(255, 210, 76, 0.20), transparent 27%),
            radial-gradient(ellipse at 96% 18%, rgba(65, 196, 177, 0.15), transparent 25%),
            #fffaf1;
        color: #282522;
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3, h4, [data-testid="stMetricValue"] {
        font-family: 'Fredoka', sans-serif !important;
        letter-spacing: 0;
    }
    h1 { color: #e8593d; }
    .stCaption, [data-testid="stCaption"] { color: #73695f; }
    .stButton > button, [data-testid="stFormSubmitButton"] button {
        border: 2px solid #282522;
        border-radius: 12px;
        background: #ffd24c;
        color: #282522;
        font-family: 'DM Sans', sans-serif;
        font-weight: 800;
        transition: transform 140ms ease, box-shadow 140ms ease, background 140ms ease;
        box-shadow: 0 3px 0 #282522;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px) rotate(-1deg);
        background: #ffbd59;
        box-shadow: 0 5px 0 #282522;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif;
        font-weight: 800;
        padding: 10px 16px;
    }
    [data-baseweb="tab-highlight"] { background: #e8593d; }
    [data-testid="stForm"] {
        border: 2px solid #282522;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 5px 5px 0 #282522;
        padding: 20px;
    }
    [data-testid="stFileUploader"] section {
        border: 2px dashed #e8593d;
        border-radius: 12px;
        background: #fff5e8;
    }
    [data-testid="stExpander"] {
        border-color: rgba(40, 37, 34, 0.22);
        border-radius: 12px;
    }
    @media (max-width: 640px) {
        [data-testid="stForm"] { padding: 14px; }
        .stTabs [data-baseweb="tab"] { padding: 8px 7px; font-size: 0.83rem; }
    }
    </style>
    """, unsafe_allow_html=True)

def hero_header(title, subtitle, chips=None):
    st.title(title)
    st.subheader(subtitle)
    if chips:
        cols = st.columns(len(chips))
        for col, chip in zip(cols, chips):
            col.info(chip)

# --- Page Setup ---

st.set_page_config(
    page_title="Giggle and Laugh",
    page_icon="😂",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()
if not MONGO_AVAILABLE:
    st.warning("MongoDB is not connected. Mood history, memes, and jokes will only be saved for this session.")
inject_css()

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "community_memes" not in st.session_state:
    st.session_state.community_memes = []
if "community_jokes" not in st.session_state:
    st.session_state.community_jokes = []
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# --- Sidebar ---

with st.sidebar:
    st.markdown("## 😂 Giggle and Laugh")
    st.caption(APP_SUBTITLE)
    st.divider()

    if not st.session_state.logged_in:
        st.info("Log in from the main page to unlock all tabs.")
    else:
        st.success(f"Hi there, **{st.session_state.user_id}**")
        if st.button("End Session", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            # Clear other session keys to prevent stale state errors
            for k in list(st.session_state.keys()):
                if k not in ("logged_in", "user_id"):
                    del st.session_state[k]
            st.rerun()

    st.divider()
    with st.expander("🔐 Owner controls", expanded=st.session_state.admin_authenticated):
        if not APP_ADMIN_PASSWORD:
            st.caption("Set APP_ADMIN_PASSWORD in Streamlit secrets to enable content management.")
        elif st.session_state.admin_authenticated:
            st.success("Owner access is enabled for this session.")
            if st.button("Lock owner tools", key="admin_logout", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.rerun()
        else:
            with st.form("admin_login_form"):
                admin_password_entry = st.text_input("Owner password", type="password")
                admin_unlock = st.form_submit_button("Unlock management")
            if admin_unlock:
                if hmac.compare_digest(admin_password_entry, APP_ADMIN_PASSWORD):
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("That owner password did not match.")

# --- Main Content ---

st.title("😂 Giggle and Laugh")
st.caption("Because life is too short to be serious all the time.")

if not st.session_state.logged_in:
    hero_header(
        "Welcome to Giggle and Laugh",
        "Play games, read jokes, view memes, and track your vibe.",
        chips=[
            "🎮 Mini Games",
            "😂 Hilarious Jokes",
            "🖼️ Meme Gallery",
            "🧘 Mood Tracker"
        ],
    )

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("#### 👋 Quick Login")
        with st.form("login_form"):
            raw_id = st.text_input("Nickname", placeholder="e.g. Chuckles")
            go = st.form_submit_button("Start Laughing 🎈", use_container_width=True, type="primary")
        if go:
            if raw_id.strip():
                st.session_state.user_id = hash_pseudonym(raw_id)
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.warning("Please enter a nickname to continue.")

    with right:
        st.markdown("#### ✨ What's inside")
        st.markdown("""
        - **Vibe Check** — log your mood, see your trend
        - **Games Zone** — clicker, Flap Dash, Temple Dash, and Rock Paper Scissors
        - **Meme Gallery** — instant laughs
        - **Joke Factory** — filterable puns & one-liners
        """)

    st.stop()  # Only stops here, AFTER showing the login UI


# ---- Tabs (only reached when logged in) ----

tab_vibe, tab_games, tab_memes, tab_jokes = st.tabs(
    [
        "🧘 Vibe Check",
        "🎮 Games Zone",
        "🖼️ Meme Gallery",
        "😂 Joke Factory",
    ]
)

# 1. VIBE CHECK
with tab_vibe:
    st.markdown("### How's your vibe today?")
    st.caption("Quickly tell us how you're feeling so we can recommend some content.")
    
    vibe_options = ["😢 Low Energy", "😐 Neutral", "🙂 Good", "🤩 Great"]
    vibe_scores = [1, 2, 3, 4]
    
    selected_vibe_idx = st.radio("Select your current mood:", range(len(vibe_options)), format_func=lambda x: vibe_options[x], horizontal=True)
    
    if st.button("Get Recommendation"):
        score = vibe_scores[selected_vibe_idx]
        rec_text = ""
        
        if score <= 2:
            rec_text = "You need a pick-me-up! Check out the 'Joke Factory' for puns, or play a game to distract yourself."
            st.info(rec_text)
        elif score == 3:
            rec_text = "Looking good! Maybe some funny memes will boost your mood even higher."
            st.success(rec_text)
        else:
            rec_text = "Wow, great energy! Share a joke with someone else to spread the love."
            st.balloons()
            st.success(rec_text)
            
        # Save to DB
        save_mood_log(st.session_state.user_id, score, rec_text)
        st.toast("Vibe logged successfully!")

    st.divider()
    st.markdown("#### Your Recent Vibes")
    history_df = get_user_history(st.session_state.user_id)
    if not history_df.empty:
        chart_df = history_df.copy()
        chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"])
        st.line_chart(chart_df.set_index("timestamp")[["mood_score"]])
    else:
        st.write("No vibes logged yet. Click above to log one!")

# 2. GAMES ZONE
with tab_games:
    st.markdown("### 🎮 Arcade Mode")
    st.write("Pick a game and take the scenic route through your break.")
    clicker_tab, flappy_tab, runner_tab, rps_tab = st.tabs(
        ["✨ Clicker", "🐤 Flap Dash", "🏛️ Temple Dash", "✊ Rock Paper Scissors"]
    )

    with clicker_tab:
        components.html(GAMES_HTML, height=350)

    with flappy_tab:
        components.html(FLAPPY_HTML, height=455)

    with runner_tab:
        components.html(RUNNER_HTML, height=700)

    with rps_tab:
        st.markdown("#### ✊✋✌️ Rock, Paper, Scissors")
        if "rps_result" not in st.session_state:
            st.session_state.rps_result = "Make your move!"

        choices = ["Rock", "Paper", "Scissors"]
        col1, col2, col3 = st.columns(3)

        def play_rps(choice):
            computer = random.choice(choices)
            msg = f"You chose {choice}. Computer chose {computer}. "

            if choice == computer:
                msg += "It's a tie! 🤝"
            elif (choice == "Rock" and computer == "Scissors") or \
                 (choice == "Paper" and computer == "Rock") or \
                 (choice == "Scissors" and computer == "Paper"):
                msg += "You win! 🏆"
            else:
                msg += "You lose! 😅"

            st.session_state.rps_result = msg

        with col1:
            if st.button("Rock", use_container_width=True):
                play_rps("Rock")
        with col2:
            if st.button("Paper", use_container_width=True):
                play_rps("Paper")
        with col3:
            if st.button("Scissors", use_container_width=True):
                play_rps("Scissors")

        st.info(st.session_state.rps_result)

# 3. MEME GALLERY
with tab_memes:
    st.markdown("### 🖼️ Meme Gallery")
    community_meme_tab, template_tab = st.tabs(["🌐 User Uploads", "🧩 Meme Templates"])

    with community_meme_tab:
        st.caption("Memes uploaded by the community appear here for everyone.")
        if st.button("Refresh community memes ↻"):
            st.rerun()

        with st.expander("✨ Upload a meme", expanded=False):
            with st.form("meme_upload_form", clear_on_submit=True):
                meme_title = st.text_input("Give it a title", max_chars=60, placeholder="The 2am snack situation")
                meme_caption = st.text_area("What's the joke?", max_chars=240, placeholder="Me: just one bite. Also me:")
                meme_image = st.file_uploader(
                    "Choose an image (PNG, JPG, or WebP; up to 5 MB)",
                    type=["png", "jpg", "jpeg", "webp"],
                    key="meme_image_upload",
                    max_upload_size=5,
                )
                meme_submitted = st.form_submit_button("Pin it to the wall 📌", use_container_width=True)
            if meme_submitted:
                if not meme_title.strip() or not meme_caption.strip() or meme_image is None:
                    st.warning("Add a title, a caption, and an image to post your meme.")
                elif meme_image.size > 5 * 1024 * 1024:
                    st.warning("That image is over 5 MB. Try a smaller one so the wall stays snappy.")
                else:
                    meme = {
                        "title": meme_title.strip(),
                        "desc": meme_caption.strip(),
                        "image": meme_image.getvalue(),
                        "user_id": st.session_state.user_id,
                    }
                    if save_community_meme(meme):
                        st.toast("Your meme is on the shared wall! 🎉")
                        st.rerun()
                    else:
                        st.session_state.community_memes.append(meme)
                        st.warning("MongoDB could not save this post. It is only visible in your session, not to everyone.")

        stored_memes = get_community_memes()
        if stored_memes is None:
            st.warning("The shared meme wall is unavailable right now. Session-only previews are marked below.")
            stored_memes = []
        community_memes = stored_memes + st.session_state.community_memes
        if community_memes:
            st.markdown("#### Community uploads")
            cols = st.columns(2)
            for index, meme in enumerate(community_memes):
                with cols[index % 2]:
                    st.markdown(f"#### {meme['title']}")
                    if meme.get("image"):
                        st.image(meme["image"], use_container_width=True)
                    is_session_only = meme in st.session_state.community_memes
                    st.caption("Session-only preview" if is_session_only else "Shared community meme")
                    st.caption(meme["desc"])
        else:
            st.info("No community memes yet. Be the first to post one!")

        if st.session_state.admin_authenticated:
            st.divider()
            st.markdown("#### 🛠️ Manage uploaded memes")
            if stored_memes:
                meme_lookup = {str(meme["_id"]): meme for meme in stored_memes}
                selected_meme_id = st.selectbox(
                    "Choose a meme",
                    list(meme_lookup),
                    format_func=lambda post_id: meme_lookup[post_id]["title"],
                    key="meme_admin_selection",
                )
                selected_meme = meme_lookup[selected_meme_id]
                with st.form(f"edit_meme_{selected_meme_id}"):
                    edited_meme_title = st.text_input("Meme title", value=selected_meme["title"])
                    edited_meme_desc = st.text_area("Meme caption", value=selected_meme["desc"])
                    save_meme_changes = st.form_submit_button("Save changes")
                if save_meme_changes:
                    if update_community_meme(selected_meme_id, edited_meme_title, edited_meme_desc):
                        st.toast("Meme updated for everyone.")
                        st.rerun()
                    else:
                        st.error("Could not update this meme.")
                if st.button("Delete selected meme", key=f"delete_meme_{selected_meme_id}"):
                    if delete_community_meme(selected_meme_id):
                        st.toast("Meme removed from the shared wall.")
                        st.rerun()
                    else:
                        st.error("Could not delete this meme.")
            else:
                st.info("There are no saved community memes to manage.")

    with template_tab:
        st.caption("Browse the built-in meme prompts.")
        cols = st.columns(2)
        for index, meme in enumerate(MEME_TEMPLATES):
            with cols[index % 2]:
                st.markdown(f"#### {meme['title']}")
                st.markdown(f"<div style='background:#ffe8b8;padding:24px;text-align:center;font-size:48px;border:2px solid #282522;border-radius:14px'>{meme['emoji']}</div>", unsafe_allow_html=True)
                st.caption(meme["desc"])

# 4. JOKE FACTORY
with tab_jokes:
    st.markdown("### 😂 Joke Factory")
    community_joke_tab, joke_library_tab = st.tabs(["🌐 User Uploads", "📚 Joke Library"])

    with community_joke_tab:
        st.caption("Jokes submitted by users appear here for everyone.")
        if st.button("Refresh community jokes ↻"):
            st.rerun()

        with st.expander("🎤 Submit a joke", expanded=False):
            with st.form("joke_submit_form", clear_on_submit=True):
                submitted_joke = st.text_area("Your one-liner", max_chars=300, placeholder="Why did the scarecrow win an award?...")
                submitted_category = st.selectbox("Pick a shelf", ["Puns", "Tech", "Animals", "Work", "Science", "Food", "General"])
                joke_submitted = st.form_submit_button("Send it to the laugh lab 🧪", use_container_width=True)
            if joke_submitted:
                if submitted_joke.strip():
                    joke = {
                        "category": submitted_category,
                        "text": submitted_joke.strip(),
                        "user_id": st.session_state.user_id,
                    }
                    if save_community_joke(joke):
                        st.toast("Joke added to the shared laugh lab! 😄")
                        st.rerun()
                    else:
                        st.session_state.community_jokes.append(joke)
                        st.warning("MongoDB could not save this joke. It is only visible in your session, not to everyone.")
                else:
                    st.warning("Type a joke first. Even a terrible one counts.")

        stored_jokes = get_community_jokes()
        if stored_jokes is None:
            st.warning("The shared joke list is unavailable right now. Session-only previews are marked below.")
            stored_jokes = []
        community_jokes = stored_jokes + st.session_state.community_jokes
        if community_jokes:
            st.markdown("#### Community jokes")
            for joke in community_jokes:
                session_only = joke in st.session_state.community_jokes
                label = "Session-only preview · " if session_only else ""
                with st.expander(f"{label}{joke['category']}: {joke['text'][:50]}..."):
                    st.markdown(joke["text"])
        else:
            st.info("No community jokes yet. Share the first one!")

        if st.session_state.admin_authenticated:
            st.divider()
            st.markdown("#### 🛠️ Manage uploaded jokes")
            if stored_jokes:
                joke_lookup = {str(joke["_id"]): joke for joke in stored_jokes}
                selected_joke_id = st.selectbox(
                    "Choose a joke",
                    list(joke_lookup),
                    format_func=lambda post_id: f"{joke_lookup[post_id]['category']}: {joke_lookup[post_id]['text'][:45]}",
                    key="joke_admin_selection",
                )
                selected_joke = joke_lookup[selected_joke_id]
                with st.form(f"edit_joke_{selected_joke_id}"):
                    edited_joke_category = st.selectbox(
                        "Joke category",
                        ["Puns", "Tech", "Animals", "Work", "Science", "Food", "General"],
                        index=["Puns", "Tech", "Animals", "Work", "Science", "Food", "General"].index(selected_joke["category"]),
                    )
                    edited_joke_text = st.text_area("Joke text", value=selected_joke["text"])
                    save_joke_changes = st.form_submit_button("Save changes")
                if save_joke_changes:
                    if update_community_joke(selected_joke_id, edited_joke_category, edited_joke_text):
                        st.toast("Joke updated for everyone.")
                        st.rerun()
                    else:
                        st.error("Could not update this joke.")
                if st.button("Delete selected joke", key=f"delete_joke_{selected_joke_id}"):
                    if delete_community_joke(selected_joke_id):
                        st.toast("Joke removed from the shared laugh lab.")
                        st.rerun()
                    else:
                        st.error("Could not delete this joke.")
            else:
                st.info("There are no saved community jokes to manage.")

    with joke_library_tab:
        st.caption("The original Giggle and Laugh joke collection.")
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + sorted(set(joke["category"] for joke in JOKES_LIST)),
        )
        filtered_jokes = JOKES_LIST if category_filter == "All" else [
            joke for joke in JOKES_LIST if joke["category"] == category_filter
        ]
        st.markdown("#### 🔥 Hot Joke of the Moment")
        random_joke = random.choice(filtered_jokes)
        st.markdown(f"> **{random_joke['text']}**")
        st.caption(f"— Category: {random_joke['category']}")
        if st.button("Give me another one! 🔄"):
            st.rerun()
        st.divider()
        st.markdown("#### All Jokes")
        for joke in filtered_jokes:
            with st.expander(f"{joke['category']}: {joke['text'][:30]}..."):
                st.markdown(joke["text"])