"""
Giggle and Laugh 😂 — Your Daily Dose of Happiness
A fun, lighthearted wellness & entertainment portal for everyone.
"""

import os
import json
import base64
import mimetypes
import hmac
import html
import uuid
from datetime import datetime
from datetime import date, timedelta
from knowledge_content import INDIA_GK_QUESTIONS, RIDDLES
import pandas as pd
import streamlit as st
import random
from supabase import create_client
from app_helpers import (
    build_rps_leaderboard,
    build_mood_garden,
    calculate_activity_streak,
    count_recent_distress_checkins,
    get_profile_badges,
    get_rps_result,
    hash_pseudonym,
    summarize_mood_scores,
    summarize_mood_pulse,
    validate_chat_attachment,
)

# --- Configuration Constants ---

def config_value(name, default):
    environment_value = os.getenv(name)
    if environment_value:
        return environment_value
    try:
        return st.secrets.get(name, default)
    except st.errors.StreamlitSecretNotFoundError:
        return default


SUPABASE_URL = config_value("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = config_value("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_MEME_BUCKET = config_value("SUPABASE_MEME_BUCKET", "community-memes")
SUPABASE_CHAT_BUCKET = config_value("SUPABASE_CHAT_BUCKET", "community-chat")
APP_ADMIN_PASSWORD = config_value("APP_ADMIN_PASSWORD", "")
COUNSELING_CENTER_NAME = config_value("COUNSELING_CENTER_NAME", "")
COUNSELING_CENTER_PHONE = config_value("COUNSELING_CENTER_PHONE", "")
APP_TITLE = "Giggle and Laugh"
APP_SUBTITLE = "A lighter place to take a break."

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
    {
        "title": "Distracted Boyfriend",
        "desc": "Me looking at dessert when I said I'm on a diet.",
        "emoji": "👀🍰",
        "mood_label": "Pulled in two directions",
        "mood_score": 2,
        "emotion": "Torn between competing priorities.",
    },
    {
        "title": "Drake Hotline Bling",
        "desc": "Working Hard: ❌ | Taking a Nap: ✅",
        "emoji": "🙅‍♂️😴",
        "mood_label": "Choosing rest",
        "mood_score": 1,
        "emotion": "Low energy and ready to take a break.",
    },
    {
        "title": "Two Buttons",
        "desc": "Sleep Early vs. Watch One More Episode",
        "emoji": "😵💤📺",
        "mood_label": "Decision overload",
        "mood_score": 1,
        "emotion": "Overwhelmed by too many small decisions.",
    },
    {
        "title": "Expanding Brain",
        "desc": "Coffee → Espresso → Caffeine IV Drip",
        "emoji": "🧠☕⚡",
        "mood_label": "Caffeine-fueled",
        "mood_score": 3,
        "emotion": "Running on determination and a little caffeine.",
    },
    {
        "title": "This is Fine",
        "desc": "Me when the deadline is tomorrow but today is fine.",
        "emoji": "🔥🐶☕",
        "mood_label": "Overwhelmed but coping",
        "mood_score": 1,
        "emotion": "Overwhelmed, but finding a way to cope.",
    },
    {
        "title": "Change My Mind",
        "desc": "Pineapple belongs on pizza. Change my mind.",
        "emoji": "🍕🤔",
        "mood_label": "Playfully confident",
        "mood_score": 4,
        "emotion": "Feeling upbeat and ready to share an opinion.",
    },
]


