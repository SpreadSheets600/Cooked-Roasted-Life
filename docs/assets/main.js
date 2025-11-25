document.addEventListener("DOMContentLoaded", () => {
	// API Configuration
	const API_BASE = typeof window !== "undefined" && window.API_BASE ? window.API_BASE.replace(/\/$/, "") : "";
	const FRONTEND_BASE = typeof window !== "undefined" && window.FRONTEND_BASE ? window.FRONTEND_BASE.replace(/\/$/, "") : window.location.origin;

	// DOM Elements
	const form = document.getElementById("roast-form");

	const resultBox = document.getElementById("roast-result");
	const roastText = document.getElementById("roast-text");

	const shareBtn = document.getElementById("share-btn");

	const shareUrlBox = document.getElementById("share-url");
	const shareUrlInput = document.getElementById("share-url-input");

	const copyUrlBtn = document.getElementById("copy-url-btn");

	const historyList = document.getElementById("history-list");
	const submitButton = document.getElementById("generate-btn");
	const latestCard = document.getElementById("latest-card");
	const latestEmpty = document.getElementById("latest-empty");
	const latestUpdated = document.getElementById("latest-updated");
	const latestCardId = document.getElementById("latest-card-id");
	const latestCardTime = document.getElementById("latest-card-time");
	const latestCardText = document.getElementById("latest-card-text");
	const latestCardInputs = document.getElementById("latest-card-inputs");
	const latestReplayBtn = document.getElementById("latest-replay-btn");
	const latestOpenLink = document.getElementById("latest-open-link");

	const HISTORY_KEY = "roastHistory";

	// Spotify Elements
	const spotifyStatusText = document.getElementById("spotify-status-text");
	const spotifyIndicator = document.getElementById("spotify-indicator");
	const spotifyAuthBtn = document.getElementById("spotify-auth-btn");

	let currentRoastId = null;
	let spotifyAuthenticated = false;

	// Initialization Of Services
	setupEventListeners();
	checkAuthStatus();
	loadHistory();

	// Authentication Check
	async function checkAuthStatus() {
		try {
			const res = await fetch(`${API_BASE}/api/auth/status`, { credentials: "include" });
			if (res.ok) {
				const data = await res.json();
				spotifyAuthenticated = !!data.spotify_authenticated;
				updateSpotifyUI(data);
				validateDataSources();
			}
		} catch (e) {
			console.error("Authentication Check Failed", e);
		}
	}

	function updateSpotifyUI(data) {
		if (!spotifyIndicator || !spotifyStatusText || !spotifyAuthBtn) return;

		if (spotifyAuthenticated) {
			spotifyIndicator.classList.remove("bg-red-500");
			spotifyIndicator.classList.add("bg-green-500", "shadow-[0_0_10px_rgba(34,197,94,0.5)]");

			spotifyStatusText.textContent = `CONNECTED AS ${data.user.name?.toUpperCase() || "USER"}`;

			spotifyAuthBtn.textContent = "DISCONNECT";
			spotifyAuthBtn.href = `${API_BASE}/spotify/logout?redirect=${encodeURIComponent(window.location.href)}`;

			spotifyAuthBtn.classList.replace("bg-green-600", "bg-white/10");
			spotifyAuthBtn.classList.replace("hover:bg-green-500", "hover:bg-white/20");
		} else {
			spotifyIndicator.classList.add("bg-red-500");
			spotifyIndicator.classList.remove("bg-green-500", "shadow-[0_0_10px_rgba(34,197,94,0.5)]");

			spotifyStatusText.textContent = "DISCONNECTED";

			spotifyAuthBtn.textContent = "CONNECT";
			spotifyAuthBtn.href = `${API_BASE}/spotify/login?redirect=${encodeURIComponent(window.location.href)}`;

			spotifyAuthBtn.classList.replace("bg-white/10", "bg-green-600");
			spotifyAuthBtn.classList.replace("hover:bg-white/20", "hover:bg-green-500");
		}
	}

	// Form Validation
	function validateDataSources() {
		if (!form) return;

		const valorantName = document.getElementById("valorant_name")?.value.trim();
		const valorantTag = document.getElementById("valorant_tag")?.value.trim();

		const anilistUser = document.getElementById("anilist_user")?.value.trim();

		const steamId = document.getElementById("steam_id")?.value.trim();
		const steamVanity = document.getElementById("steam_vanity")?.value.trim();

		const hasValorant = valorantName && valorantTag;
		const hasSteam = steamId || steamVanity;
		const hasSpotify = spotifyAuthenticated;
		const hasAnilist = anilistUser;

		const hasAnyData = hasValorant || hasAnilist || hasSteam || hasSpotify;

		if (submitButton) {
			submitButton.disabled = !hasAnyData;
		}
	}

	function setupEventListeners() {
		if (!form) return;

		const inputs = form.querySelectorAll("input, select");
		inputs.forEach((input) => {
			input.addEventListener("input", validateDataSources);
			input.addEventListener("change", validateDataSources);
		});

		form.addEventListener("submit", (e) => {
			e.preventDefault();
			handleRoastSubmit(e);
		});

		submitButton?.addEventListener("click", handleRoastSubmit);

		shareBtn?.addEventListener("click", handleShare);
		copyUrlBtn?.addEventListener("click", handleCopyUrl);
	}

	// Roast Logic
	async function handleRoastSubmit(e) {
		if (e) e.preventDefault();
		if (!submitButton) return;

		// UI Loading State
		const originalBtnText = submitButton.innerHTML;
		submitButton.disabled = true;
		submitButton.innerHTML = '<span class="relative z-10">ANALYZING...</span>';

		resultBox.classList.remove("hidden");
		roastText.textContent = "ESTABLISHING NEURAL LINK...";
		shareUrlBox.classList.add("hidden");

		const rawEntries = Object.fromEntries(new FormData(form).entries());
		const data = Object.fromEntries(
			Object.entries(rawEntries)
				.map(([k, v]) => [k, typeof v === "string" ? v.trim() : v])
				.filter(([_, v]) => v !== "" && v !== undefined && v !== null)
		);

		try {
			const res = await fetch(`${API_BASE}/api/roast`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
				body: JSON.stringify(data),
			});

			const json = await res.json();

			if (json.error) throw new Error(json.error);

			currentRoastId = json.id;

			// Local History Save
			saveToLocalHistory({
				id: json.id,
				roast: json.roast,
				timestamp: json.timestamp || new Date().toISOString(),
				inputs: json.inputs || data,
			});

			// Force Clear
			roastText.textContent = "";

			if (json.roast) {
				setTimeout(() => {
					typeWriter(json.roast, roastText);
				}, 50);
			} else {
				roastText.textContent = "ROAST GENERATED BUT TEXT MISSING.";
			}

			resultBox.classList.remove("hidden");

			void resultBox.offsetWidth;
			resultBox.scrollIntoView({ behavior: "smooth", block: "center" });
		} catch (err) {
			console.error("Roast generation error:", err);

			roastText.textContent = "SYSTEM FAILURE : " + (err.message || "UNKNOWN ERROR");

			resultBox.classList.remove("hidden");
			resultBox.scrollIntoView({ behavior: "smooth", block: "start" });
		} finally {
			submitButton.disabled = false;
			submitButton.innerHTML = originalBtnText;
		}
	}

	function typeWriter(text, element, speed = 20) {
		if (!element) return;
		element.textContent = "";
		if (!text) return;

		let i = 0;

		function type() {
			if (i < text.length) {
				element.textContent += text.charAt(i);
				i++;
				setTimeout(() => requestAnimationFrame(type), speed);
			}
		}
		requestAnimationFrame(type);
	}

	// History Logic
	function getStoredHistory() {
		try {
			return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
		} catch (err) {
			console.warn("Failed to parse local roast history", err);
			return [];
		}
	}

	function persistHistory(roasts) {
		localStorage.setItem(HISTORY_KEY, JSON.stringify(roasts.slice(0, 20)));
	}

	function saveToLocalHistory(roastItem) {
		const history = getStoredHistory().filter((h) => h.id !== roastItem.id);
		history.unshift(roastItem);
		persistHistory(history);
		renderHistory(history);
	}

	function loadHistory() {
		renderHistory(getStoredHistory());
	}

	function formatHistoryInputs(inputs = {}) {
		const badges = [];
		if (inputs.spotify_name) badges.push('<span class="px-2 py-0.5 rounded bg-green-500/10 text-green-400 text-[10px] border border-green-500/20 font-mono">SPOTIFY</span>');
		if (inputs.valorant_name) badges.push('<span class="px-2 py-0.5 rounded bg-red-500/10 text-red-400 text-[10px] border border-red-500/20 font-mono">VALORANT</span>');
		if (inputs.anilist_user) badges.push('<span class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px] border border-blue-500/20 font-mono">ANILIST</span>');
		if (inputs.steam_id || inputs.steam_vanity) badges.push('<span class="px-2 py-0.5 rounded bg-slate-500/10 text-slate-400 text-[10px] border border-slate-500/20 font-mono">STEAM</span>');
	}

	function formatTimestamp(value) {
		if (!value) return "--";
		const date = new Date(value);
		if (Number.isNaN(date.getTime())) return "--";
		return date.toLocaleString("en-US", {
			month: "short",
			day: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		});
	}

	function renderHistory(roasts) {
		const latest = roasts[0];
		renderLatest(latest);

		if (!historyList) return;

		const archived = roasts.slice(1);

		if (!archived.length) {
			historyList.innerHTML = '<p class="text-slate-500 font-mono text-sm col-span-full text-center">ARCHIVE EMPTY — GENERATE MORE ROASTS TO FILL THIS GRID.</p>';
			return;
		}

		historyList.innerHTML = archived.map((r) => createHistoryCard(r)).join("");
	}

	function renderLatest(roast) {
		if (!latestCard) return;

		if (!roast) {
			latestCard.classList.add("hidden");
			latestEmpty?.classList.remove("hidden");
			latestUpdated?.classList.add("hidden");
			return;
		}

		latestCard.classList.remove("hidden");
		latestEmpty?.classList.add("hidden");

		// Update the latest card to look like history cards but bigger/highlighted
		latestCard.className = "glass-panel p-8 rounded-2xl border border-electric/20 relative overflow-hidden group hover:border-electric/50 transition-all cursor-pointer";
		latestCard.onclick = () => (window.location.href = `./view.html?id=${roast.id}`);

		const timestamp = roast.timestamp || roast.created_at;
		const formattedTime = formatTimestamp(timestamp);

		// Reconstruct inner HTML to match the style
		latestCard.innerHTML = `
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <div class="w-24 h-24 bg-electric rounded-full blur-3xl"></div>
            </div>
            <div class="relative z-10">
                <div class="flex justify-between items-start mb-6 border-b border-white/5 pb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-2 h-2 bg-electric rounded-full animate-pulse"></div>
                        <span class="font-mono text-sm text-electric tracking-widest">ROAST #${(roast.id || "").substring(0, 6)}</span>
                    </div>
                    <span class="font-mono text-xs text-slate-500">${formattedTime}</span>
                </div>
                
                <p class="font-mono text-lg text-slate-200 mb-6">${roast.roast || "ROAST PAYLOAD NOT AVAILABLE."}</p>
            </div>
        `;

		if (latestUpdated) {
			latestUpdated.classList.remove("hidden");
			latestUpdated.textContent = `Updated ${formattedTime}`;
		}
	}

	function createHistoryCard(roast) {
		const timestamp = formatTimestamp(roast.timestamp || roast.created_at);
		return `
	        <div class="glass-panel p-6 rounded-xl cursor-pointer hover:border-electric/50 transition-all group flex flex-col h-full" onclick="window.location.href='./view.html?id=${roast.id}'">
	            <div class="flex justify-between items-start mb-4 border-b border-white/5 pb-2">
	                <span class="font-mono text-xs text-electric tracking-widest">ROAST #${(roast.id || "").substring(0, 6)}</span>
	                <span class="font-mono text-xs text-slate-500">${timestamp}</span>
	            </div>
	            <p class="font-mono text-sm text-slate-400 line-clamp-3 group-hover:text-slate-200 transition-colors flex-grow mb-4">${roast.roast || "ROAST TEXT MISSING"}</p>
	        </div>
	    `;
	}

	window.loadHistoryRoast = async (id) => {
		try {
			const res = await fetch(`${API_BASE}/api/roast/${id}`, { credentials: "include" });
			const data = await res.json();

			currentRoastId = id;

			typeWriter(data.roast, roastText, 5);

			resultBox.classList.remove("hidden");
			shareUrlBox.classList.add("hidden");

			resultBox.scrollIntoView({ behavior: "smooth" });
		} catch (err) {
			console.error("Failed to load roast:", err);
		}
	};

	function handleShare() {
		if (!currentRoastId) return;

		const dir = window.location.origin + window.location.pathname.replace(/[^/]*$/, "");
		const base = (window.FRONTEND_BASE || dir).replace(/\/$/, "");
		const shareUrl = `${base}/view.html?id=${currentRoastId}`;

		shareUrlInput.value = shareUrl;
		shareUrlBox.classList.remove("hidden");
	}

	async function handleCopyUrl() {
		try {
			await navigator.clipboard.writeText(shareUrlInput.value);
			const originalText = copyUrlBtn.textContent;

			copyUrlBtn.textContent = "COPIED";

			setTimeout(() => (copyUrlBtn.textContent = originalText), 2000);
		} catch {
			shareUrlInput.select();
			document.execCommand("copy");
		}
	}
});