def build_data_url_from_file(filename):
    base_path = os.path.join(os.path.dirname(__file__), filename)
    mime_type = mimetypes.guess_type(base_path)[0] or "image/png"
    with open(base_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


JUMPSCARE_IMAGES = [
    build_data_url_from_file(filename)
    for filename in [
        "Pasted Image",
        "Pasted Image 2",
        "Pasted Image 3",
        "Pasted Image 4",
        "Pasted Image 5",
        "Pasted Image 6",
        "Screenshot 2026-10-12 at 11.22.20 AM.png",
        "image.png",
        "Donald Trump GIF by Neon Indian.gif",
        "donald trump GIF.gif",
        "giphy (1).gif",
        "giphy (3).gif",
        "giphy.gif",
    ]
    if os.path.exists(os.path.join(os.path.dirname(__file__), filename))
]

# --- Games HTML (Clicker Game) ---
GAMES_HTML = """
<div class="clicker-game">
    <h3>SUPER CLICKER</h3>
    <p>Keep tapping. You never know who might show up.</p>
    <button id="clickBtn">CLICK ME</button>
    <h2 id="count">0</h2>
    <div class="surprise-overlay" id="surpriseOverlay" aria-hidden="true">
        <button class="surprise-close" id="surpriseClose" aria-label="Close surprise">×</button>
        <img id="surpriseImage" alt="surprise" />
        <strong id="surpriseTitle">JUMPSCARE!</strong>
        <span id="surpriseCaption">The button was never the same again.</span>
    </div>
</div>
<style>
    .clicker-game{position:relative;min-height:300px;padding:20px;overflow:hidden;text-align:center;background:radial-gradient(ellipse at 50% 110%,#ffdf8a 0,#fff5e8 65%);color:#292b30;font-family:'Nunito',sans-serif}
    .clicker-game h3{margin:2px 0 4px;font-size:24px}.clicker-game p{margin:4px 0 14px;color:#70695f;font-size:14px}
    #clickBtn{position:relative;z-index:1;min-width:176px;min-height:70px;padding:16px 28px;border:3px solid #282522;border-radius:50%;background:#ff6b35;color:white;font-size:21px;font-weight:900;cursor:pointer;box-shadow:0 6px #c44d28;transition:transform .1s,background .12s}
    #clickBtn:active{transform:translateY(4px);box-shadow:0 2px #c44d28}.clicker-game #count{margin:12px 0 0;font-size:36px;color:#2d2a32}
    .surprise-overlay{position:absolute;z-index:4;inset:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;border:4px solid #f5c15b;background:radial-gradient(ellipse at center,#712a31,#171b26 78%);color:#fff1d0;opacity:0;visibility:hidden;transform:scale(.65) rotate(-3deg);transition:opacity .15s ease,transform .2s cubic-bezier(.2,.9,.25,1.25),visibility .15s;font-family:'Courier New',monospace}
    .surprise-overlay.visible{opacity:1;visibility:visible;transform:scale(1) rotate(0)}.surprise-overlay strong{font-size:19px;color:#ffdc76;text-shadow:2px 2px #8d242b}.surprise-overlay span{font-size:11px}
    .surprise-close{position:absolute;top:5px;right:8px;width:30px;height:30px;border:1px solid #fff1d0;background:#282522;color:#fff1d0;font-size:23px;line-height:1;cursor:pointer}
    #surpriseImage{max-width:90%;max-height:72%;object-fit:contain;border:4px solid rgba(255,255,255,.25);box-shadow:0 0 30px rgba(0,0,0,.30);background:#000}
    @media(prefers-reduced-motion:reduce){.surprise-overlay,#clickBtn{transition:none}}
</style>
    <script>
        const jumpscareImages = __JUMPSCARE_IMAGES__;
        let count = 0;
        let surpriseTimer;
        let scareIndex = 0;
        function shuffle(items) {
            const next = [...items];
            for (let i = next.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [next[i], next[j]] = [next[j], next[i]];
            }
            return next;
        }
        let scareQueue = shuffle(jumpscareImages);

        function nextScareImage() {
            if (!jumpscareImages.length) return '';
            const current = scareQueue[scareIndex % scareQueue.length];
            scareIndex += 1;
            if (scareIndex % scareQueue.length === 0) {
                scareQueue = shuffle(jumpscareImages);
            }
            return current;
        }

        function increment() {
            count++;
            document.getElementById('count').innerText = count;
            const btn = document.getElementById('clickBtn');
            const colors = ['#FF6B35', '#4CC9F0', '#F72585', '#4361EE', '#7209B7'];
            const shadows = ['#c44d28', '#3ab0d9', '#c4176b', '#3548c2', '#5a078d'];
            const rand = Math.floor(Math.random() * colors.length);
            btn.style.backgroundColor = colors[rand];
            btn.style.boxShadow = '0 6px ' + shadows[rand];
            if (Math.random() < 0.09 && jumpscareImages.length) {
                const overlay = document.getElementById('surpriseOverlay');
                const image = document.getElementById('surpriseImage');
                const chosen = nextScareImage();
                image.src = chosen;
                image.alt = 'jump scare image';
                document.getElementById('surpriseTitle').textContent = 'JUMPSCARE!';
                document.getElementById('surpriseCaption').textContent = 'Every scare gets a turn.';
                overlay.classList.add('visible');
                overlay.setAttribute('aria-hidden', 'false');
                clearTimeout(surpriseTimer);
                surpriseTimer = setTimeout(closeSurprise, 1800);
            }
        }

        function closeSurprise() {
            const overlay = document.getElementById('surpriseOverlay');
            overlay.classList.remove('visible');
            overlay.setAttribute('aria-hidden', 'true');
        }

        document.getElementById('clickBtn').addEventListener('click', increment);
        document.getElementById('surpriseClose').addEventListener('click', closeSurprise);
    </script>
</div>
"""

GAMES_HTML = GAMES_HTML.replace("__JUMPSCARE_IMAGES__", json.dumps(JUMPSCARE_IMAGES))

PLATFORMER_HTML = """
<div class="skyway-shell" id="skywayShell">
    <canvas id="skywayCanvas" aria-label="Skyway Sprint 3D endless platform game" tabindex="0"></canvas>
    <div class="skyway-topbar"><strong>SKYWAY<br><b>SPRINT</b></strong><div><small>DISTANCE</small><b id="skyDistance">0000 m</b></div><div><small>LEVEL</small><b id="skyLevel">01</b></div><div><small>GEMS</small><b id="skyGems">0</b></div><div><small>BEST</small><b id="skyBest">0000 m</b></div></div>
    <div class="skyway-toast" id="skyToast"></div>
    <section class="skyway-overlay" id="skyOverlay">
        <div class="skyway-title"><small>ENDLESS 3D PLATFORM ADVENTURE</small><h2 id="skyTitle">SKYWAY<br><em>SPRINT</em></h2><p id="skyCopy">Leap the gaps, dodge the clockwork hazards, and see how far the sky road goes.</p>
            <label class="hero-picker">RUNNER <select id="heroSelect"><option value="courier">The Courier</option><option value="showman">The Showman (cartoon parody)</option><option value="starlight">Starlight Pilot</option></select></label>
            <button id="skyStart">START RUN <span>↗</span></button><small class="sky-controls-hint">A / D OR ← / → SWITCH LANES · SPACE / ↑ JUMP</small>
        </div>
    </section>
    <div class="skyway-touch"><button data-sky="left" aria-label="Move left">◀</button><button data-sky="jump">JUMP</button><button data-sky="right" aria-label="Move right">▶</button></div>
    <div class="skyway-foot"><span>ENDLESS SKY ROAD</span><span id="skyState">READY</span></div>
</div>
<style>
    .skyway-shell{position:relative;width:100%;height:clamp(430px,68vw,650px);min-height:430px;max-height:680px;overflow:hidden;border:1px solid #37525a;background:#b9e4d7;color:#19343d;font-family:'Courier New',monospace;isolation:isolate}
    #skywayCanvas{position:absolute;inset:0;width:100%;height:100%;display:block;outline:none;touch-action:none}
    .skyway-topbar{position:absolute;z-index:2;top:12px;left:14px;right:14px;display:flex;align-items:center;gap:10px;color:#fff6db;text-shadow:1px 2px #233d43;pointer-events:none}
    .skyway-topbar>strong{margin-right:auto;font-size:13px;line-height:.9;letter-spacing:1px}.skyway-topbar>strong b{color:#ffd267}
    .skyway-topbar>div{min-width:68px;padding:5px 8px;border:1px solid rgba(255,246,219,.55);background:rgba(22,51,56,.62);text-align:center}
    .skyway-topbar small{display:block;color:#d8e8d1;font-size:8px;letter-spacing:1px}.skyway-topbar>div b{font-size:14px}
    .skyway-overlay{position:absolute;z-index:4;inset:0;display:flex;align-items:center;padding:24px;background:linear-gradient(90deg,rgba(12,43,47,.68),rgba(12,43,47,.04));transition:opacity .24s ease,visibility .24s ease}
    .skyway-overlay.hidden{opacity:0;visibility:hidden;pointer-events:none}.skyway-title{max-width:410px;color:#fff5dc;text-shadow:2px 3px rgba(18,41,46,.6)}
    .skyway-title>small{font-size:9px;font-weight:bold;letter-spacing:2px;color:#ffdf91}.skyway-title h2{margin:12px 0;font-size:clamp(44px,8vw,78px);line-height:.8}.skyway-title h2 em{color:#ffd065;font-style:normal}.skyway-title p{max-width:350px;font:14px/1.5 Arial,sans-serif;color:#e5ead9}
    .hero-picker{display:grid;gap:5px;margin-top:16px;color:#ffdf91;font-size:9px;font-weight:bold;letter-spacing:1px;text-shadow:none}
    .hero-picker select{width:min(285px,72vw);padding:9px;border:2px solid #253b3f;border-radius:0;background:#fff2d4;color:#253b3f;font:700 12px 'Courier New',monospace}
    #skyStart{display:flex;justify-content:space-between;align-items:center;gap:28px;margin-top:14px;padding:11px 15px;border:2px solid #253b3f;background:#ffd065;color:#253b3f;font:900 11px 'Courier New',monospace;box-shadow:3px 3px #253b3f;cursor:pointer}
    #skyStart span{font-size:17px}.sky-controls-hint{display:block;margin-top:15px;color:#fff2d4;font-size:8px;letter-spacing:.7px}
    .skyway-touch{position:absolute;z-index:3;right:14px;bottom:42px;display:flex;gap:6px}.skyway-touch button{min-width:42px;height:40px;border:1px solid rgba(255,246,219,.72);background:rgba(22,51,56,.72);color:#fff5dc;font:700 9px 'Courier New',monospace;touch-action:none}
    .skyway-foot{position:absolute;z-index:2;right:14px;bottom:12px;left:14px;display:flex;justify-content:space-between;color:#fff3d6;font-size:8px;font-weight:bold;letter-spacing:1px;text-shadow:1px 1px #18363e;pointer-events:none}
    .skyway-toast{position:absolute;z-index:3;top:82px;left:50%;transform:translateX(-50%);color:#ffedb4;font-size:11px;font-weight:bold;text-shadow:1px 2px #17383f;opacity:0;transition:opacity .15s}.skyway-toast.show{opacity:1}
    @media(max-width:560px){.skyway-shell{height:520px;min-height:460px}.skyway-topbar{top:8px;left:7px;right:7px;gap:4px}.skyway-topbar>strong{font-size:9px}.skyway-topbar>div{min-width:49px;padding:4px 3px}.skyway-topbar small{font-size:6px}.skyway-topbar>div b{font-size:11px}.skyway-overlay{padding:16px}.skyway-title{max-width:100%}.skyway-title h2{font-size:48px}.skyway-title p{max-width:290px;font-size:12px}.skyway-touch{right:50%;transform:translateX(50%);bottom:40px}.skyway-touch button{height:38px}.skyway-foot{font-size:7px}}
    @media(prefers-reduced-motion:reduce){.skyway-overlay,.skyway-toast{transition:none}}
</style>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js';
(() => {
    const shell = document.getElementById('skywayShell');
    const canvas = document.getElementById('skywayCanvas');
    const overlay = document.getElementById('skyOverlay');
    const title = document.getElementById('skyTitle');
    const copy = document.getElementById('skyCopy');
    const startButton = document.getElementById('skyStart');
    const heroSelect = document.getElementById('heroSelect');
    const toast = document.getElementById('skyToast');
    const stateLabel = document.getElementById('skyState');
    const distanceLabel = document.getElementById('skyDistance');
    const levelLabel = document.getElementById('skyLevel');
    const gemsLabel = document.getElementById('skyGems');
    const bestLabel = document.getElementById('skyBest');
    const laneX = [-2.15, 0, 2.15];
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#66c7e2');
    scene.fog = new THREE.Fog('#78cbdc', 34, 118);
    const camera = new THREE.PerspectiveCamera(54, 1, .1, 130);
    camera.position.set(0, 6.2, 11.8);
    camera.lookAt(0, -1.8, -8);
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.35));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.02;
    scene.add(new THREE.HemisphereLight('#e3fff0', '#46506d', 1.7));
    const sun = new THREE.DirectionalLight('#fff0c1', 2.2); sun.position.set(-5, 11, 7); scene.add(sun);
    const materials = {
        deck: new THREE.MeshStandardMaterial({ color: '#d09b52', roughness: .92 }),
        side: new THREE.MeshStandardMaterial({ color: '#568365', roughness: 1 }),
        stripe: new THREE.MeshStandardMaterial({ color: '#f7db8c', roughness: .8 }),
        hazard: new THREE.MeshStandardMaterial({ color: '#dc6449', roughness: .72 }),
        dark: new THREE.MeshStandardMaterial({ color: '#33464f', roughness: .8 }),
        gold: new THREE.MeshStandardMaterial({ color: '#ffd05b', metalness: .34, roughness: .34, emissive: '#784b12', emissiveIntensity: .4 }),
        teal: new THREE.MeshStandardMaterial({ color: '#47a9a0', roughness: .6 }),
        leaf: new THREE.MeshStandardMaterial({ color: '#36755c', roughness: .9 }),
        cloud: new THREE.MeshStandardMaterial({ color: '#f5efdd', roughness: 1 })
    };
    const shared = {
        floor: new THREE.BoxGeometry(7.8, .48, 12),
        rail: new THREE.BoxGeometry(.24, .25, 12),
        stripe: new THREE.BoxGeometry(.11, .035, 11.6),
        hazard: new THREE.BoxGeometry(.9, 1.25, .8),
        coin: new THREE.TorusGeometry(.34, .12, 8, 14),
        cloud: new THREE.SphereGeometry(1, 8, 6),
        trunk: new THREE.CylinderGeometry(.09, .13, 1.3, 6),
        canopy: new THREE.ConeGeometry(.75, 1.35, 6)
    };
    const floorBase = new THREE.Mesh(new THREE.BoxGeometry(180, .4, 150), materials.side);
    floorBase.position.set(0, -3.9, -46); scene.add(floorBase);
    const mountainMats = [
        new THREE.MeshStandardMaterial({ color: '#e6a77c', roughness: 1 }),
        new THREE.MeshStandardMaterial({ color: '#c98268', roughness: 1 }),
        new THREE.MeshStandardMaterial({ color: '#a9675b', roughness: 1 })
    ];
    const mountainGeo = new THREE.ConeGeometry(8, 15, 7, 2);
    for (let index = 0; index < 8; index++) {
        const mountain = new THREE.Mesh(mountainGeo, mountainMats[index % mountainMats.length]);
        mountain.position.set((index % 2 ? 1 : -1) * (10 + Math.floor(index / 2) * 4.5), 1.6 - (index % 3) * .8, -37 - Math.floor(index / 2) * 19);
        mountain.scale.set(1.05 + (index % 3) * .2, 1 + (index % 2) * .3, .72);
        scene.add(mountain);
    }
    const roadSegments = [];
    const totalSegments = 12, segmentLength = 12;
    function addMesh(group, geometry, material, position) {
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(...position); group.add(mesh); return mesh;
    }
    function randomizeSegment(segment, difficulty, safe = false) {
        segment.hole = !safe && Math.random() < Math.min(.08 + difficulty * .012, .26);
        segment.floor.visible = !segment.hole;
        for (const rail of segment.rails) rail.visible = !segment.hole;
        const hazardRoll = Math.random();
        segment.hazard.visible = !safe && !segment.hole && hazardRoll < Math.min(.36 + difficulty * .045, .72);
        segment.hazardLane = Math.floor(Math.random() * 3);
        segment.hazard.position.x = laneX[segment.hazardLane];
        const coinLane = Math.floor(Math.random() * 3);
        segment.coins.forEach((coin, index) => {
            coin.visible = !segment.hole && coinLane === index && (segment.hazardLane !== index || !segment.hazard.visible);
            coin.position.x = laneX[index];
        });
    }
    for (let index = 0; index < totalSegments; index++) {
        const group = new THREE.Group(); group.position.z = -index * segmentLength;
        const floor = addMesh(group, shared.floor, materials.deck, [0, -3.45, 0]);
        const rails = [-1, 1].map(side => addMesh(group, shared.rail, materials.teal, [side * 3.85, -3.05, 0]));
        for (const lane of [-1, 1]) addMesh(group, shared.stripe, materials.stripe, [lane * 1.28, -3.18, 0]);
        const hazard = addMesh(group, shared.hazard, index % 2 ? materials.hazard : materials.dark, [0, -2.55, -3.4]);
        hazard.userData.baseY = -2.55;
        const coins = laneX.map((lane, laneIndex) => {
            const coin = addMesh(group, shared.coin, materials.gold, [lane, -1.9, laneIndex - 1]);
            coin.rotation.y = Math.PI / 2;
            return coin;
        });
        const segment = { group, floor, rails, hazard, hazardLane: 1, hole: false, coins, gapHit: false, hazardHit: false };
        randomizeSegment(segment, 0, index < 2);
        scene.add(group); roadSegments.push(segment);
    }
    const props = [];
    for (let index = 0; index < 8; index++) {
        const group = new THREE.Group();
        group.position.set(index % 2 ? 5.9 : -5.9, -3.2, -8 - index * 12);
        addMesh(group, shared.trunk, materials.dark, [0, -.1, 0]);
        const canopy = addMesh(group, shared.canopy, materials.leaf, [0, .85, 0]);
        canopy.rotation.z = (index % 2 ? 1 : -1) * .12;
        scene.add(group); props.push(group);
    }
    for (let index = 0; index < 7; index++) {
        const cloudGroup = new THREE.Group(); cloudGroup.position.set(-15 + index * 5, 5 + (index % 3) * 2, -24 - index * 12);
        for (let puff = 0; puff < 3; puff++) {
            const cloud = addMesh(cloudGroup, shared.cloud, materials.cloud, [puff * .8, puff % 2 * .3, 0]);
            cloud.scale.set(1.2, .45, .55);
        }
        scene.add(cloudGroup);
    }
    function createHero(kind) {
        const hero = new THREE.Group();
        let jacket = '#df664c', pants = '#334557', hair = '#4a3528', skin = '#d99b70', tie = '#edbf58';
        if (kind === 'showman') { jacket = '#202b3a'; pants = '#172234'; hair = '#e5b947'; skin = '#efb888'; tie = '#d8463f'; }
        if (kind === 'starlight') { jacket = '#487b99'; pants = '#29384c'; hair = '#332c44'; skin = '#e3b296'; tie = '#72d8c1'; }
        const jacketMat = new THREE.MeshStandardMaterial({ color: jacket, roughness: .75 });
        const pantsMat = new THREE.MeshStandardMaterial({ color: pants, roughness: .9 });
        const hairMat = new THREE.MeshStandardMaterial({ color: hair, roughness: .88 });
        const skinMat = new THREE.MeshStandardMaterial({ color: skin, roughness: .8 });
        const tieMat = new THREE.MeshStandardMaterial({ color: tie, roughness: .65 });
        const torso = new THREE.Group(); hero.add(torso);
        const torsoMesh = new THREE.Mesh(new THREE.CapsuleGeometry(.34, .65, 3, 7), jacketMat); torsoMesh.position.y = .95; torso.add(torsoMesh);
        const head = new THREE.Mesh(new THREE.SphereGeometry(.29, 12, 10), skinMat); head.position.set(0, 1.72, .06); torso.add(head);
        const hairCap = new THREE.Mesh(new THREE.SphereGeometry(.305, 12, 7, 0, Math.PI * 2, 0, Math.PI * .5), hairMat);
        hairCap.position.set(0, 1.81, .04); hairCap.scale.set(1.05, .8, 1.03); torso.add(hairCap);
        if (kind === 'showman') {
            const sweep = new THREE.Mesh(new THREE.SphereGeometry(.23, 10, 6), hairMat); sweep.position.set(-.12, 1.99, .04); sweep.scale.set(1.45, .4, 1.1); sweep.rotation.z = -.15; torso.add(sweep);
        }
        const tieMesh = new THREE.Mesh(new THREE.ConeGeometry(.095, .48, 4), tieMat); tieMesh.position.set(0, .96, .34); tieMesh.rotation.x = -.08; torso.add(tieMesh);
        const armGeo = new THREE.CapsuleGeometry(.105, .43, 3, 6);
        for (const side of [-1, 1]) {
            const arm = new THREE.Mesh(armGeo, jacketMat); arm.position.set(side * .43, 1.03, .02); arm.rotation.z = side * -.18; torso.add(arm);
            const leg = new THREE.Mesh(new THREE.CapsuleGeometry(.13, .43, 3, 6), pantsMat); leg.position.set(side * .17, .32, 0); torso.add(leg);
        }
        hero.userData.torso = torso; hero.userData.legs = torso.children.filter(child => child.position.y === .32);
        return hero;
    }
    let hero = createHero('courier'); hero.position.set(0, -3.2, 3.5); scene.add(hero);
    heroSelect.addEventListener('change', () => {
        scene.remove(hero); hero = createHero(heroSelect.value); hero.position.set(laneX[lane], -3.2 + jumpHeight, 3.5); scene.add(hero);
    });
    let lane = 1, jumpHeight = 0, jumpVelocity = 0, distance = 0, gems = 0, level = 1, speed = 9, lives = 3;
    let running = false, paused = false, countdown = 0, lastFrame = 0, raf = 0, seconds = 0, toastTime = 0, hitCooldown = 0;
    let best = Number(localStorage.getItem('skywaySprintBest') || 0); bestLabel.textContent = String(best).padStart(4, '0') + ' m';
    const baseCoins = materials.gold.emissiveIntensity;
    function resize() {
        const width = Math.max(1, shell.clientWidth), height = Math.max(1, shell.clientHeight);
        renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix(); renderer.render(scene, camera);
        if (window.frameElement) window.frameElement.style.height = Math.ceil(shell.getBoundingClientRect().height + 20) + 'px';
    }
    new ResizeObserver(resize).observe(shell); resize();
    function announce(text) { toast.textContent = text; toast.classList.add('show'); toastTime = 1.05; }
    function updateLabels() {
        distanceLabel.textContent = String(Math.floor(distance)).padStart(4, '0') + ' m';
        level = 1 + Math.floor(distance / 180); speed = 9 + (level - 1) * .72;
        levelLabel.textContent = String(level).padStart(2, '0'); gemsLabel.textContent = String(gems);
        stateLabel.textContent = countdown > 0 ? String(Math.ceil(countdown)) : `RUN ${lives}♥`;
    }
    function restartSegment(segment) {
        const farthest = Math.min(...roadSegments.map(item => item.group.position.z));
        segment.group.position.z = farthest - segmentLength;
        segment.gapHit = false; segment.hazardHit = false; randomizeSegment(segment, level);
    }
    function loseLife(reason) {
        if (hitCooldown > 0 || countdown > 0) return;
        lives--; hitCooldown = 1.1; announce(reason);
        if (lives <= 0) {
            running = false; paused = false;
            if (distance > best) { best = Math.floor(distance); localStorage.setItem('skywaySprintBest', String(best)); bestLabel.textContent = String(best).padStart(4, '0') + ' m'; }
            title.innerHTML = 'RUN<br><em>ENDED</em>'; copy.textContent = `You travelled ${Math.floor(distance)} m and found ${gems} gems. The sky road is still out there.`;
            startButton.innerHTML = 'RUN AGAIN <span>↗</span>'; overlay.classList.remove('hidden'); stateLabel.textContent = 'GAME OVER';
        } else {
            lane = 1; hero.position.x = laneX[lane]; jumpHeight = .5; jumpVelocity = 4;
        }
    }
    function handleAction(action) {
        if (!running || countdown > 0) return;
        if (action === 'left') lane = Math.max(0, lane - 1);
        if (action === 'right') lane = Math.min(2, lane + 1);
        if (action === 'jump' && jumpHeight < .08) jumpVelocity = 9.5;
    }
    function startGame() {
        if (raf) cancelAnimationFrame(raf);
        lane = 1; jumpHeight = 0; jumpVelocity = 0; distance = 0; gems = 0; level = 1; speed = 9; lives = 3; seconds = 0; countdown = 3; hitCooldown = 0;
        for (let index = 0; index < roadSegments.length; index++) {
            roadSegments[index].group.position.z = -index * segmentLength;
            roadSegments[index].gapHit = false; roadSegments[index].hazardHit = false; randomizeSegment(roadSegments[index], 0, index < 2);
        }
        hero.position.set(laneX[lane], -3.2, 3.0); title.innerHTML = 'SKYWAY<br><em>SPRINT</em>';
        copy.textContent = 'Leap the gaps, dodge the clockwork hazards, and see how far the sky road goes.';
        startButton.innerHTML = 'START RUN <span>↗</span>'; overlay.classList.add('hidden'); running = true; paused = false; lastFrame = 0; updateLabels();
        raf = requestAnimationFrame(tick);
    }
    function tick(now) {
        raf = 0; if (!running || document.visibilityState !== 'visible') return;
        const dt = lastFrame ? Math.min((now - lastFrame) / 1000, .05) : 0; lastFrame = now; seconds += dt;
        if (countdown > 0) {
            countdown = Math.max(0, countdown - dt); stateLabel.textContent = countdown > 0 ? String(Math.ceil(countdown)) : 'GO!';
            hero.position.y = -3.2 + Math.sin(seconds * 8) * .045;
            renderer.render(scene, camera);
            if (countdown === 0) announce('GO!');
            raf = requestAnimationFrame(tick); return;
        }
        distance += speed * dt; hitCooldown = Math.max(0, hitCooldown - dt);
        jumpVelocity -= 22 * dt; jumpHeight = Math.max(0, jumpHeight + jumpVelocity * dt);
        if (jumpHeight === 0) jumpVelocity = 0;
        hero.position.y = -3.2 + jumpHeight;
        hero.position.x += (laneX[lane] - hero.position.x) * Math.min(12 * dt, 1);
        hero.userData.torso.rotation.z = (laneX[lane] - hero.position.x) * .11;
        hero.userData.legs.forEach((leg, index) => { leg.rotation.x = Math.sin(seconds * 13 + index * Math.PI) * .45; });
        for (const segment of roadSegments) {
            segment.group.position.z += speed * dt;
            if (segment.group.position.z > 15) restartSegment(segment);
            segment.coins.forEach(coin => { if (coin.visible) coin.rotation.y += dt * 3.2; });
            const relativeZ = segment.group.position.z - hero.position.z;
            if (segment.hole && !segment.gapHit && Math.abs(relativeZ) < 5.6) {
                segment.gapHit = true;
                if (jumpHeight < .8) loseLife('MISSED THE GAP!');
            }
            const hazardZ = segment.group.position.z + segment.hazard.position.z;
            if (segment.hazard.visible && !segment.hazardHit && Math.abs(hazardZ - hero.position.z) < .9) {
                segment.hazardHit = true;
                if (segment.hazardLane === lane && jumpHeight < 1.45) loseLife('WATCH YOUR STEP!');
            }
            for (const coin of segment.coins) {
                const coinZ = segment.group.position.z + coin.position.z;
                if (coin.visible && coin.position.x === laneX[lane] && Math.abs(coinZ - hero.position.z) < .8 && jumpHeight < 2.5) {
                    coin.visible = false; gems++; announce('+1 SKY GEM');
                }
            }
        }
        for (const prop of props) { prop.position.z += speed * dt; if (prop.position.z > 13) prop.position.z -= totalSegments * segmentLength * .66; }
        if (toastTime > 0) { toastTime -= dt; if (toastTime <= 0) toast.classList.remove('show'); }
        if (Math.floor(seconds * 6) !== Math.floor((seconds - dt) * 6)) updateLabels();
        camera.position.x += (hero.position.x * .13 - camera.position.x) * Math.min(dt * 2, 1);
        camera.lookAt(hero.position.x * .1, -1.8 + jumpHeight * .08, -8);
        materials.gold.emissiveIntensity = baseCoins + Math.sin(seconds * 4) * .12;
        renderer.render(scene, camera);
        if (running) raf = requestAnimationFrame(tick);
    }
    startButton.addEventListener('click', () => {
        if (paused) {
            paused = false; running = true; overlay.classList.add('hidden'); stateLabel.textContent = 'RESUMED'; lastFrame = 0; raf = requestAnimationFrame(tick);
        } else startGame();
    });
    window.addEventListener('keydown', event => {
        const actions = { ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', ArrowUp: 'jump', Space: 'jump', KeyW: 'jump' };
        if (actions[event.code]) { event.preventDefault(); handleAction(actions[event.code]); }
        if (event.code === 'Escape' && running && countdown <= 0) { running = false; paused = true; if (raf) cancelAnimationFrame(raf); raf = 0; title.innerHTML = 'PAUSED'; copy.textContent = 'Take a breath. The sky road will wait.'; startButton.innerHTML = 'RESUME RUN <span>↗</span>'; overlay.classList.remove('hidden'); }
    });
    document.querySelectorAll('[data-sky]').forEach(button => button.addEventListener('pointerdown', event => { event.preventDefault(); handleAction(button.dataset.sky); }));
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState !== 'visible') { if (raf) cancelAnimationFrame(raf); raf = 0; lastFrame = 0; }
        else if (running && !raf) raf = requestAnimationFrame(tick);
    });
    drawIdle();
    function drawIdle() { renderer.render(scene, camera); }
})();
</script>
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
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.35));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

scene.add(new THREE.HemisphereLight('#d8ebc8', '#45382d', 2.2));
const sun = new THREE.DirectionalLight('#ffe1a0', 3.2);
sun.position.set(-7, 12, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(768, 768);
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
    for (const item of list) removeRunObject(item.group);
    list.length = 0;
}

function removeRunObject(group) {
    if (group.userData.disposed) return;
    scene.remove(group);
    group.traverse(child => {
        if (child.geometry) child.geometry.dispose();
    });
    group.userData.disposed = true;
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
    startAnimation();
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
    stopAnimation();
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
        startAnimation();
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
        stopAnimation();
    } else {
        startOverlay.classList.add('hidden');
        startAnimation();
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
            if (obstacle.group.position.z > 12) { removeRunObject(obstacle.group); return false; }
        return true;
    });
    for (const relic of relics) {
        relic.group.position.z += speed * delta;
        relic.group.rotation.y += delta * 2.5;
        relic.group.position.y = 1.2 + Math.sin(elapsed * 5 + relic.group.position.z) * .12;
        if (!relic.collected && relic.group.position.z > 1.15 && relic.group.position.z < 2.6 && relic.lane === currentLane) {
            relic.collected = true; relicCount++; relicValue.textContent = String(relicCount); removeRunObject(relic.group); showRelicToast();
        }
    }
    relics = relics.filter(relic => {
        if (relic.collected || relic.group.position.z > 12) { removeRunObject(relic.group); return false; }
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
    renderer.render(scene, camera);
}
let animationFrame = 0;
let lastFrameTime = 0;
let pageVisible = document.visibilityState === 'visible';
let shellVisible = true;

function stopAnimation() {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    animationFrame = 0;
    lastFrameTime = 0;
}

function animate(timestamp) {
    animationFrame = 0;
    if (!active || paused || !pageVisible || !shellVisible) return;
    const delta = lastFrameTime ? Math.min((timestamp - lastFrameTime) / 1000, .05) : 0;
    lastFrameTime = timestamp;
    updateGame(delta);
    renderer.render(scene, camera);
    if (active && !paused && pageVisible && shellVisible) {
        animationFrame = requestAnimationFrame(animate);
    }
}

function startAnimation() {
    if (!animationFrame && active && !paused && pageVisible && shellVisible) {
        lastFrameTime = 0;
        animationFrame = requestAnimationFrame(animate);
    }
}

document.addEventListener('visibilitychange', () => {
    pageVisible = document.visibilityState === 'visible';
    if (pageVisible) startAnimation();
    else stopAnimation();
});
new IntersectionObserver(entries => {
    shellVisible = entries[0].isIntersecting;
    if (shellVisible) startAnimation();
    else stopAnimation();
}).observe(shell);
new ResizeObserver(resize).observe(shell);
resize();
renderer.render(scene, camera);
</script>
"""

RACER_HTML = """
<div class="racer-shell">
    <div class="racer-topline"><span>COAST RUN · STAGE 01</span><b>POCKET GRAND PRIX</b><span>BEST <b id="racerBest">000000</b></span></div>
    <div class="racer-frame">
        <canvas id="racerCanvas" width="768" height="576" aria-label="Retro highway racing game" tabindex="0"></canvas>
        <div class="racer-scanlines"></div>
        <div class="racer-speedbar"><i id="racerSpeedBar"></i></div>
        <div class="racer-hud"><strong id="racerSpeed">000</strong><small>KM/H</small><span id="racerClock">00:00</span></div>
        <div class="racer-fuel"><b>F</b><div><i id="racerFuelBar"></i></div><b>E</b></div>
        <div class="racer-gear"><span>LIVES</span><b id="racerLives">N×3</b><span>AUTO</span><b>5</b><span>GEAR</span><b id="racerGear">1</b></div>
        <div class="racer-distance"><b id="racerPosition">1ST</b><span><strong id="racerDistance">00.0</strong> KM</span></div>
        <div class="racer-countdown" id="racerCountdown" aria-live="assertive" hidden>3</div>
        <div class="racer-message" id="racerMessage"><small>COAST TO COAST</small><strong>POCKET<br>GRAND PRIX</strong><span>ONE MORE RACE BEFORE THE SUN SETS</span><button id="racerStart">START ENGINE <i>▶</i></button></div>
        <div class="racer-mobile-controls"><button data-steer="-1" aria-label="Steer left">◀</button><button data-pedal="brake">BRK</button><button data-pedal="gas">GAS</button><button data-steer="1" aria-label="Steer right">▶</button></div>
    </div>
    <div class="racer-bottomline"><span>← → / A D STEER</span><span>↑ / W GAS · ↓ / S BRAKE</span><span>THE COAST IS YOURS</span></div>
</div>
<style>
    .racer-shell{max-width:900px;margin:0 auto;padding:12px 14px 14px;background:#f5ecd7;border:1px solid #b9a98a;color:#293540;font-family:'Courier New',monospace;box-shadow:0 12px 34px rgba(38,46,48,.12)}
    .racer-topline,.racer-bottomline{display:flex;justify-content:space-between;gap:10px;align-items:center;font-size:10px;font-weight:bold;letter-spacing:1.3px}
    .racer-topline{padding:0 2px 9px;color:#728076}.racer-topline>b{color:#d25136;font-size:13px}.racer-topline span:last-child b{color:#d25136}
    .racer-frame{position:relative;width:100%;overflow:hidden;background:#86c8d0;border:4px solid #263641;aspect-ratio:4/3}
    #racerCanvas{display:block;width:100%;height:100%;image-rendering:pixelated;touch-action:none}
    .racer-scanlines{position:absolute;inset:0;pointer-events:none;opacity:.16;background:repeating-linear-gradient(0deg,transparent 0 3px,rgba(13,26,34,.45) 4px 5px);mix-blend-mode:multiply}
    .racer-speedbar{position:absolute;z-index:2;top:11px;right:12px;width:156px;height:13px;padding:2px;border:2px solid #202b36;background:#101922;pointer-events:none}
    .racer-speedbar i{display:block;width:0;height:100%;background:repeating-linear-gradient(90deg,#2fbf50 0 7px,#12391f 7px 9px);transition:width .15s linear}
    .racer-hud{position:absolute;z-index:2;top:27px;right:12px;display:grid;grid-template-columns:auto auto;align-items:center;column-gap:5px;min-width:126px;padding:6px 9px 5px;border:3px solid #202b36;background:#101922;color:#f4e9ca;box-shadow:3px 3px rgba(16,25,34,.42);pointer-events:none}
    .racer-hud strong{grid-row:span 2;color:#f0443c;font-size:29px;line-height:1;text-align:right;text-shadow:0 0 7px rgba(240,68,60,.55)}
    .racer-hud small{align-self:end;color:#f0443c;font-size:8px;font-weight:bold}.racer-hud span{color:#e8e4d7;font-size:10px;font-weight:bold}
    .racer-gear,.racer-distance{position:absolute;z-index:2;bottom:12px;display:grid;grid-template-columns:auto auto;align-items:center;gap:2px 8px;padding:5px 8px;background:rgba(17,28,35,.84);color:#fff2cf;font-size:10px;font-weight:bold;pointer-events:none;text-shadow:1px 1px #111}
    .racer-gear{left:12px}.racer-gear span{color:#f1ce77}.racer-gear b{color:#fff;font-size:13px}.racer-distance{right:12px;display:flex;align-items:baseline;gap:9px}.racer-distance b{font-size:17px;color:#fff2cf}.racer-distance span{color:#f1ce77}.racer-distance strong{color:#fff2cf;font-size:16px}
    .racer-fuel{position:absolute;z-index:2;top:34%;right:12px;display:flex;flex-direction:column;align-items:center;gap:3px;color:#fff2cf;font-size:9px;font-weight:bold;text-shadow:1px 1px #111;pointer-events:none}
    .racer-fuel>div{width:15px;height:112px;padding:2px;border:2px solid #202b36;background:#101922;display:flex;align-items:flex-end}
    .racer-fuel i{display:block;width:100%;height:100%;background:repeating-linear-gradient(0deg,#43d65b 0 5px,#17602b 5px 7px)}
    .racer-countdown{position:absolute;z-index:4;top:50%;left:50%;transform:translate(-50%,-50%);color:#ffe28a;font:900 clamp(72px,16vw,150px)/1 'Courier New',monospace;text-shadow:5px 5px #c63e32,-2px -2px #172831;pointer-events:none}
    .racer-countdown.bump{font-size:clamp(38px,8vw,72px);color:#fff2cf}
    .racer-countdown[hidden]{display:none}
    .racer-message{position:absolute;inset:0;z-index:3;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:#fff4d1;text-shadow:3px 3px #293540;background:linear-gradient(180deg,rgba(26,52,62,.08),rgba(23,39,43,.28));transition:opacity .2s ease}
    .racer-message.hidden{opacity:0;visibility:hidden;pointer-events:none}
    .racer-message small{color:#ffdb70;font-weight:bold;font-size:11px;letter-spacing:4px}
    .racer-message strong{margin:8px 0 4px;font-size:clamp(36px,7vw,76px);line-height:.82}
    .racer-message span{font-size:10px;letter-spacing:1px}
    .racer-message button{margin-top:20px;padding:12px 18px;border:3px solid #293540;background:#ffdb70;color:#293540;font:900 12px 'Courier New',monospace;box-shadow:4px 4px #293540;cursor:pointer}
    .racer-message button i{margin-left:14px;font-style:normal}
    .racer-bottomline{padding:9px 2px 0;color:#728076;font-size:9px}
    .racer-mobile-controls{position:absolute;z-index:2;right:50%;bottom:10px;display:none;transform:translateX(50%);gap:5px}
    .racer-mobile-controls button{min-width:36px;height:34px;border:2px solid #fff2cb;background:rgba(35,51,58,.88);color:#fff2cb;font:700 9px 'Courier New',monospace;touch-action:none}
    @media(max-width:650px){.racer-shell{padding:9px}.racer-topline span:last-child,.racer-bottomline span:last-child{display:none}.racer-topline,.racer-bottomline{font-size:8px}.racer-mobile-controls{display:flex}.racer-speedbar{top:7px;right:7px;width:118px;height:11px}.racer-hud{top:21px;right:7px;min-width:100px;padding:4px 6px}.racer-hud strong{font-size:21px}.racer-hud span{font-size:9px}.racer-fuel{top:34%;right:7px}.racer-fuel>div{height:82px;width:13px}.racer-gear,.racer-distance{bottom:8px;padding:4px 5px;gap:2px 5px;font-size:8px}.racer-gear{left:7px}.racer-distance{right:7px;gap:5px}.racer-distance strong{font-size:13px}.racer-message strong{font-size:clamp(32px,9vw,58px)}}
</style>
<script>
(() => {
    const canvas = document.getElementById('racerCanvas');
    const ctx = canvas.getContext('2d', { alpha: false });
    const message = document.getElementById('racerMessage');
    const bestLabel = document.getElementById('racerBest');
    const speedLabel = document.getElementById('racerSpeed');
    const clockLabel = document.getElementById('racerClock');
    const gearLabel = document.getElementById('racerGear');
    const distanceLabel = document.getElementById('racerDistance');
    const positionLabel = document.getElementById('racerPosition');
    const livesLabel = document.getElementById('racerLives');
    const speedBar = document.getElementById('racerSpeedBar');
    const fuelBar = document.getElementById('racerFuelBar');
    const countdownLabel = document.getElementById('racerCountdown');
    const W = canvas.width, H = canvas.height, horizon = 195;
    const keys = new Set();
    const player = { x: 0, steer: 0 };
    let traffic = [], distance = 0, score = 0, speed = 0, raceSeconds = 0, fuel = 1, active = false, crashed = false, frame = 0, nextTrafficFrame = 40, countdown = 0, goSignal = 0, lives = 3, impactCooldown = 0, offroadClock = 0, bumpClock = 0, raf = 0, last = 0;
    let best = Number(localStorage.getItem('pocketGrandPrixBest') || 0);
    bestLabel.textContent = String(best).padStart(6, '0');
    const sky = ctx.createLinearGradient(0, 0, 0, horizon);
    sky.addColorStop(0, '#00bde9'); sky.addColorStop(1, '#f5bd79');
    const hills = document.createElement('canvas'); hills.width = W; hills.height = H;
    const hillCtx = hills.getContext('2d');
    hillCtx.fillStyle = '#d5aa7c'; hillCtx.beginPath(); hillCtx.moveTo(0, horizon);
    for (let x = 0; x <= W; x += 64) hillCtx.lineTo(x, 108 + Math.sin(x * .013) * 30 + Math.sin(x * .031) * 13);
    hillCtx.lineTo(W, horizon); hillCtx.closePath(); hillCtx.fill();
    hillCtx.fillStyle = '#b98259'; hillCtx.beginPath(); hillCtx.moveTo(0, horizon);
    for (let x = 0; x <= W; x += 56) hillCtx.lineTo(x, 156 + Math.sin(x * .018 + 1) * 24);
    hillCtx.lineTo(W, horizon); hillCtx.closePath(); hillCtx.fill();
    const backdrop = document.createElement('canvas'); backdrop.width = W; backdrop.height = H;
    const backdropCtx = backdrop.getContext('2d');
    backdropCtx.fillStyle = sky; backdropCtx.fillRect(0, 0, W, horizon);
    backdropCtx.drawImage(hills, 0, 0);
    backdropCtx.fillStyle = '#f4d27b'; backdropCtx.beginPath(); backdropCtx.arc(650, 75, 26, 0, Math.PI * 2); backdropCtx.fill();
    backdropCtx.fillStyle = '#8b9369'; backdropCtx.fillRect(0, horizon, W, H - horizon);
    function format(value) { return String(Math.floor(value)).padStart(6, '0').slice(-6); }
    function formatClock(seconds) {
        const minutes = Math.floor(seconds / 60);
        return String(minutes).padStart(2, '0') + ':' + String(Math.floor(seconds % 60)).padStart(2, '0');
    }
    function roadPoint(t, bend) {
        const y = horizon + t * (H - horizon);
        const curve = bend * t * t * 176;
        const half = 18 + t * 366;
        return { y, center: W / 2 + curve, half };
    }
    const spriteCache = new Map();
    const carPalettes = {
        '#b23cc2': { body: '#b23cc2', light: '#ee89e9', shade: '#69246f', glass: '#262a42', chrome: '#dad2e0' },
        '#e8e4ea': { body: '#e8e4ea', light: '#fff', shade: '#777789', glass: '#25283d', chrome: '#d6d4db' },
        '#d85b45': { body: '#d85b45', light: '#ffad76', shade: '#743838', glass: '#25283d', chrome: '#d7c7b3' },
        '#35465e': { body: '#35465e', light: '#788ea9', shade: '#182535', glass: '#202a3b', chrome: '#bac5cc' },
        '#e5a93e': { body: '#e5a93e', light: '#ffe183', shade: '#79502e', glass: '#25283d', chrome: '#e6d4b1' },
        '#428a78': { body: '#428a78', light: '#8ed0a6', shade: '#204f4c', glass: '#202a3b', chrome: '#c4d4c1' }
    };
    function makeCarSprite(color) {
        if (spriteCache.has(color)) return spriteCache.get(color);
        const sprite = document.createElement('canvas');
        sprite.width = 96; sprite.height = 56;
        const car = sprite.getContext('2d');
        car.imageSmoothingEnabled = false;
        const palette = carPalettes[color] || carPalettes['#e8e4ea'];
        function polygon(points, fill) {
            car.fillStyle = fill; car.beginPath(); car.moveTo(points[0][0], points[0][1]);
            for (let index = 1; index < points.length; index++) car.lineTo(points[index][0], points[index][1]);
            car.closePath(); car.fill();
        }
        car.fillStyle = 'rgba(10,17,25,.62)'; car.fillRect(8, 46, 80, 6);
        car.fillStyle = '#141923'; car.fillRect(9, 30, 13, 19); car.fillRect(74, 30, 13, 19);
        polygon([[8, 41], [10, 25], [18, 17], [24, 10], [34, 7], [62, 7], [72, 10], [79, 17], [87, 25], [89, 41], [81, 47], [15, 47]], '#171923');
        polygon([[12, 39], [14, 26], [21, 19], [27, 12], [36, 10], [60, 10], [69, 12], [76, 19], [83, 26], [85, 39], [78, 44], [18, 44]], palette.body);
        polygon([[25, 18], [31, 12], [38, 10], [58, 10], [65, 12], [72, 18], [75, 25], [21, 25]], palette.light);
        polygon([[29, 18], [34, 14], [40, 13], [56, 13], [62, 14], [68, 18], [71, 23], [25, 23]], palette.glass);
        car.fillStyle = '#111923'; car.fillRect(18, 25, 60, 5);
        car.fillStyle = palette.shade; car.fillRect(15, 28, 66, 7); car.fillRect(11, 26, 8, 12); car.fillRect(77, 26, 8, 12);
        car.fillStyle = '#f2473c'; car.fillRect(16, 29, 19, 6); car.fillRect(61, 29, 19, 6);
        car.fillStyle = '#ffb15d'; car.fillRect(18, 30, 13, 2); car.fillRect(65, 30, 13, 2);
        car.fillStyle = '#212431'; car.fillRect(37, 29, 22, 12);
        car.fillStyle = palette.chrome; car.fillRect(40, 31, 16, 7);
        car.fillStyle = '#727582'; car.fillRect(42, 33, 12, 2);
        car.fillStyle = palette.light; car.fillRect(13, 40, 70, 3);
        car.fillStyle = '#242630'; car.fillRect(7, 22, 5, 15); car.fillRect(84, 22, 5, 15);
        car.fillStyle = palette.chrome; car.fillRect(17, 45, 16, 3); car.fillRect(63, 45, 16, 3);
        car.fillStyle = '#242630'; car.fillRect(21, 45, 8, 2); car.fillRect(67, 45, 8, 2);
        car.fillStyle = palette.light; car.fillRect(9, 20, 8, 3); car.fillRect(79, 20, 8, 3);
        spriteCache.set(color, sprite);
        return sprite;
    }
    function drawCar(x, y, scale, color, lean = 0) {
        const sprite = makeCarSprite(color);
        const width = Math.max(8, Math.round(sprite.width * scale));
        const height = Math.max(6, Math.round(sprite.height * scale));
        ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(Math.round(x), Math.round(y)); ctx.rotate(lean);
        ctx.drawImage(sprite, Math.round(-width / 2), Math.round(-height / 2), width, height);
        ctx.restore();
    }
    function drawRoadside(t, side, bend, index) {
        const point = roadPoint(t, bend);
        const size = .12 + t * 1.12;
        const x = point.center + side * point.half * 1.2;
        const y = point.y;
        if (index % 4 === 0) {
            ctx.fillStyle = '#30333a'; ctx.fillRect(x - 2 * size, y - 31 * size, 4 * size, 33 * size);
            ctx.fillStyle = '#f4e6cf'; ctx.fillRect(x - 19 * size, y - 49 * size, 38 * size, 21 * size);
            ctx.fillStyle = '#ba3832'; ctx.fillRect(x - 16 * size, y - 46 * size, 32 * size, 15 * size);
            ctx.fillStyle = '#fff1d8'; ctx.font = `bold ${Math.max(5, 9 * size)}px monospace`; ctx.textAlign = 'center';
            ctx.fillText(side < 0 ? '>>>' : '<<<', x, y - 35 * size); ctx.textAlign = 'left';
            return;
        }
        if (index % 4 === 1 || index % 4 === 3) {
            ctx.fillStyle = '#275344'; ctx.fillRect(x - 5 * size, y - 41 * size, 10 * size, 40 * size);
            ctx.fillRect(x - 14 * size, y - 31 * size, 8 * size, 8 * size); ctx.fillRect(x - 14 * size, y - 36 * size, 5 * size, 12 * size);
            ctx.fillRect(x + 6 * size, y - 25 * size, 9 * size, 7 * size); ctx.fillRect(x + 10 * size, y - 31 * size, 5 * size, 13 * size);
            ctx.fillStyle = '#3b8a59'; ctx.fillRect(x - 3 * size, y - 39 * size, 6 * size, 35 * size);
            ctx.fillRect(x - 11 * size, y - 29 * size, 7 * size, 5 * size); ctx.fillRect(x + 7 * size, y - 23 * size, 7 * size, 4 * size);
            return;
        }
        ctx.fillStyle = '#47543b'; ctx.fillRect(x - 11 * size, y - 10 * size, 22 * size, 9 * size);
        ctx.fillStyle = '#70804c'; ctx.fillRect(x - 8 * size, y - 15 * size, 14 * size, 9 * size);
        ctx.fillStyle = '#9b855b'; ctx.fillRect(x - 2 * size, y - 7 * size, 4 * size, 6 * size);
    }
    function drawStartLine(bend) {
        const point = roadPoint(.76, bend);
        const pieces = 18, pieceWidth = point.half * 2 / pieces;
        const lineHeight = 4 + 8 * .76;
        for (let index = 0; index < pieces; index++) {
            ctx.fillStyle = index % 2 ? '#202a32' : '#f7f0dc';
            ctx.fillRect(point.center - point.half + index * pieceWidth, point.y, pieceWidth + 1, lineHeight);
        }
    }
    function draw() {
        ctx.drawImage(backdrop, 0, 0);
        const bend = Math.sin(distance * .00055) * .86 + Math.sin(distance * .00018) * .3;
        const stripe = Math.floor(distance / 12) % 2;
        for (let segment = 0; segment < 32; segment++) {
            const near = segment / 32, far = (segment + 1) / 32;
            const a = roadPoint(near, bend), b = roadPoint(far, bend);
            ctx.fillStyle = (segment + stripe) % 2 ? '#f2dfbd' : '#cf5b4c';
            ctx.beginPath(); ctx.moveTo(a.center - a.half * 1.11, a.y); ctx.lineTo(a.center - a.half, a.y); ctx.lineTo(b.center - b.half, b.y); ctx.lineTo(b.center - b.half * 1.11, b.y); ctx.fill();
            ctx.beginPath(); ctx.moveTo(a.center + a.half, a.y); ctx.lineTo(a.center + a.half * 1.11, a.y); ctx.lineTo(b.center + b.half * 1.11, b.y); ctx.lineTo(b.center + b.half, b.y); ctx.fill();
            ctx.fillStyle = (segment + stripe) % 2 ? '#555b5a' : '#606565';
            ctx.beginPath(); ctx.moveTo(a.center - a.half, a.y); ctx.lineTo(a.center + a.half, a.y); ctx.lineTo(b.center + b.half, b.y); ctx.lineTo(b.center - b.half, b.y); ctx.fill();
            if ((segment + stripe) % 3 === 0) {
                ctx.fillStyle = '#fff0bf';
                for (const lane of [-1 / 3, 1 / 3]) {
                    const aw = Math.max(1, a.half * .012), bw = Math.max(1, b.half * .012);
                    ctx.beginPath(); ctx.moveTo(a.center + a.half * lane - aw, a.y); ctx.lineTo(a.center + a.half * lane + aw, a.y); ctx.lineTo(b.center + b.half * lane + bw, b.y); ctx.lineTo(b.center + b.half * lane - bw, b.y); ctx.fill();
                }
            }
        }
        if (countdown > 0 || goSignal > 0) drawStartLine(bend);
        const roadsideOffset = (distance * .00016) % 1;
        for (let index = 0; index < 9; index++) {
            const t = (index / 9 + roadsideOffset) % 1;
            if (t > .035) {
                drawRoadside(t, -1, bend, index);
                drawRoadside(t, 1, bend, index + 2);
            }
        }
        for (const car of traffic) {
            const t = car.depth;
            if (t <= 0 || t >= 1) continue;
            const point = roadPoint(t, bend);
            drawCar(point.center + car.lane * point.half * .72, point.y, .25 + t * .92, car.color);
        }
        const near = roadPoint(.94, bend);
        const playerY = canvas.clientWidth < 650 ? H - 122 : H - 48;
        drawCar(near.center + player.x * near.half * .72, playerY, 1.18, '#b23cc2', player.steer * -.035);
        drawRouteMap();
        if (!active && !crashed) {
            ctx.fillStyle = 'rgba(36,52,58,.22)'; ctx.fillRect(0, 0, W, H);
        }
    }
    function drawRouteMap() {
        const points = [[25, 70], [43, 70], [55, 56], [47, 41], [63, 29], [82, 39], [99, 24], [119, 25]];
        ctx.fillStyle = '#14222a'; ctx.fillRect(12, 12, 132, 82);
        ctx.strokeStyle = '#d4c59d'; ctx.lineWidth = 2; ctx.strokeRect(12.5, 12.5, 131, 81);
        ctx.strokeStyle = '#e7ddbf'; ctx.lineWidth = 6; ctx.lineCap = 'square'; ctx.lineJoin = 'round';
        ctx.beginPath(); ctx.moveTo(points[0][0], points[0][1]);
        for (let index = 1; index < points.length; index++) ctx.lineTo(points[index][0], points[index][1]);
        ctx.stroke();
        ctx.strokeStyle = '#59615c'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(points[0][0], points[0][1]);
        for (let index = 1; index < points.length; index++) ctx.lineTo(points[index][0], points[index][1]);
        ctx.stroke();
        const progress = (distance / 2400) % 1 * (points.length - 1);
        const segment = Math.min(Math.floor(progress), points.length - 2), fraction = progress - segment;
        const carX = points[segment][0] + (points[segment + 1][0] - points[segment][0]) * fraction;
        const carY = points[segment][1] + (points[segment + 1][1] - points[segment][1]) * fraction;
        ctx.fillStyle = '#f0443c'; ctx.fillRect(carX - 4, carY - 4, 8, 8);
        ctx.fillStyle = '#fff2cf'; ctx.font = 'bold 8px monospace'; ctx.fillText('COAST', 17, 23);
    }
    function updateHud() {
        speedLabel.textContent = String(Math.round(speed)).padStart(3, '0');
        clockLabel.textContent = formatClock(raceSeconds);
        gearLabel.textContent = String(Math.min(5, Math.max(1, Math.floor(speed / 55))));
        distanceLabel.textContent = (distance / 3000).toFixed(1).padStart(4, '0');
        const place = Math.min(8, 1 + traffic.filter(car => !car.grid && car.depth < .86).length);
        const suffix = place === 1 ? 'ST' : place === 2 ? 'ND' : place === 3 ? 'RD' : 'TH';
        positionLabel.textContent = place + suffix;
        livesLabel.textContent = 'N×' + lives;
        speedBar.style.width = Math.min(100, speed / 285 * 100) + '%';
        fuelBar.style.height = Math.max(0, fuel * 100) + '%';
        bestLabel.textContent = format(best);
    }
    function stop() { if (raf) cancelAnimationFrame(raf); raf = 0; last = 0; }
    function finishRace() {
        active = false; crashed = true; countdownLabel.hidden = true;
        if (score > best) { best = score; localStorage.setItem('pocketGrandPrixBest', String(best)); }
        message.querySelector('small').textContent = 'RACE OVER · SCORE ' + format(score);
        message.querySelector('strong').innerHTML = 'NICE<br>DRIVING';
        message.querySelector('span').textContent = 'THE OPEN ROAD WILL STILL BE HERE TOMORROW';
        message.querySelector('button').innerHTML = 'RACE AGAIN <i>▶</i>';
        message.classList.remove('hidden');
        updateHud();
    }
    function takeHit(car = null) {
        if (impactCooldown > 0 || countdown > 0 || goSignal > 0) return;
        lives = Math.max(0, lives - 1);
        impactCooldown = 1.35;
        fuel = Math.max(0, fuel - .06);
        speed = Math.max(75, speed * .68);
        bumpClock = .7;
        countdownLabel.textContent = 'BUMP!  ×' + lives;
        countdownLabel.classList.add('bump');
        countdownLabel.hidden = false;
        if (car) {
            car.hit = true;
            car.depth = Math.min(1.14, car.depth + .14);
            player.x += player.x >= car.lane * .72 ? .14 : -.14;
        } else {
            player.x *= .68;
        }
        if (lives === 0) finishRace();
        updateHud();
    }
    function tick(now) {
        raf = 0;
        if (!active || document.visibilityState !== 'visible') return;
        const dt = last ? Math.min((now - last) / 1000, .05) : 0; last = now;
        frame += dt * 60;
        if (countdown > 0) {
            countdown = Math.max(0, countdown - dt);
            if (countdown === 0) goSignal = .8;
            countdownLabel.textContent = countdown > 0 ? String(Math.ceil(countdown)) : 'GO!';
            countdownLabel.hidden = false;
            draw(); raf = requestAnimationFrame(tick); return;
        }
        if (goSignal > 0) {
            goSignal = Math.max(0, goSignal - dt);
            countdownLabel.textContent = 'GO!'; countdownLabel.hidden = false;
            if (goSignal === 0) {
                countdownLabel.hidden = true; countdownLabel.classList.remove('bump');
                for (const car of traffic) car.grid = false;
                speed = 105; nextTrafficFrame = frame + 35;
                updateHud();
            }
            draw(); raf = requestAnimationFrame(tick); return;
        }
        raceSeconds += dt;
        impactCooldown = Math.max(0, impactCooldown - dt);
        if (bumpClock > 0) {
            bumpClock = Math.max(0, bumpClock - dt);
            if (bumpClock === 0) { countdownLabel.hidden = true; countdownLabel.classList.remove('bump'); }
        }
        fuel = Math.max(0, fuel - dt * .0009);
        const accelerating = keys.has('ArrowUp') || keys.has('KeyW') || keys.has('gas');
        const braking = keys.has('ArrowDown') || keys.has('KeyS') || keys.has('brake');
        speed += (accelerating ? 58 : -17) * dt;
        if (braking) speed -= 82 * dt;
        speed = Math.max(fuel > 0 ? 90 : 65, Math.min(fuel > 0 ? 285 : 115, speed));
        const steering = (keys.has('ArrowLeft') || keys.has('KeyA') || keys.has('left') ? -1 : 0) + (keys.has('ArrowRight') || keys.has('KeyD') || keys.has('right') ? 1 : 0);
        player.steer += (steering - player.steer) * Math.min(9 * dt, 1);
        player.x += player.steer * dt * (1.55 + speed / 250);
        player.x -= Math.sin(distance * .00075) * dt * speed * .00075;
        if (Math.abs(player.x) > 1.02) {
            player.x = Math.sign(player.x) * 1.02;
            speed = Math.max(65, speed - 95 * dt);
            offroadClock += dt;
            if (offroadClock > .75 && impactCooldown <= 0) { offroadClock = 0; takeHit(); }
        } else offroadClock = 0;
        distance += speed * dt * 3.1; score = Math.floor(distance / 8);
        if (frame >= nextTrafficFrame) {
            if (traffic.length < 7) traffic.push({ depth: .04, lane: [-.68, 0, .68][Math.floor(Math.random() * 3)], color: ['#e8e4ea', '#d85b45', '#35465e', '#e5a93e', '#428a78'][Math.floor(Math.random() * 5)], grid: false, hit: false });
            nextTrafficFrame = frame + 42 + Math.random() * 28;
        }
        for (const car of traffic) if (!car.grid) car.depth += dt * (0.12 + speed / 1500);
        for (const car of traffic) {
            if (!car.hit && !car.grid && car.depth > .91 && car.depth < 1.03 && Math.abs(car.lane * .72 - player.x * .72) < .19) {
                takeHit(car); break;
            }
        }
        traffic = traffic.filter(car => car.depth < 1.15);
        score = Math.floor(distance / 8);
        if (Math.floor(frame) % 6 === 0) updateHud();
        if (lives === 0) finishRace();
        draw();
        if (active) raf = requestAnimationFrame(tick);
    }
    function start() {
        stop();
        traffic = [
            { depth: .83, lane: -.66, color: '#e8e4ea', grid: true, hit: false },
            { depth: .83, lane: .66, color: '#d85b45', grid: true, hit: false },
            { depth: .58, lane: 0, color: '#35465e', grid: true, hit: false },
            { depth: .4, lane: -.66, color: '#e5a93e', grid: true, hit: false },
            { depth: .34, lane: .66, color: '#428a78', grid: true, hit: false }
        ];
        distance = 0; score = 0; speed = 0; raceSeconds = 0; fuel = 1; frame = 0; nextTrafficFrame = 40;
        player.x = 0; player.steer = 0; crashed = false; active = true; lives = 3;
        countdown = 3; goSignal = 0; impactCooldown = 0; offroadClock = 0; bumpClock = 0;
        message.classList.add('hidden');
        countdownLabel.classList.remove('bump'); countdownLabel.textContent = '3'; countdownLabel.hidden = false;
        updateHud();
        draw();
        raf = requestAnimationFrame(tick);
    }
    document.getElementById('racerStart').addEventListener('click', start);
    window.addEventListener('keydown', event => {
        if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Space'].includes(event.code)) event.preventDefault();
        keys.add(event.code);
        if (event.code === 'Space' && !active) start();
    });
    window.addEventListener('keyup', event => keys.delete(event.code));
    window.addEventListener('blur', () => keys.clear());
    document.querySelectorAll('[data-steer]').forEach(button => {
        const key = button.dataset.steer === '-1' ? 'left' : 'right';
        button.addEventListener('pointerdown', event => { event.preventDefault(); keys.add(key); });
        for (const type of ['pointerup', 'pointercancel', 'pointerleave']) button.addEventListener(type, () => keys.delete(key));
    });
    document.querySelectorAll('[data-pedal]').forEach(button => {
        const key = button.dataset.pedal;
        button.addEventListener('pointerdown', event => { event.preventDefault(); keys.add(key); });
        for (const type of ['pointerup', 'pointercancel', 'pointerleave']) button.addEventListener(type, () => keys.delete(key));
    });
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState !== 'visible') { stop(); keys.clear(); }
        else if (active && !raf) raf = requestAnimationFrame(tick);
    });
    const racerShell = document.querySelector('.racer-shell');
    function resizeEmbed() {
        const frameElement = window.frameElement;
        if (!frameElement) return;
        const height = Math.ceil(racerShell.getBoundingClientRect().height + 20);
        frameElement.style.height = `${height}px`;
    }
    new ResizeObserver(resizeEmbed).observe(racerShell);
    requestAnimationFrame(resizeEmbed);
    draw();
})();
</script>
"""

# --- Database Functions ---

supabase_client = None
SUPABASE_AVAILABLE = False
SUPABASE_ERROR = None

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        required_columns = {
            "mood_logs": "id,user_id,timestamp,mood_score,mood_label,recommendation",
            "memes": "id,title,description,image_path,user_id,is_hidden",
            "jokes": "id,category,text,user_id,is_hidden",
            "content_reports": "id,target_type,target_id,reporter_id,reason,resolved",
            "game_scores": "id,user_id,game_name,score,created_at",
            "profiles": "user_id,display_name,avatar_color,bio",
            "activity_events": "id,user_id,activity_type,activity_date,points",
            "comments": "id,target_type,target_id,user_id,body",
            "reactions": "id,target_type,target_id,user_id,reaction",
            "chat_messages": (
                "id,user_id,display_name,body,created_at,is_hidden,"
                "attachment_path,attachment_name,attachment_type,attachment_size"
            ),
        }
        for table_name, columns in required_columns.items():
            supabase_client.table(table_name).select(columns).limit(1).execute()
        supabase_client.rpc(
            "get_game_leaderboard",
            {"p_game_name": "rock-paper-scissors", "p_since": None},
        ).execute()
        SUPABASE_AVAILABLE = True
    except Exception as error:
        supabase_client = None
        SUPABASE_ERROR = str(error).replace(SUPABASE_SERVICE_ROLE_KEY, "[redacted]")


def save_community_meme(meme):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        return False

    image_path = f"{uuid.uuid4().hex}.{meme['image_extension']}"
    try:
        supabase_client.storage.from_(SUPABASE_MEME_BUCKET).upload(
            image_path,
            meme["image"],
            file_options={"content-type": meme["image_type"], "upsert": "false"},
        )
        supabase_client.table("memes").insert(
            {
                "title": meme["title"],
                "description": meme["desc"],
                "image_path": image_path,
                "user_id": meme["user_id"],
            }
        ).execute()
        return True
    except Exception:
        try:
            supabase_client.storage.from_(SUPABASE_MEME_BUCKET).remove([image_path])
        except Exception:
            pass
        return False


def get_community_memes(include_hidden=False):
    if st.session_state.get("demo_mode"):
        return []
    if not SUPABASE_AVAILABLE:
        return None
    try:
        query = supabase_client.table("memes").select("*").order("created_at", desc=True)
        if not include_hidden:
            query = query.eq("is_hidden", False)
        response = query.execute()
        memes = []
        for record in response.data:
            image_url = supabase_client.storage.from_(SUPABASE_MEME_BUCKET).get_public_url(record["image_path"])
            memes.append(
                {
                    "_id": record["id"],
                    "title": record["title"],
                    "desc": record["description"],
                    "image": image_url,
                    "image_path": record["image_path"],
                    "user_id": record["user_id"],
                    "created_at": record["created_at"],
                    "is_hidden": record["is_hidden"],
                }
            )
        return memes
    except Exception:
        return None


def save_community_joke(joke):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        return False
    try:
        supabase_client.table("jokes").insert(
            {"category": joke["category"], "text": joke["text"], "user_id": joke["user_id"]}
        ).execute()
        return True
    except Exception:
        return False


def get_community_jokes(include_hidden=False):
    if st.session_state.get("demo_mode"):
        return []
    if not SUPABASE_AVAILABLE:
        return None
    try:
        query = supabase_client.table("jokes").select("*").order("created_at", desc=True)
        if not include_hidden:
            query = query.eq("is_hidden", False)
        response = query.execute()
        return [
            {
                "_id": record["id"],
                "category": record["category"],
                "text": record["text"],
                "user_id": record["user_id"],
                "created_at": record["created_at"],
                "is_hidden": record["is_hidden"],
            }
            for record in response.data
        ]
    except Exception:
        return None


def update_community_meme(post_id, title, description):
    if not SUPABASE_AVAILABLE:
        return False
    try:
        response = supabase_client.table("memes").update(
            {"title": title.strip(), "description": description.strip()}
        ).eq("id", post_id).select("id").execute()
        return bool(response.data)
    except Exception:
        return False


def delete_community_meme(post_id):
    if not SUPABASE_AVAILABLE:
        return False
    try:
        record = supabase_client.table("memes").select("image_path").eq("id", post_id).single().execute().data
        response = supabase_client.table("memes").delete().eq("id", post_id).select("id").execute()
        if not response.data:
            return False
        supabase_client.storage.from_(SUPABASE_MEME_BUCKET).remove([record["image_path"]])
        return True
    except Exception:
        return False


def update_community_joke(post_id, category, text):
    if not SUPABASE_AVAILABLE:
        return False
    try:
        response = supabase_client.table("jokes").update(
            {"category": category, "text": text.strip()}
        ).eq("id", post_id).select("id").execute()
        return bool(response.data)
    except Exception:
        return False


def delete_community_joke(post_id):
    if not SUPABASE_AVAILABLE:
        return False
    try:
        response = supabase_client.table("jokes").delete().eq("id", post_id).select("id").execute()
        return bool(response.data)
    except Exception:
        return False


def submit_content_report(target_type, target_id, reporter_id, reason):
    if not SUPABASE_AVAILABLE:
        return False
    try:
        supabase_client.table("content_reports").insert(
            {
                "target_type": target_type,
                "target_id": target_id,
                "reporter_id": reporter_id,
                "reason": reason,
            }
        ).execute()
        return True
    except Exception:
        return False


def get_open_content_reports():
    if not SUPABASE_AVAILABLE:
        return None
    try:
        response = supabase_client.table("content_reports").select(
            "id,target_type,target_id,reporter_id,reason,created_at"
        ).eq("resolved", False).order("created_at", desc=True).execute()
        return response.data
    except Exception:
        return None


def resolve_content_report(report_id, target_type=None, target_id=None, hide_content=False):
    if not SUPABASE_AVAILABLE:
        return False
    try:
        if hide_content:
            table_name = {"meme": "memes", "joke": "jokes"}.get(target_type)
            if table_name is None:
                return False
            hidden = supabase_client.table(table_name).update(
                {"is_hidden": True}
            ).eq("id", target_id).select("id").execute()
            if not hidden.data:
                return False
        response = supabase_client.table("content_reports").update(
            {"resolved": True}
        ).eq("id", report_id).select("id").execute()
        return bool(response.data)
    except Exception:
        return False


def set_content_visibility(target_type, target_id, is_hidden):
    if not SUPABASE_AVAILABLE:
        return False
    table_name = {"meme": "memes", "joke": "jokes"}.get(target_type)
    if table_name is None:
        return False
    try:
        response = supabase_client.table(table_name).update(
            {"is_hidden": is_hidden}
        ).eq("id", target_id).select("id").execute()
        return bool(response.data)
    except Exception:
        return False


def record_game_score(user_id, game_name, score):
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        st.session_state.demo_game_scores.append(
            {"user_id": user_id, "game_name": game_name, "score": score, "created_at": created_at}
        )
        return True
    try:
        supabase_client.table("game_scores").insert(
            {"user_id": user_id, "game_name": game_name, "score": score, "created_at": created_at}
        ).execute()
        return True
    except Exception:
        return False


def get_game_leaderboard(game_name, period="All-time"):
    cutoff = None
    if period == "Last 7 days":
        cutoff = (datetime.now().astimezone() - timedelta(days=7)).isoformat(timespec="seconds")
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        score_rows = [
            item for item in st.session_state.demo_game_scores
            if item["game_name"] == game_name
            and (cutoff is None or item.get("created_at", "") >= cutoff)
        ]
        if game_name == "rock-paper-scissors":
            leaderboard = build_rps_leaderboard(score_rows)
            return pd.DataFrame(leaderboard) if leaderboard else pd.DataFrame(
                columns=["user_id", "wins", "rounds"]
            )
        if score_rows:
            return (
                pd.DataFrame(score_rows)
                .groupby("user_id", as_index=False)["score"]
                .max()
                .sort_values(["score", "user_id"], ascending=[False, True])
                .head(10)
                .reset_index(drop=True)
            )
        return pd.DataFrame(columns=["user_id", "score"])
    try:
        response = supabase_client.rpc(
            "get_game_leaderboard",
            {"p_game_name": game_name, "p_since": cutoff},
        ).execute()
        if not response.data:
            if game_name == "rock-paper-scissors":
                return pd.DataFrame(columns=["user_id", "wins", "rounds"])
            return pd.DataFrame(columns=["user_id", "score"])
        score_label = "wins" if game_name == "rock-paper-scissors" else "score"
        leaderboard = pd.DataFrame(response.data).rename(columns={"metric": score_label})
        if game_name != "rock-paper-scissors":
            leaderboard = leaderboard.drop(columns=["rounds"])
        return leaderboard
    except Exception:
        return None


def save_profile(user_id, display_name, avatar_color, bio):
    profile = {
        "user_id": user_id,
        "display_name": display_name.strip()[:30],
        "avatar_color": avatar_color,
        "bio": bio.strip()[:160],
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        st.session_state.demo_profiles[user_id] = profile
        return True
    try:
        supabase_client.table("profiles").upsert(profile, on_conflict="user_id").execute()
        return True
    except Exception:
        return False


def get_profile(user_id):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        return st.session_state.demo_profiles.get(
            user_id,
            {"display_name": st.session_state.get("profile_display_name", "Guest"), "avatar_color": "#24473f", "bio": ""},
        )
    if not SUPABASE_AVAILABLE:
        return None
    try:
        response = supabase_client.table("profiles").select(
            "display_name,avatar_color,bio"
        ).eq("user_id", user_id).maybe_single().execute()
        return response.data or {
            "display_name": st.session_state.get("profile_display_name", "Guest"),
            "avatar_color": "#24473f",
            "bio": "",
        }
    except Exception:
        return None


def record_activity(user_id, activity_type, points=1):
    activity_date = date.today().isoformat()
    event = {
        "user_id": user_id,
        "activity_type": activity_type,
        "activity_date": activity_date,
        "points": points,
    }
    try:
        if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
            local_events = st.session_state.demo_activity_events
            if not any(
                item["user_id"] == user_id
                and item["activity_type"] == activity_type
                and item["activity_date"] == activity_date
                for item in local_events
            ):
                local_events.append(event)
        else:
            supabase_client.table("activity_events").upsert(
                event, on_conflict="user_id,activity_type,activity_date", ignore_duplicates=True
            ).execute()
        if activity_type != "daily_reward":
            daily_events = get_user_activity(user_id)
            if daily_events is not None and not any(
                item["activity_type"] == "daily_reward"
                and item["activity_date"] == activity_date
                for item in daily_events
            ):
                record_activity(user_id, "daily_reward", 10)
        return True
    except Exception:
        return False


def get_user_activity(user_id):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        return [
            item for item in st.session_state.demo_activity_events if item["user_id"] == user_id
        ]
    try:
        response = supabase_client.table("activity_events").select(
            "activity_type,activity_date,points"
        ).eq("user_id", user_id).order("activity_date", desc=True).limit(500).execute()
        return response.data
    except Exception:
        return None


def get_platform_analytics():
    demo = st.session_state.get("demo_mode")
    if not SUPABASE_AVAILABLE or demo:
        if demo:
            demo_moods = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 2, 3, 4, 1, 3, 4]
            mood_records = [
                {
                    "timestamp": (date.today() - timedelta(days=len(demo_moods) - index - 1)).isoformat(),
                    "mood_score": score,
                }
                for index, score in enumerate(demo_moods)
            ]
            activity_records = [
                {
                    "user_id": f"FUN-{player:02d}",
                    "activity_date": (date.today() - timedelta(days=day_offset)).isoformat(),
                }
                for day_offset in range(14)
                for player in range(8 + day_offset % 6)
            ]
            return {
                "moods": demo_moods,
                "mood_records": mood_records,
                "activity_records": activity_records,
                "game_scores": [
                    {"game_name": "rock-paper-scissors", "score": 1},
                    {"game_name": "rock-paper-scissors", "score": 0},
                    {"game_name": "clicker", "score": 72},
                    {"game_name": "flap-dash", "score": 12},
                    {"game_name": "temple-dash", "score": 340},
                    {"game_name": "grand-prix", "score": 840},
                    {"game_name": "skyway-sprint", "score": 510},
                ],
                "meme_count": 18,
                "joke_count": 32,
                "active_today": 8,
                "top_posts": [
                    {"Post": "Monday loading...", "Type": "Meme", "Reactions": 24},
                    {"Post": "The cache joke", "Type": "Joke", "Reactions": 18},
                    {"Post": "Two buttons: sleep vs. one more episode", "Type": "Meme", "Reactions": 15},
                ],
            }
        return None
    try:
        moods = supabase_client.table("mood_logs").select(
            "timestamp,mood_score"
        ).order("timestamp", desc=True).limit(1000).execute().data
        scores = supabase_client.table("game_scores").select(
            "user_id,game_name,score"
        ).order("created_at", desc=True).limit(1000).execute().data
        memes = supabase_client.table("memes").select(
            "id,title", count="exact"
        ).eq("is_hidden", False).limit(1000).execute()
        jokes = supabase_client.table("jokes").select(
            "id,text", count="exact"
        ).eq("is_hidden", False).limit(1000).execute()
        activity_records = supabase_client.table("activity_events").select(
            "user_id,activity_date"
        ).gte(
            "activity_date", (date.today() - timedelta(days=29)).isoformat()
        ).limit(5000).execute().data
        reactions = supabase_client.table("reactions").select(
            "target_type,target_id"
        ).limit(5000).execute().data
        reaction_counts = {}
        for reaction in reactions:
            post_key = (reaction["target_type"], reaction["target_id"])
            reaction_counts[post_key] = reaction_counts.get(post_key, 0) + 1
        post_titles = {
            **{("meme", row["id"]): row["title"] for row in memes.data},
            **{("joke", row["id"]): row["text"] for row in jokes.data},
        }
        top_posts = [
            {
                "Post": post_titles[key][:80],
                "Type": key[0].title(),
                "Reactions": count,
            }
            for key, count in sorted(
                reaction_counts.items(), key=lambda item: item[1], reverse=True
            )
            if key in post_titles
        ][:5]
        active_today = len({
            row["user_id"] for row in activity_records
            if row["activity_date"] == date.today().isoformat()
        })
        return {
            "moods": [int(row["mood_score"]) for row in moods],
            "mood_records": moods,
            "activity_records": activity_records,
            "game_scores": scores,
            "meme_count": memes.count or len(memes.data),
            "joke_count": jokes.count or len(jokes.data),
            "active_today": active_today,
            "top_posts": top_posts,
        }
    except Exception:
        return None


def summarize_pulse_records(records):
    summary = summarize_mood_pulse(records)
    if summary is None:
        return None
    return {
        **summary,
        "source": "live",
        "updated_at": datetime.now().astimezone().strftime("%H:%M %Z"),
    }


def get_anonymous_pulse():
    if st.session_state.get("demo_mode"):
        return {
            "source": "sample",
            "participants": 24,
            "checkins": 73,
            "mix": {"upbeat": 48, "steady": 18, "taking it slow": 7},
            "updated_at": datetime.now().astimezone().strftime("%H:%M %Z"),
        }

    week_ago = (datetime.now().astimezone() - timedelta(days=7)).isoformat(timespec="seconds")
    if SUPABASE_AVAILABLE:
        try:
            records = supabase_client.table("mood_logs").select(
                "user_id,timestamp,mood_score,mood_label"
            ).gte("timestamp", week_ago).order("timestamp", desc=True).limit(5000).execute().data
        except Exception:
            records = None
        if records is not None:
            return summarize_pulse_records(records) or {
                "source": "sample",
                "participants": 24,
                "checkins": 73,
                "mix": {"upbeat": 48, "steady": 18, "taking it slow": 7},
                "updated_at": datetime.now().astimezone().strftime("%H:%M %Z"),
            }

    local_records = [
        record
        for record in st.session_state.demo_mood_logs
        if record.get("timestamp", "") >= week_ago
    ]
    local_pulse = summarize_pulse_records(local_records)
    if local_pulse:
        local_pulse["source"] = "session"
        local_pulse["updated_at"] = datetime.now().astimezone().strftime("%H:%M %Z")
        return local_pulse
    return {
        "source": "sample",
        "participants": 24,
        "checkins": 73,
        "mix": {"upbeat": 48, "steady": 18, "taking it slow": 7},
        "updated_at": datetime.now().astimezone().strftime("%H:%M %Z"),
    }


@st.fragment(run_every="60s")
def render_anonymous_pulse():
    pulse = get_anonymous_pulse()
    st.markdown("#### 📡 Anonymous campus pulse")
    if pulse["source"] == "sample":
        st.caption("Illustrative sample only — these are not live campus or user statistics.")
    elif pulse["source"] == "session":
        st.caption("Anonymous aggregate from this app session · refreshes every minute.")
    else:
        st.caption(
            "Anonymous aggregate across this app's shared database · refreshes every minute. "
            "This is not a campus-wide census."
        )

    pulse_cols = st.columns(2)
    pulse_cols[0].metric("Check-ins · last 7 days", pulse["checkins"])
    pulse_cols[1].metric("Anonymous participants", pulse["participants"])
    total = sum(pulse["mix"].values())
    if total:
        vibe_summary = " · ".join(
            f"{html.escape(vibe.title())}: {count / total:.0%}"
            for vibe, count in pulse["mix"].items()
        )
        st.markdown(f"**Vibe mix:** {vibe_summary}", unsafe_allow_html=True)
    if pulse["source"] != "sample":
        st.caption(
            "To protect privacy, live totals appear only after at least 5 distinct pseudonyms "
            "check in; small mood groups are combined or omitted."
        )


def get_post_interactions(target_type, target_id, user_id):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        key = f"{target_type}:{target_id}"
        reactions = st.session_state.demo_reactions.get(key, {})
        comments = st.session_state.demo_comments.get(key, [])
        return {
            "counts": {name: sum(value == name for value in reactions.values()) for name in ("like", "laugh", "love")},
            "mine": reactions.get(user_id),
            "comments": comments,
        }
    try:
        reactions = supabase_client.table("reactions").select(
            "user_id,reaction"
        ).eq("target_type", target_type).eq("target_id", target_id).execute().data
        comments = supabase_client.table("comments").select(
            "user_id,body,created_at"
        ).eq("target_type", target_type).eq("target_id", target_id).order("created_at").limit(30).execute().data
        return {
            "counts": {
                name: sum(item["reaction"] == name for item in reactions)
                for name in ("like", "laugh", "love")
            },
            "mine": next((item["reaction"] for item in reactions if item["user_id"] == user_id), None),
            "comments": comments,
        }
    except Exception:
        return None


def set_post_reaction(target_type, target_id, user_id, reaction):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        key = f"{target_type}:{target_id}"
        reactions = st.session_state.demo_reactions.setdefault(key, {})
        if reactions.get(user_id) == reaction:
            del reactions[user_id]
        else:
            reactions[user_id] = reaction
        return True
    try:
        query = supabase_client.table("reactions").select("id,reaction").eq(
            "target_type", target_type
        ).eq("target_id", target_id).eq("user_id", user_id).maybe_single().execute()
        if query.data and query.data["reaction"] == reaction:
            supabase_client.table("reactions").delete().eq("id", query.data["id"]).execute()
        else:
            supabase_client.table("reactions").upsert(
                {
                    "target_type": target_type,
                    "target_id": target_id,
                    "user_id": user_id,
                    "reaction": reaction,
                },
                on_conflict="target_type,target_id,user_id",
            ).execute()
        return True
    except Exception:
        return False


def add_post_comment(target_type, target_id, user_id, body):
    clean_body = body.strip()[:300]
    if not clean_body:
        return False
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        key = f"{target_type}:{target_id}"
        comments = st.session_state.demo_comments.setdefault(key, [])
        comments.append({"user_id": user_id, "body": clean_body})
        return True
    try:
        supabase_client.table("comments").insert(
            {
                "target_type": target_type,
                "target_id": target_id,
                "user_id": user_id,
                "body": clean_body,
            }
        ).execute()
        return True
    except Exception:
        return False


def get_chat_messages(include_hidden=False):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        messages = st.session_state.chat_messages
        if not include_hidden:
            messages = [message for message in messages if not message.get("is_hidden", False)]
        return messages[-50:]
    try:
        query = supabase_client.table("chat_messages").select(
            "id,user_id,display_name,body,created_at,is_hidden,"
            "attachment_path,attachment_name,attachment_type,attachment_size"
        )
        if not include_hidden:
            query = query.eq("is_hidden", False)
        messages = query.order("created_at", desc=True).limit(50).execute().data[::-1]
        for message in messages:
            attachment_path = message.get("attachment_path")
            if attachment_path:
                signed_url = supabase_client.storage.from_(
                    SUPABASE_CHAT_BUCKET
                ).create_signed_url(attachment_path, 3600)
                message["attachment_url"] = signed_url.get("signedURL")
        return messages
    except Exception:
        return None


def send_chat_message(user_id, display_name, body, attachment=None):
    clean_body = body.strip()
    if len(clean_body) > 500 or (not clean_body and attachment is None):
        return False
    now = datetime.now().astimezone()
    last_sent = st.session_state.get("chat_last_sent_at")
    if isinstance(last_sent, datetime) and (now - last_sent).total_seconds() < 2:
        return False
    message = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "display_name": display_name.strip()[:30] or "Student",
        "body": clean_body,
        "created_at": now.isoformat(timespec="seconds"),
        "is_hidden": False,
    }
    attachment_path = None
    if attachment is not None:
        try:
            validated_type = validate_chat_attachment(
                attachment["name"], attachment["type"], attachment["data"]
            )
        except (KeyError, TypeError, ValueError):
            return False
        safe_name = os.path.basename(attachment["name"].replace("\\", "/"))[:120]
        attachment_path = f"{user_id}/{uuid.uuid4().hex}{os.path.splitext(safe_name)[1].lower()}"
        message.update(
            {
                "attachment_name": safe_name,
                "attachment_type": validated_type,
                "attachment_size": len(attachment["data"]),
            }
        )
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        if attachment is not None:
            message["attachment_data"] = attachment["data"]
        st.session_state.chat_messages.append(message)
    else:
        try:
            if attachment is not None:
                supabase_client.storage.from_(SUPABASE_CHAT_BUCKET).upload(
                    attachment_path,
                    attachment["data"],
                    file_options={
                        "content-type": message["attachment_type"],
                        "upsert": "false",
                    },
                )
                message["attachment_path"] = attachment_path
            supabase_client.table("chat_messages").insert(message).execute()
        except Exception:
            if attachment_path:
                try:
                    supabase_client.storage.from_(SUPABASE_CHAT_BUCKET).remove(
                        [attachment_path]
                    )
                except Exception:
                    pass
            return False
    st.session_state.chat_last_sent_at = now
    return True


def set_chat_message_hidden(message_id, is_hidden):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        for message in st.session_state.chat_messages:
            if message["id"] == message_id:
                message["is_hidden"] = is_hidden
                return True
        return False
    try:
        response = supabase_client.table("chat_messages").update(
            {"is_hidden": is_hidden}
        ).eq("id", message_id).select("id").execute()
        return bool(response.data)
    except Exception:
        return False


@st.fragment(run_every="10s")
def render_community_chat():
    st.markdown("### 💬 Community chat")
    if st.session_state.demo_mode:
        st.info("Presentation demo · chat messages are stored only in this session.")
    elif SUPABASE_AVAILABLE:
        st.caption("Shared community chat · refreshes automatically every 10 seconds.")
    else:
        st.info("Session-only chat · connect Supabase to chat with people in other sessions.")
    st.caption(
        "Community chat is not private: messages and uploaded files are visible to other chat users "
        "and may be examined by the app's moderators. Be careful—never share passwords, contact "
        "details, or other personal or sensitive information."
    )

    attachment_key = (
        f"community_chat_attachment_{st.session_state.chat_attachment_widget_version}"
    )
    uploaded_file = st.file_uploader(
        "Attach one PNG, JPG, WebP, PDF, or TXT file (max 1 MB)",
        type=["png", "jpg", "jpeg", "webp", "pdf", "txt"],
        key=attachment_key,
        max_upload_size=1,
    )
    with st.form("community_chat_form", clear_on_submit=True):
        message_text = st.text_area(
            "Your message",
            max_chars=500,
            placeholder="Say hello to the community...",
            height=90,
        )
        send_message = st.form_submit_button("Send message 💌", width="stretch")
    if send_message:
        attachment = None
        if uploaded_file is not None:
            attachment = {
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "data": uploaded_file.getvalue(),
            }
            try:
                attachment["type"] = validate_chat_attachment(
                    attachment["name"], attachment["type"], attachment["data"]
                )
            except ValueError as error:
                st.warning(str(error))
                attachment = False
        if attachment is False:
            pass
        elif not message_text.strip() and attachment is None:
            st.warning("Write a message or attach a file before sending.")
        elif st.session_state.get("chat_last_sent_at") and (
            datetime.now().astimezone() - st.session_state.chat_last_sent_at
        ).total_seconds() < 2:
            st.warning("Please wait a moment before sending another message.")
        elif send_chat_message(
            st.session_state.user_id,
            st.session_state.get("profile_display_name", "Student"),
            message_text,
            attachment,
        ):
            record_activity(st.session_state.user_id, "community_chat", 2)
            st.session_state.chat_attachment_widget_version += 1
            st.toast("Message sent!")
            st.rerun()
        else:
            st.error("Could not send your message. Check the connection and try again.")

    messages = get_chat_messages(include_hidden=st.session_state.admin_authenticated)
    if messages is None:
        st.error("The shared chat is unavailable. Check the database setup and connection.")
        return
    if not messages:
        st.info("No messages yet. Start the conversation!")
        return

    for message in reversed(messages):
        if message.get("is_hidden", False):
            with st.expander("Hidden message · owner only"):
                st.caption(f"{message['display_name']} · {message['created_at']}")
                st.markdown(html.escape(message["body"]))
                if message.get("attachment_data") is not None:
                    st.download_button(
                        f"Download {html.escape(message['attachment_name'])}",
                        data=message["attachment_data"],
                        file_name=os.path.basename(message["attachment_name"]),
                        mime=message["attachment_type"],
                        key=f"chat_download_{message['id']}",
                    )
                elif message.get("attachment_path"):
                    attachment_url = message.get("attachment_url")
                    if attachment_url:
                        st.link_button(
                            f"Download {message['attachment_name']}",
                            attachment_url,
                            help="This private file link expires in one hour.",
                        )
                    else:
                        st.caption("Attachment link could not be generated. Refresh to try again.")
                if st.button("Restore message", key=f"restore_chat_{message['id']}"):
                    if set_chat_message_hidden(message["id"], False):
                        st.toast("Message restored.")
                        st.rerun()
                    st.error("Could not restore this message.")
            continue

        with st.container(border=True):
            st.markdown(
                f"**{html.escape(message['display_name'])}** · "
                f"<span style='color:#73695f'>{html.escape(message['created_at'])}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(html.escape(message["body"]))
            if message.get("attachment_data") is not None:
                st.download_button(
                    f"Download {html.escape(message['attachment_name'])}",
                    data=message["attachment_data"],
                    file_name=os.path.basename(message["attachment_name"]),
                    mime=message["attachment_type"],
                    key=f"chat_download_{message['id']}",
                )
            elif message.get("attachment_path"):
                attachment_url = message.get("attachment_url")
                if attachment_url:
                    st.link_button(
                        f"Download {message['attachment_name']}",
                        attachment_url,
                        help="This private file link expires in one hour.",
                    )
                else:
                    st.caption("Attachment link could not be generated. Refresh to try again.")
            if st.session_state.admin_authenticated and st.button(
                "Hide message",
                key=f"hide_chat_{message['id']}",
            ):
                if set_chat_message_hidden(message["id"], True):
                    st.toast("Message hidden from the community.")
                    st.rerun()
                st.error("Could not hide this message.")


def save_mood_log(user_id, mood_score, mood_label, recommendation):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        st.session_state.demo_mood_logs.append(
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                "mood_score": mood_score,
                "mood_label": mood_label,
                "recommendation": recommendation,
            }
        )
        return True
    try:
        supabase_client.table("mood_logs").insert(
            {
                "user_id": user_id,
                "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                "mood_score": mood_score,
                "mood_label": mood_label,
                "recommendation": recommendation,
            }
        ).execute()
        return True
    except Exception:
        return False


def get_user_history(user_id):
    if st.session_state.get("demo_mode") or not SUPABASE_AVAILABLE:
        return pd.DataFrame(
            [item for item in st.session_state.demo_mood_logs if item["user_id"] == user_id],
            columns=["id", "user_id", "timestamp", "mood_score", "mood_label", "recommendation"],
        )
    if not SUPABASE_AVAILABLE:
        return None

    try:
        response = supabase_client.table("mood_logs").select(
            "id,user_id,timestamp,mood_score,mood_label,recommendation"
        ).eq("user_id", user_id).order("timestamp").execute()
        return pd.DataFrame(response.data)
    except Exception:
        return None


def delete_user_history(user_id):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        st.session_state.demo_mood_logs = [
            item for item in st.session_state.demo_mood_logs if item["user_id"] != user_id
        ]
        return True
    try:
        supabase_client.table("mood_logs").delete().eq("user_id", user_id).execute()
        return True
    except Exception:
        return False


def render_report_control(target_type, target_id, reporter_id, key_suffix):
    if not SUPABASE_AVAILABLE or st.session_state.get("demo_mode"):
        return
    with st.expander("Report this post"):
        with st.form(f"report_{target_type}_{key_suffix}"):
            reason = st.selectbox(
                "Reason",
                ["Inappropriate content", "Spam", "Harassment", "Copyright concern", "Other"],
                key=f"report_reason_{target_type}_{key_suffix}",
            )
            submitted = st.form_submit_button("Send report")
        if submitted:
            if submit_content_report(target_type, target_id, reporter_id, reason):
                st.success("Thanks. The post has been sent to the moderation queue.")
            else:
                st.warning("Could not save this report. Check the connection or see if it was already submitted.")


def render_moderation_queue():
    if st.session_state.get("demo_mode"):
        st.caption("The demo workspace does not access the live moderation queue.")
        return
    reports = get_open_content_reports()
    if reports is None:
        st.warning("Reports are unavailable. Check the Supabase connection and database setup.")
        return
    st.markdown("#### Open community reports")
    if not reports:
        st.caption("There are no open reports.")
        return
    for report in reports:
        target_label = "Meme" if report["target_type"] == "meme" else "Joke"
        with st.expander(f"{target_label} report · {report['reason']}"):
            st.caption(
                f"Submitted {report['created_at']} · Reporter {report['reporter_id']} · "
                f"Post {report['target_id']}"
            )
            hide_col, dismiss_col = st.columns(2)
            with hide_col:
                if st.button("Hide post and resolve", key=f"hide_report_{report['id']}"):
                    if resolve_content_report(
                        report["id"], report["target_type"], report["target_id"], hide_content=True
                    ):
                        st.toast("Post hidden and report resolved.")
                        st.rerun()
                    st.error("Could not hide the post or resolve its report.")
            with dismiss_col:
                if st.button("Dismiss report", key=f"dismiss_report_{report['id']}"):
                    if resolve_content_report(report["id"]):
                        st.toast("Report dismissed.")
                        st.rerun()
                    st.error("Could not resolve this report.")


def render_post_interactions(target_type, target_id, user_id):
    interaction_data = get_post_interactions(target_type, target_id, user_id)
    if interaction_data is None:
        st.caption("Reactions and comments are temporarily unavailable.")
        return
    reaction_columns = st.columns(3)
    for column, reaction, label in zip(
        reaction_columns, ("like", "laugh", "love"), ("Like", "Laugh", "Love")
    ):
        with column:
            selected = interaction_data["mine"] == reaction
            if st.button(
                f"{'✓ ' if selected else ''}{label} · {interaction_data['counts'][reaction]}",
                key=f"reaction_{target_type}_{target_id}_{reaction}",
                width="stretch",
            ):
                if set_post_reaction(target_type, target_id, user_id, reaction):
                    record_activity(user_id, "community_reaction", 2)
                    st.rerun()
                st.error("Could not save your reaction.")
    with st.form(f"comment_{target_type}_{target_id}", clear_on_submit=True):
        comment = st.text_input("Add a comment", max_chars=300, key=f"comment_input_{target_type}_{target_id}")
        submitted = st.form_submit_button("Post comment")
    if submitted:
        if add_post_comment(target_type, target_id, user_id, comment):
            record_activity(user_id, "community_comment", 3)
            st.rerun()
        st.error("Could not post your comment. Make sure it is not empty.")
    if interaction_data["comments"]:
        with st.expander(f"Comments ({len(interaction_data['comments'])})"):
            for item in interaction_data["comments"]:
                st.markdown(
                    f"<div class='community-comment'><b>{html.escape(item['user_id'])}</b> · "
                    f"{html.escape(item['body'])}</div>",
                    unsafe_allow_html=True,
                )


def render_game_embed(markup, height, description):
    accessibility_styles = """
    <style>
      :focus-visible { outline: 3px solid #f0bd78 !important; outline-offset: 3px !important; }
      button { font: inherit; }
      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
      }
    </style>
    """
    st.iframe(
        markup + accessibility_styles,
        height=height,
        alt=description,
    )


# --- UI Helpers ---

def inject_css():
    """Injects the app's shared visual theme."""
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
    [data-testid="stMainBlockContainer"] {
        max-width: 1240px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    h1, h2, h3, h4, [data-testid="stMetricValue"] {
        color: #282522;
        font-family: 'Fredoka', sans-serif !important;
        font-weight: 600;
        letter-spacing: 0;
    }
    h1 { color: #e8593d; font-size: clamp(2rem, 4vw, 3rem) !important; }
    h2 { font-size: clamp(1.45rem, 3vw, 2rem) !important; }
    p, label, [data-testid="stCaption"] { color: #73695f; }
    [data-testid="stSidebar"] { background: #fff3e6; }
    [data-testid="stSidebar"] h2 { color: #e8593d; }
    [data-testid="stSidebar"] [data-testid="stCaption"] { color: #73695f; }
    .stButton > button, [data-testid="stFormSubmitButton"] button {
        min-height: 2.7rem;
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
        color: #282522;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif;
        font-weight: 800;
        padding: 10px 16px;
        color: #73695f;
    }
    .stTabs [aria-selected="true"] { color: #282522; }
    [data-baseweb="tab-highlight"] { background: #e8593d; }
    [data-testid="stForm"] {
        border: 2px solid #282522;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.88);
        box-shadow: 5px 5px 0 #282522;
        padding: 20px;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-color: #e4d6bf;
        border-radius: 10px;
        background: #fff;
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(40, 37, 34, 0.22);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.76);
    }
    [data-testid="stFileUploader"] section {
        border: 2px dashed #e8593d;
        border-radius: 12px;
        background: #fff5e8;
    }
    .welcome-hero {
        position: relative;
        overflow: hidden;
        margin: 0 0 1.75rem;
        padding: clamp(1.6rem, 4vw, 3rem);
        border: 2px solid #282522;
        border-radius: 18px;
        background:
            radial-gradient(circle at 92% 12%, rgba(76, 201, 240, .30), transparent 23%),
            radial-gradient(circle at 8% 110%, rgba(255, 210, 76, .36), transparent 30%),
            #fff1d5;
        color: #282522;
        box-shadow: 5px 5px 0 #282522;
    }
    .welcome-hero::after {
        position: absolute;
        right: -45px;
        bottom: -120px;
        width: 280px;
        height: 280px;
        border: 2px solid rgba(232, 89, 61, 0.22);
        border-radius: 50%;
        content: "";
        box-shadow: 0 0 0 34px rgba(232, 89, 61, 0.045), 0 0 0 70px rgba(65, 196, 177, 0.08);
        pointer-events: none;
    }
    .welcome-eyebrow {
        margin-bottom: .7rem;
        color: #a35d38;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
    }
    .welcome-hero h1 {
        margin: 0 0 .65rem;
        color: #e8593d;
        font-size: clamp(2.2rem, 5vw, 3.6rem) !important;
        line-height: 1.1;
        text-shadow: 2px 2px 0 rgba(255, 210, 76, .6);
    }
    .welcome-hero p {
        max-width: 600px;
        margin: 0;
        color: #5d6259;
        font-size: 1rem;
        line-height: 1.65;
    }
    .feature-pills {
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin-top: 1.45rem;
    }
    .feature-pill {
        padding: .42rem .75rem;
        border: 1px solid rgba(40, 37, 34, .28);
        border-radius: 999px;
        background: #fff;
        color: #282522;
        font-size: .8rem;
        font-weight: 700;
    }
    .section-kicker {
        margin: .15rem 0 .45rem;
        color: #e8593d;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    :focus-visible {
        outline: 3px solid #e8593d !important;
        outline-offset: 3px !important;
    }
    .stButton > button:focus-visible,
    [data-testid="stFormSubmitButton"] button:focus-visible {
        outline: 3px solid #e8593d !important;
        outline-offset: 3px !important;
    }
    [data-testid="stMarkdownContainer"] a { color: #d04f35; text-underline-offset: 3px; }
    [data-testid="stMetric"] {
        padding: 1rem;
        border: 2px solid #282522;
        border-radius: 14px;
        background: #fff;
        box-shadow: 3px 3px 0 rgba(40, 37, 34, .22);
    }
    .profile-avatar {
        display: inline-grid;
        width: 3.2rem;
        height: 3.2rem;
        place-items: center;
        border-radius: 50%;
        color: #fff;
        border: 2px solid #282522;
        font: 700 1.35rem 'Fredoka', sans-serif;
    }
    .community-comment {
        padding: .6rem .75rem;
        border-left: 3px solid #e8593d;
        border-radius: 0 10px 10px 0;
        background: #fff8e9;
        color: #4a4138;
        font-size: .9rem;
    }
    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding: 1.25rem 1rem 3rem; }
        [data-testid="stForm"] { padding: 14px; }
        .stTabs [data-baseweb="tab"] { padding: 8px 7px; font-size: 0.83rem; }
        .welcome-hero { border-radius: 14px; box-shadow: 3px 3px 0 #282522; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            scroll-behavior: auto !important;
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .01ms !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def hero_header(title, subtitle, chips=None):
    feature_markup = ""
    if chips:
        feature_markup = "<div class='feature-pills'>" + "".join(
            f"<span class='feature-pill'>{html.escape(chip)}</span>" for chip in chips
        ) + "</div>"
    st.markdown(
        f"<section class='welcome-hero'><div class='welcome-eyebrow'>A small break, well spent</div>"
        f"<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p>{feature_markup}</section>",
        unsafe_allow_html=True,
    )

# --- Page Setup ---

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not SUPABASE_AVAILABLE and not st.session_state.get("demo_mode", False):
    st.warning(
        "Supabase is not connected or its schema is incomplete. Mood history, reports, and "
        "shared scores are unavailable; community posts will only be saved for this session."
    )
    if SUPABASE_ERROR:
        st.caption("Check the Supabase secrets and run the SQL setup script from the project.")
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
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False
if "profile_display_name" not in st.session_state:
    st.session_state.profile_display_name = ""
for state_key in ("demo_profiles", "demo_comments", "demo_reactions"):
    if state_key not in st.session_state:
        st.session_state[state_key] = {}
if "demo_activity_events" not in st.session_state:
    st.session_state.demo_activity_events = []
if "demo_game_scores" not in st.session_state:
    st.session_state.demo_game_scores = []
if "demo_mood_logs" not in st.session_state:
    st.session_state.demo_mood_logs = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_attachment_widget_version" not in st.session_state:
    st.session_state.chat_attachment_widget_version = 0
if "demo_seeded" not in st.session_state:
    st.session_state.demo_seeded = False
if "india_gk_index" not in st.session_state:
    st.session_state.india_gk_index = random.randrange(len(INDIA_GK_QUESTIONS))
if "india_gk_answer_revealed" not in st.session_state:
    st.session_state.india_gk_answer_revealed = False
if "riddle_index" not in st.session_state:
    st.session_state.riddle_index = 0
if "riddle_started_at" not in st.session_state:
    st.session_state.riddle_started_at = None
if "riddle_answer_revealed" not in st.session_state:
    st.session_state.riddle_answer_revealed = False

# --- Sidebar ---

with st.sidebar:
    st.markdown(f"## 😂 {APP_TITLE}")
    st.caption(APP_SUBTITLE)
    st.divider()

    if not st.session_state.logged_in:
        st.info("Log in from the main page to unlock all tabs.")
    else:
        st.success(f"Hi there, **{st.session_state.user_id}**")
        if st.button("End Session", width="stretch"):
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            # Clear other session keys to prevent stale state errors
            for k in list(st.session_state.keys()):
                if k not in ("logged_in", "user_id", "demo_mode", "demo_mood_logs", "chat_messages"):
                    del st.session_state[k]
            st.rerun()

    st.divider()
    with st.expander("🔐 Owner controls", expanded=st.session_state.admin_authenticated):
        if not APP_ADMIN_PASSWORD:
            st.caption("Set APP_ADMIN_PASSWORD in Streamlit secrets to enable content management.")
        elif st.session_state.admin_authenticated:
            st.success("Owner access is enabled for this session.")
            if st.button("Lock owner tools", key="admin_logout", width="stretch"):
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

if not st.session_state.logged_in:
    hero_header(
        "Welcome to Giggle and Laugh!",
        "Your little corner for mini games, memes, jokes, and a mood check. Come in, pick a game, and leave with a smile.",
        chips=[
            "🎮 Mini games",
            "✨ Daily challenges",
            "🏅 Player badges",
            "😂 Jokes",
            "🖼️ Meme gallery",
            "🧘 Mood tracker"
        ],
    )

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("<div class='section-kicker'>Get started</div>", unsafe_allow_html=True)
        st.markdown("#### 👋 Quick Login")
        if "demo_mode_toggle" not in st.session_state:
            st.session_state.demo_mode_toggle = st.session_state.demo_mode
        st.checkbox(
            "Use presentation demo mode",
            key="demo_mode_toggle",
            help="Load sample analytics and keep profile, activity, reaction, and chat data in this browser session.",
        )
        st.session_state.demo_mode = st.session_state.demo_mode_toggle
        if st.session_state.demo_mode and not st.session_state.demo_seeded:
            st.session_state.community_memes.extend(
                [
                    {
                        "_id": "demo-meme-1",
                        "title": "Monday loading...",
                        "desc": "When the coffee has not kicked in yet.",
                        "image": None,
                        "user_id": "FUN-DEMO",
                    }
                ]
            )
            st.session_state.community_jokes.extend(
                [
                    {
                        "_id": "demo-joke-1",
                        "category": "Tech",
                        "text": "Why did the developer go broke? Because they used up all their cache.",
                        "user_id": "FUN-DEMO",
                    }
                ]
            )
            demo_score_timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
            st.session_state.demo_game_scores.extend([
                {"user_id": "FUN-DEMO", "game_name": game_name, "score": score, "created_at": demo_score_timestamp}
                for game_name, score in [
                    ("clicker", 72),
                    ("flap-dash", 12),
                    ("temple-dash", 340),
                    ("grand-prix", 840),
                    ("skyway-sprint", 510),
                    ("rock-paper-scissors", 1),
                    ("rock-paper-scissors", 1),
                    ("rock-paper-scissors", 0),
                    ("rock-paper-scissors", 1),
                ]
            ])
            st.session_state.demo_seeded = True
        with st.form("login_form"):
            raw_id = st.text_input("Choose a nickname", placeholder="e.g. Alex")
            go = st.form_submit_button("Start Laughing 🎈", width="stretch", type="primary")
        if go:
            if raw_id.strip():
                st.session_state.user_id = hash_pseudonym(raw_id)
                st.session_state.profile_display_name = raw_id.strip()[:30]
                st.session_state.logged_in = True
                if st.session_state.demo_mode:
                    st.session_state.demo_profiles[st.session_state.user_id] = {
                        "display_name": st.session_state.profile_display_name,
                        "avatar_color": "#24473f",
                        "bio": "",
                    }
                else:
                    save_profile(
                        st.session_state.user_id,
                        st.session_state.profile_display_name,
                        "#24473f",
                        "",
                    )
                st.rerun()
            else:
                st.warning("Please enter a nickname to continue.")

    with right:
        st.markdown("<div class='section-kicker'>Explore</div>", unsafe_allow_html=True)
        st.markdown("#### ✨ What's inside")
        st.markdown("""
        - **Daily challenges** — build streaks and collect badges
        - **Overview dashboard** — explore mood trends and community activity
        - **Mood check** — record how you feel and see your history
        - **Games** — six quick experiences, from arcade classics to original runners
        - **Meme gallery** — browse community posts and templates
        - **Community chat** — talk with other people using the app
        - **Jokes** — explore a filterable library or share your own
        """)

    st.stop()  # Only stops here, AFTER showing the login UI


# ---- Tabs (only reached when logged in) ----

st.title(f"😂 {APP_TITLE}")
active_profile = get_profile(st.session_state.user_id)
if active_profile is None:
    st.warning("Your profile could not be loaded. Try again after checking the database connection.")
    active_profile = {
        "display_name": st.session_state.profile_display_name or "Guest",
        "avatar_color": "#24473f",
        "bio": "",
    }
st.caption(f"Welcome back, {html.escape(active_profile['display_name'])}. {APP_SUBTITLE}")
if st.session_state.demo_mode:
    st.info("Presentation demo mode · sample platform analytics are illustrative, not live community data.")

(
    tab_dashboard,
    tab_daily,
    tab_profile,
    tab_vibe,
    tab_games,
    tab_memes,
    tab_jokes,
    tab_chat,
    tab_india_gk,
    tab_riddles,
) = st.tabs(
    [
        "📊 Overview",
        "🎯 Daily Challenge",
        "🏅 Profile",
        "🧘 Mood Check",
        "🎮 Games Zone",
        "🖼️ Meme Gallery",
        "😂 Joke Factory",
        "💬 Community Chat",
        "🇮🇳 India GK",
        "🧩 Riddles",
    ]
)

with tab_dashboard:
    st.markdown("### 📊 Community overview")
    st.caption("A quick look at participation and what the community has been enjoying.")
    render_anonymous_pulse()
    analytics = get_platform_analytics()
    if analytics is None:
        st.info("Platform analytics need a working Supabase connection. Enable demo mode on the welcome screen to preview the dashboard.")
    else:
        mood_scores = analytics["moods"]
        score_rows = analytics["game_scores"]
        average_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0
        games_played = len(score_rows)
        games_col, mood_col, players_col, posts_col = st.columns(4)
        games_col.metric("Recorded game rounds", f"{games_played:,}")
        mood_col.metric("Average mood check-in", f"{average_mood:.1f} / 4" if mood_scores else "—")
        players_col.metric("Daily active users", f"{analytics['active_today']:,}")
        posts_col.metric("Community posts", f"{analytics['meme_count'] + analytics['joke_count']:,}")
        if mood_scores:
            mood_distribution = pd.Series(mood_scores, name="Check-ins").value_counts().sort_index()
            mood_labels = {1: "Low energy", 2: "Neutral", 3: "Good", 4: "Great"}
            mood_distribution.index = [mood_labels[int(score)] for score in mood_distribution.index]
            st.markdown("#### 🧘 Mood check-in distribution")
            st.bar_chart(mood_distribution)
        mood_history = pd.DataFrame(analytics["mood_records"])
        if not mood_history.empty:
            mood_history["day"] = pd.to_datetime(mood_history["timestamp"]).dt.date
            mood_trend = mood_history.groupby("day")["mood_score"].mean()
            st.markdown("#### 📈 Mood trend")
            st.line_chart(mood_trend, height=220)
        activity_history = pd.DataFrame(analytics["activity_records"])
        if not activity_history.empty:
            daily_users = activity_history.groupby("activity_date")["user_id"].nunique()
            st.markdown("#### 👥 Daily active users · last 30 days")
            st.line_chart(daily_users, height=220)
        if score_rows:
            game_data = pd.DataFrame(score_rows)
            game_counts = game_data.groupby("game_name").size().sort_values(ascending=False)
            game_counts.name = "Recorded scores"
            st.markdown("#### 🎮 Game activity")
            st.bar_chart(game_counts)
        if analytics["top_posts"]:
            st.markdown("#### 💛 Community favorites")
            st.dataframe(
                pd.DataFrame(analytics["top_posts"]),
                width="stretch",
                hide_index=True,
            )
        st.caption(
            "Live charts show anonymous aggregates from recent records. Arcade scores are self-reported; "
            "mood trends are not a medical assessment. Demo charts use illustrative sample data."
        )

    user_events = get_user_activity(st.session_state.user_id)
    if user_events is None:
        st.warning("Your activity summary is unavailable. Check the database setup.")
    else:
        user_points = sum(int(event["points"]) for event in user_events)
        user_streak = calculate_activity_streak([event["activity_date"] for event in user_events])
        st.markdown("#### ✨ Your progress")
        point_col, streak_col = st.columns(2)
        point_col.metric("Points earned", user_points)
        streak_col.metric("Active-day streak", f"{user_streak} days")

with tab_daily:
    st.markdown("### 🎯 Daily challenge")
    st.caption("Small steps count. Complete one activity today to earn 10 bonus points.")
    daily_events = get_user_activity(st.session_state.user_id)
    if daily_events is None:
        st.error("Daily challenge progress could not be loaded. Check the database connection.")
    else:
        today = date.today().isoformat()
        today_events = [
            event for event in daily_events
            if event["activity_date"] == today and event["activity_type"] != "daily_reward"
        ]
        streak = calculate_activity_streak([event["activity_date"] for event in daily_events])
        points = sum(int(event["points"]) for event in daily_events)
        challenge_col, streak_col, points_col = st.columns(3)
        challenge_col.metric("Today's progress", "Complete" if today_events else "0 / 1")
        streak_col.metric("Current streak", f"{streak} days")
        points_col.metric("Total points", points)
        if today_events:
            st.success("Challenge complete — your 10-point daily bonus is included in your total!")
        else:
            st.info("Try a mood check-in, play a round, react to a post, leave a comment, or share something.")
        st.progress(1.0 if today_events else 0.0, text="Daily challenge")
        st.markdown("#### 🏅 Streak rewards")
        st.write("3 active days · 3-day streak badge")
        st.write("7 active days · Week of good vibes badge")

with tab_profile:
    st.markdown("### 🏅 Your player profile")
    st.caption("Your public nickname is a pseudonym, not a password-protected account.")
    profile = get_profile(st.session_state.user_id)
    if profile is None:
        st.error("Could not load your profile. Try again after checking the database connection.")
    else:
        user_events = get_user_activity(st.session_state.user_id)
        if user_events is None:
            st.error("Profile activity is unavailable. Check the database connection.")
            user_events = []
        points = sum(int(event["points"]) for event in user_events)
        streak = calculate_activity_streak([event["activity_date"] for event in user_events])
        game_days = len({
            (event["activity_type"], event["activity_date"])
            for event in user_events
            if event["activity_type"].startswith("play_")
        })
        badges = get_profile_badges(points, streak, game_days)
        initials = html.escape(profile["display_name"][:1].upper() or "?")
        avatar_color = profile.get("avatar_color", "#24473f")
        st.markdown(
            f"<span class='profile-avatar' style='background:{avatar_color}'>{initials}</span> "
            f"**{html.escape(profile['display_name'])}** · `{st.session_state.user_id}`",
            unsafe_allow_html=True,
        )
        if profile.get("bio"):
            st.caption(html.escape(profile["bio"]))
        point_col, streak_col, days_col = st.columns(3)
        point_col.metric("Points", points)
        streak_col.metric("Streak", f"{streak} days")
        days_col.metric("Game sessions", game_days)
        st.markdown("#### ✨ Achievements")
        if badges:
            st.write(" · ".join(f"🏅 {badge}" for badge in badges))
        else:
            st.caption("Keep checking in and joining the community to unlock badges.")
        if user_events:
            st.markdown("#### 🕒 Recent activity")
            recent_events = sorted(
                user_events,
                key=lambda event: event["activity_date"],
                reverse=True,
            )[:5]
            activity_table = pd.DataFrame(
                [
                    {
                        "Activity": event["activity_type"].replace("_", " ").title(),
                        "Date": event["activity_date"],
                        "Points": event["points"],
                    }
                    for event in recent_events
                ]
            )
            st.dataframe(activity_table, width="stretch", hide_index=True)
        with st.form("profile_edit_form"):
            display_name = st.text_input(
                "Display name", value=profile["display_name"], max_chars=30
            )
            avatar_color = st.selectbox(
                "Avatar color",
                ["#24473f", "#a35e46", "#4c6b91", "#7a5c91", "#a47b36"],
                index=["#24473f", "#a35e46", "#4c6b91", "#7a5c91", "#a47b36"].index(
                    profile.get("avatar_color", "#24473f")
                    if profile.get("avatar_color", "#24473f") in
                    ["#24473f", "#a35e46", "#4c6b91", "#7a5c91", "#a47b36"]
                    else "#24473f"
                ),
            )
            bio = st.text_area("About you", value=profile.get("bio", ""), max_chars=160)
            save_profile_button = st.form_submit_button("Save profile")
        if save_profile_button:
            if not display_name.strip():
                st.warning("Display name cannot be empty.")
            elif save_profile(
                st.session_state.user_id, display_name, avatar_color, bio
            ):
                st.session_state.profile_display_name = display_name.strip()
                st.toast("Profile saved.")
                st.rerun()
            else:
                st.error("Could not save the profile. Check the database connection.")

# 1. VIBE CHECK
with tab_vibe:
    st.markdown("### 🧘 Mood check")
    st.caption("Take a moment to check in. Your selection helps us suggest something for your break.")
    
    vibe_options = ["😢 Low Energy", "😐 Neutral", "🙂 Good", "🤩 Great", "😞 Sad", "🫥 Hopeless"]
    vibe_scores = [1, 2, 3, 4, 1, 1]
    vibe_labels = ["Low Energy", "Neutral", "Good", "Great", "Sad", "Hopeless"]
    selected_vibe_idx = st.radio(
        "How are you feeling?",
        range(len(vibe_options)),
        format_func=lambda index: vibe_options[index],
        horizontal=True,
    )
    selected_mood_label = vibe_labels[selected_vibe_idx]
    selected_mood_score = vibe_scores[selected_vibe_idx]
    selected_meme_title = st.selectbox(
        "Or pick a meme as your mood (optional)",
        [""] + [meme["title"] for meme in MEME_TEMPLATES],
        format_func=lambda title: title or "Choose a meme...",
    )
    if selected_meme_title:
        selected_meme = next(
            meme for meme in MEME_TEMPLATES if meme["title"] == selected_meme_title
        )
        selected_mood_label = selected_meme["mood_label"]
        selected_mood_score = selected_meme["mood_score"]
        st.info(
            f"{selected_meme['emoji']} **{selected_meme_title}** — "
            f"{selected_meme['emotion']}"
        )
    
    if st.button("Get Recommendation"):
        score = selected_mood_score
        mood_label = selected_mood_label
        rec_text = ""
        
        if mood_label in {"Sad", "Hopeless"}:
            rec_text = (
                "Thanks for checking in. You don't have to handle difficult feelings alone; "
                "consider reaching out to someone you trust or your college counseling center."
            )
            st.info(rec_text)
        elif score <= 2:
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
        if save_mood_log(st.session_state.user_id, score, mood_label, rec_text):
                record_activity(st.session_state.user_id, "mood_check", 5)
                st.toast("Vibe logged successfully!")
        else:
            st.warning("Supabase could not save this vibe. Check your connection and Supabase setup.")

    st.divider()
    st.markdown("#### 📈 Mood history")
    history_df = get_user_history(st.session_state.user_id)
    history_unavailable = history_df is None
    if history_unavailable:
        st.error("Could not load mood history. Check the Supabase connection and database setup.")
        history_df = pd.DataFrame(columns=["timestamp", "mood_score", "recommendation"])
    elif not history_df.empty:
        chart_df = history_df.copy()
        chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"])
        summary = summarize_mood_scores(chart_df["mood_score"].astype(int).tolist())
        metric_count, metric_average, metric_change = st.columns(3)
        metric_count.metric("Check-ins", summary["count"])
        metric_average.metric("Average mood", f"{summary['average']:.1f} / 4")
        metric_change.metric(
            "Change over history",
            "—" if summary["change"] is None else f"{summary['change']:+d}",
            help="Difference between your most recent and earliest recorded mood.",
        )
        st.line_chart(chart_df.set_index("timestamp")[["mood_score"]])
    else:
        st.write("No vibes logged yet. Click above to log one!")

    if not history_unavailable:
        distress_count = count_recent_distress_checkins(
            history_df.to_dict("records")
        )
        if distress_count >= 3:
            counseling_name = html.escape(
                COUNSELING_CENTER_NAME or "your college counseling center"
            )
            counseling_phone = html.escape(COUNSELING_CENTER_PHONE)
            phone_link = "".join(
                char for char in COUNSELING_CENTER_PHONE if char.isdigit() or char == "+"
            )
            if phone_link:
                st.info(
                    f"💛 You've logged Sad or Hopeless check-ins {distress_count} times this week. "
                    f"You deserve support. Contact **{counseling_name}** at "
                    f"[{counseling_phone}](tel:{phone_link}) if you'd like to talk."
                )
            else:
                st.info(
                    f"💛 You've logged Sad or Hopeless check-ins {distress_count} times this week. "
                    "You deserve support. Consider reaching out to someone you trust or your "
                    "college counseling center. The college contact number hasn't been configured yet."
                )

        st.divider()
        st.markdown("#### 🌷 Your mood garden")
        st.caption(
            "Each check-in day plants a flower that matches your mood. Plants keep their growth "
            "through breaks; they grow again when you check in."
        )
        garden = build_mood_garden(history_df.to_dict("records"))
        if garden:
            garden_cols = st.columns(4)
            plant_notes = {
                "Cactus": "resilient through stress",
                "Sunflower": "bright, happy energy",
                "Tulip": "steady growth",
                "Daisy": "a calm moment",
                "Seedling": "rest and renewal",
            }
            for index, plant in enumerate(reversed(garden[-12:])):
                with garden_cols[index % len(garden_cols)]:
                    st.markdown(f"### {plant['flower']} {plant['plant_name']}")
                    st.caption(
                        f"{plant['date']} · {plant['mood_label']} · {plant['growth_label']} · "
                        f"{plant_notes.get(plant['plant_name'], 'growing at your pace')}"
                    )
        else:
            st.caption("Your first check-in will plant a flower here.")

    with st.expander("Your data and privacy"):
        st.caption(
            "Mood check-ins are saved under your nickname-based ID. Download a copy or remove "
            "your saved mood history at any time. Mood data is not a medical assessment."
        )
        st.warning(
            "This demo's nickname login is not password-protected. Someone who enters the same "
            "nickname may access that nickname's history. Do not enter sensitive information."
        )
        if history_unavailable:
            st.caption("Download and deletion controls are unavailable until mood history can be loaded.")
        elif not history_df.empty:
            export_columns = [
                column for column in ("timestamp", "mood_score", "mood_label", "recommendation")
                if column in history_df.columns
            ]
            export_df = history_df[export_columns].copy()
            st.download_button(
                "Download mood history (CSV)",
                data=export_df.to_csv(index=False).encode("utf-8"),
                file_name="giggle-and-laugh-mood-history.csv",
                mime="text/csv",
                width="stretch",
            )
            confirm_delete = st.checkbox(
                "I understand this permanently deletes my saved mood check-ins.",
                key="confirm_delete_mood_history",
            )
            if st.button(
                "Delete my mood history",
                disabled=not confirm_delete,
                type="secondary",
                key="delete_mood_history",
            ):
                if delete_user_history(st.session_state.user_id):
                    st.session_state.confirm_delete_mood_history = False
                    st.toast("Your mood history has been deleted.")
                    st.rerun()
                st.error("Could not delete your mood history. Check the Supabase connection.")
        else:
            st.caption("There is no saved mood history to download or delete.")

# 2. GAMES ZONE
with tab_games:
    st.markdown("### 🎮 Games")
    st.write("Choose a quick game for your break.")
    clicker_tab, flappy_tab, runner_tab, racer_tab, skyway_tab, rps_tab = st.tabs(
        ["✨ Clicker", "🐤 Flap Dash", "🏛️ Temple Dash", "🏎️ Grand Prix", "🌤️ Skyway Sprint", "✊ Rock Paper Scissors"]
    )

    with clicker_tab:
        render_game_embed(GAMES_HTML, height=350, description="Clicker mini-game")

    with flappy_tab:
        render_game_embed(FLAPPY_HTML, height=455, description="Flap Dash mini-game")

    with runner_tab:
        render_game_embed(RUNNER_HTML, height=700, description="Temple Dash mini-game")

    with racer_tab:
        render_game_embed(RACER_HTML, height=760, description="Grand Prix mini-game")

    with skyway_tab:
        render_game_embed(PLATFORMER_HTML, height=680, description="Skyway Sprint mini-game")

    with rps_tab:
        st.markdown("#### Rock, Paper, Scissors")
        st.markdown("""
        <style>
            .rps-choice{min-height:126px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;margin:4px 0 10px;border:2px solid #282522;border-radius:14px;background:linear-gradient(180deg,#fff,#fff5e8);color:#282522;box-shadow:3px 3px 0 rgba(40,37,34,.18)}
            .rps-choice span{font-size:48px;line-height:1;filter:drop-shadow(2px 3px 0 rgba(40,37,34,.15))}
            .rps-choice b{font:800 13px 'DM Sans',sans-serif;letter-spacing:1px}
            .rps-choice small{color:#73695f;font:600 11px 'DM Sans',sans-serif}
            .rps-result{display:flex;align-items:center;justify-content:center;gap:22px;min-height:154px;margin-top:18px;padding:16px;border:2px solid #282522;border-radius:14px;background:radial-gradient(ellipse at 50% 0,#fff1c9,#fffaf1 75%);text-align:center;box-shadow:4px 4px 0 #282522}
            .rps-fighter{min-width:110px}.rps-fighter span{display:block;font-size:50px;line-height:1.15}.rps-fighter b{font:800 11px 'DM Sans',sans-serif;letter-spacing:1px;color:#73695f}
            .rps-versus{color:#e8593d;font:900 18px 'Fredoka',sans-serif}
            .rps-verdict{margin:10px 0 0;text-align:center;font:900 22px 'Fredoka',sans-serif;color:#2c766d}
            .rps-verdict.loss{color:#d25136}.rps-verdict.draw{color:#b07824}
            @media(max-width:520px){.rps-result{gap:8px;padding:12px 5px}.rps-fighter{min-width:88px}.rps-fighter span{font-size:40px}}
        </style>
        """, unsafe_allow_html=True)
        choices = {
            "Rock": {"symbol": "✊", "caption": "Solid as a boulder"},
            "Paper": {"symbol": "✋", "caption": "A clean sheet"},
            "Scissors": {"symbol": "✌️", "caption": "Snip snap"},
        }
        if "rps_player" not in st.session_state:
            st.session_state.rps_player = None
            st.session_state.rps_computer = None
            st.session_state.rps_result = None

        col1, col2, col3 = st.columns(3)

        def play_rps(choice):
            computer = random.choice(list(choices))
            result = get_rps_result(choice, computer)
            st.session_state.rps_player = choice
            st.session_state.rps_computer = computer
            st.session_state.rps_result = result
            st.session_state.rps_wins = st.session_state.get("rps_wins", 0) + (result == "win")
            st.session_state.rps_rounds = st.session_state.get("rps_rounds", 0) + 1
            record_activity(st.session_state.user_id, "play_rps", 2)
            if SUPABASE_AVAILABLE:
                st.session_state.rps_score_save_error = not record_game_score(
                    st.session_state.user_id, "rock-paper-scissors", int(result == "win")
                )

        for column, choice in zip((col1, col2, col3), choices):
            with column:
                move = choices[choice]
                st.markdown(
                    f"<div class='rps-choice'><span>{move['symbol']}</span><b>{choice.upper()}</b><small>{move['caption']}</small></div>",
                    unsafe_allow_html=True,
                )
                if st.button(f"Throw {choice}", key=f"rps_{choice.lower()}", width="stretch"):
                    play_rps(choice)

        if st.session_state.rps_result:
            player = st.session_state.rps_player
            computer = st.session_state.rps_computer
            result = st.session_state.rps_result
            verdict, verdict_class = {
                "win": ("YOU WIN THIS ROUND", ""),
                "draw": ("A PERFECT TIE", "draw"),
                "loss": ("COMPUTER TAKES THIS ONE", "loss"),
            }[result]
            st.markdown(
                f"<div class='rps-result'><div class='rps-fighter'><b>YOU</b><span>{choices[player]['symbol']}</span><b>{player.upper()}</b></div>"
                f"<div class='rps-versus'>VS</div><div class='rps-fighter'><b>COMPUTER</b><span>{choices[computer]['symbol']}</span><b>{computer.upper()}</b></div></div>"
                f"<div class='rps-verdict {verdict_class}'>{verdict}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<p class='rps-verdict draw'>CHOOSE YOUR MOVE</p>", unsafe_allow_html=True)

        st.caption(
            f"Your session: {st.session_state.get('rps_wins', 0)} wins in "
            f"{st.session_state.get('rps_rounds', 0)} rounds."
        )
        rps_period = st.selectbox(
            "Leaderboard period",
            ["All-time", "Last 7 days"],
            key="rps_leaderboard_period",
        )
        leaderboard = get_game_leaderboard("rock-paper-scissors", rps_period)
        if leaderboard is None:
            st.info("Connect Supabase to save scores and see the shared leaderboard.")
        elif leaderboard.empty:
            if not SUPABASE_AVAILABLE and not st.session_state.demo_mode:
                st.caption("Your rounds stay in this session. Connect Supabase to share a leaderboard.")
            else:
                st.caption("The leaderboard is waiting for its first score.")
        else:
            leaderboard_title = (
                "Demo leaderboard · RPS wins"
                if st.session_state.demo_mode
                else "Community leaderboard · RPS wins"
            )
            st.markdown(f"#### {leaderboard_title}")
            leaderboard_display = leaderboard.rename(
                columns={"user_id": "Player", "wins": "Wins", "rounds": "Rounds"}
            )
            leaderboard_display.index = leaderboard_display.index + 1
            st.dataframe(leaderboard_display, width="stretch")
        if st.session_state.get("rps_score_save_error"):
            st.warning("This round counted for your session, but its shared score could not be saved.")

    st.divider()
    st.markdown("#### Arcade scoreboards")
    st.caption(
        "Arcade best scores are player-submitted and unverified; Rock-Paper-Scissors results are recorded automatically."
    )
    arcade_games = {
        "Clicker": "clicker",
        "Flap Dash": "flap-dash",
        "Temple Dash": "temple-dash",
        "Grand Prix": "grand-prix",
        "Skyway Sprint": "skyway-sprint",
    }
    score_game_label = st.selectbox("Choose a game", list(arcade_games), key="arcade_score_game")
    arcade_period = st.selectbox(
        "Leaderboard period",
        ["All-time", "Last 7 days"],
        key="arcade_leaderboard_period",
    )
    with st.form("arcade_score_form"):
        submitted_score = st.number_input(
            "Your best score (self-reported)",
            min_value=0,
            max_value=100000,
            value=0,
            step=1,
        )
        score_submitted = st.form_submit_button("Save my score")
    if score_submitted:
        if record_game_score(
            st.session_state.user_id, arcade_games[score_game_label], int(submitted_score)
        ):
            record_activity(st.session_state.user_id, "play_arcade", 2)
            st.toast("Score saved.")
        else:
            st.error("Could not save this score. Check the database connection.")
    arcade_leaderboard = get_game_leaderboard(arcade_games[score_game_label], arcade_period)
    if arcade_leaderboard is None:
        st.info("Arcade scoreboards require a working Supabase connection.")
    elif arcade_leaderboard.empty:
        st.caption("No scores have been submitted for this game yet.")
    else:
        if not SUPABASE_AVAILABLE and not st.session_state.demo_mode:
            st.caption("These scores are stored only in this browser session.")
        arcade_display = arcade_leaderboard.rename(
            columns={"user_id": "Player", "score": "Best score"}
        )
        arcade_display.index = arcade_display.index + 1
        st.dataframe(arcade_display, width="stretch")

# 3. MEME GALLERY
with tab_memes:
    st.markdown("### 🖼️ Meme gallery")
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
                meme_submitted = st.form_submit_button("Pin it to the wall 📌", width="stretch")
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
                        "image_type": meme_image.type,
                        "image_extension": {
                            "image/png": "png",
                            "image/jpeg": "jpg",
                            "image/webp": "webp",
                        }.get(meme_image.type, "png"),
                        "user_id": st.session_state.user_id,
                        "_id": str(uuid.uuid4()),
                    }
                    if save_community_meme(meme):
                        record_activity(st.session_state.user_id, "share_content", 5)
                        st.toast("Your meme is on the shared wall! 🎉")
                        st.rerun()
                    else:
                        st.session_state.community_memes.append(meme)
                        record_activity(st.session_state.user_id, "share_content", 5)
                        if st.session_state.demo_mode:
                            st.info("Demo post saved in this browser session only.")
                        else:
                            st.warning("Supabase could not save this post. It is only visible in your session, not to everyone.")

        stored_memes = get_community_memes(include_hidden=st.session_state.admin_authenticated)
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
                        st.image(meme["image"], width="stretch")
                    is_session_only = meme in st.session_state.community_memes
                    st.caption("Session-only preview" if is_session_only else "Shared community meme")
                    st.caption(meme["desc"])
                    if not is_session_only:
                        render_report_control(
                            "meme", str(meme["_id"]), st.session_state.user_id, str(index)
                        )
                    if meme.get("_id") and (
                        not is_session_only or st.session_state.demo_mode or not SUPABASE_AVAILABLE
                    ):
                        render_post_interactions(
                            "meme", str(meme["_id"]), st.session_state.user_id
                        )
        else:
            st.info("No community memes yet. Be the first to post one!")

        if st.session_state.admin_authenticated and not st.session_state.demo_mode:
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
                st.caption("Hidden from the community" if selected_meme["is_hidden"] else "Visible to the community")
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
                if st.button(
                    "Restore selected meme" if selected_meme["is_hidden"] else "Hide selected meme",
                    key=f"toggle_meme_visibility_{selected_meme_id}",
                ):
                    if set_content_visibility("meme", selected_meme_id, not selected_meme["is_hidden"]):
                        st.toast("Meme visibility updated.")
                        st.rerun()
                    st.error("Could not update this meme's visibility.")
                if st.button("Delete selected meme", key=f"delete_meme_{selected_meme_id}"):
                    if delete_community_meme(selected_meme_id):
                        st.toast("Meme removed from the shared wall.")
                        st.rerun()
                    else:
                        st.error("Could not delete this meme.")
            else:
                st.info("There are no saved community memes to manage.")

    with template_tab:
        st.markdown("#### 📖 Meme Dictionary")
        st.caption("Hover over a meme card for its meaning, or use the same meme in your mood check-in.")
        cols = st.columns(2)
        for index, meme in enumerate(MEME_TEMPLATES):
            with cols[index % 2]:
                st.markdown(f"#### {meme['title']}")
                tooltip = html.escape(
                    f"{meme['title']} — {meme['emotion']}",
                    quote=True,
                )
                st.markdown(
                    f"<div title='{tooltip}' style='background:#ffe8b8;padding:24px;text-align:center;font-size:48px;border:2px solid #282522;border-radius:14px'>{meme['emoji']}</div>",
                    unsafe_allow_html=True,
                )
                st.caption(meme["desc"])
                st.caption(f"💭 Emotion: {meme['emotion']}")

# 4. JOKE FACTORY
with tab_jokes:
    st.markdown("### 😂 Joke library")
    community_joke_tab, joke_library_tab = st.tabs(["🌐 User Uploads", "📚 Joke Library"])

    with community_joke_tab:
        st.caption("Jokes submitted by users appear here for everyone.")
        if st.button("Refresh community jokes ↻"):
            st.rerun()

        with st.expander("🎤 Submit a joke", expanded=False):
            with st.form("joke_submit_form", clear_on_submit=True):
                submitted_joke = st.text_area("Your one-liner", max_chars=300, placeholder="Why did the scarecrow win an award?...")
                submitted_category = st.selectbox("Pick a shelf", ["Puns", "Tech", "Animals", "Work", "Science", "Food", "General"])
                joke_submitted = st.form_submit_button("Send it to the laugh lab 🧪", width="stretch")
            if joke_submitted:
                if submitted_joke.strip():
                    joke = {
                        "category": submitted_category,
                        "text": submitted_joke.strip(),
                        "user_id": st.session_state.user_id,
                    }
                    if save_community_joke(joke):
                        record_activity(st.session_state.user_id, "share_content", 5)
                        st.toast("Joke added to the shared laugh lab! 😄")
                        st.rerun()
                    else:
                        joke["_id"] = str(uuid.uuid4())
                        st.session_state.community_jokes.append(joke)
                        record_activity(st.session_state.user_id, "share_content", 5)
                        if st.session_state.demo_mode:
                            st.info("Demo joke saved in this browser session only.")
                        else:
                            st.warning("Supabase could not save this joke. It is only visible in your session, not to everyone.")
                else:
                    st.warning("Type a joke first. Even a terrible one counts.")

        stored_jokes = get_community_jokes(include_hidden=st.session_state.admin_authenticated)
        if stored_jokes is None:
            st.warning("The shared joke list is unavailable right now. Session-only previews are marked below.")
            stored_jokes = []
        community_jokes = stored_jokes + st.session_state.community_jokes
        if community_jokes:
            st.markdown("#### Community jokes")
            for index, joke in enumerate(community_jokes):
                session_only = joke in st.session_state.community_jokes
                label = "Session-only preview · " if session_only else ""
                with st.expander(f"{label}{joke['category']}: {joke['text'][:50]}..."):
                    st.markdown(joke["text"])
                    if not session_only:
                        render_report_control(
                            "joke", str(joke["_id"]), st.session_state.user_id, str(index)
                        )
                    if joke.get("_id") and (
                        not session_only or st.session_state.demo_mode or not SUPABASE_AVAILABLE
                    ):
                        render_post_interactions(
                            "joke", str(joke["_id"]), st.session_state.user_id
                        )
        else:
            st.info("No community jokes yet. Share the first one!")

        if st.session_state.admin_authenticated and not st.session_state.demo_mode:
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
                st.caption("Hidden from the community" if selected_joke["is_hidden"] else "Visible to the community")
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
                if st.button(
                    "Restore selected joke" if selected_joke["is_hidden"] else "Hide selected joke",
                    key=f"toggle_joke_visibility_{selected_joke_id}",
                ):
                    if set_content_visibility("joke", selected_joke_id, not selected_joke["is_hidden"]):
                        st.toast("Joke visibility updated.")
                        st.rerun()
                    st.error("Could not update this joke's visibility.")
                if st.button("Delete selected joke", key=f"delete_joke_{selected_joke_id}"):
                    if delete_community_joke(selected_joke_id):
                        st.toast("Joke removed from the shared laugh lab.")
                        st.rerun()
                    else:
                        st.error("Could not delete this joke.")
            else:
                st.info("There are no saved community jokes to manage.")
            st.divider()
            render_moderation_queue()

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

with tab_chat:
    render_community_chat()

with tab_india_gk:
    st.markdown("### 🇮🇳 India General Knowledge")
    st.caption(
        f"Explore {len(INDIA_GK_QUESTIONS)} questions about India's geography, history, "
        "culture, science, sport, and civic life."
    )
    question_index = st.session_state.india_gk_index
    question, answer = INDIA_GK_QUESTIONS[question_index]
    st.caption(f"Question {question_index + 1} of {len(INDIA_GK_QUESTIONS)}")
    st.markdown(f"#### {html.escape(question)}")
    next_col, reveal_col = st.columns(2)
    if next_col.button("🎲 Another question", key="next_india_gk", width="stretch"):
        question_choices = [
            index for index in range(len(INDIA_GK_QUESTIONS))
            if index != question_index
        ]
        st.session_state.india_gk_index = random.choice(question_choices)
        st.session_state.india_gk_answer_revealed = False
        st.rerun()
    if reveal_col.button(
        "👀 Reveal answer",
        key="reveal_india_gk",
        width="stretch",
        disabled=st.session_state.india_gk_answer_revealed,
    ):
        st.session_state.india_gk_answer_revealed = True
        st.rerun()
    if st.session_state.india_gk_answer_revealed:
        st.success(f"Answer: {html.escape(answer)}")
    st.caption("A learning activity, not a formal examination. Facts are best-effort curated.")


@st.fragment(run_every="1s")
def render_riddle():
    st.markdown("### 🧩 Riddle corner")
    st.caption(
        f"There are {len(RIDDLES)} riddles. Think it through: the answer unlocks after "
        "you have stayed with the current riddle for one full minute."
    )
    riddle, answer = RIDDLES[st.session_state.riddle_index]
    started_at = st.session_state.riddle_started_at
    elapsed_seconds = (
        max(0, int(datetime.now().timestamp() - started_at))
        if started_at is not None
        else 0
    )
    remaining_seconds = max(0, 60 - elapsed_seconds)
    st.caption(f"Riddle {st.session_state.riddle_index + 1} of {len(RIDDLES)}")
    st.markdown(f"#### {html.escape(riddle)}")
    st.progress(
        min(elapsed_seconds / 60, 1.0),
        text=(
            "Start the timer when you're ready."
            if started_at is None
            else
            "Answer unlocked!"
            if remaining_seconds == 0
            else f"Take your time · {remaining_seconds} seconds until the answer unlocks"
        ),
    )

    if started_at is None and st.button(
        "▶️ Start one-minute timer",
        key="start_riddle_timer",
        width="stretch",
    ):
        st.session_state.riddle_started_at = datetime.now().timestamp()
        st.rerun()

    if st.button(
        "🔓 Show answer",
        key="show_riddle_answer",
        disabled=started_at is None or remaining_seconds > 0,
        width="stretch",
    ):
        st.session_state.riddle_answer_revealed = True
    if st.session_state.riddle_answer_revealed:
        st.success(f"Answer: {html.escape(answer)}")

    if st.button("➡️ Next riddle", key="next_riddle", width="stretch"):
        st.session_state.riddle_index = (st.session_state.riddle_index + 1) % len(RIDDLES)
        st.session_state.riddle_started_at = None
        st.session_state.riddle_answer_revealed = False
        st.rerun()


with tab_riddles:
    render_riddle()