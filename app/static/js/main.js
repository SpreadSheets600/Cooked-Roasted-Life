document.addEventListener("DOMContentLoaded", () => {
	const form = document.getElementById("roast-form");
	const resultBox = document.getElementById("roast-result");
	const roastText = document.getElementById("roast-text");
	const rawJson = document.getElementById("raw-json");
	const shareBtn = document.getElementById("share-btn");
	const saveBtn = document.getElementById("save-history-btn");
	const shareUrlBox = document.getElementById("share-url");
	const shareUrlInput = document.getElementById("share-url-input");
	const copyUrlBtn = document.getElementById("copy-url-btn");
	const historyList = document.getElementById("history-list");
	const submitButton = form?.querySelector('button[type="submit"]');

	let currentRoastId = null;

	loadHistory();

	const urlParams = new URLSearchParams(window.location.search);
	const sharedId = urlParams.get("share");
	if (sharedId) {
		window.location.href = `/share/${sharedId}`;
		return;
	}

	if (!form) return;

	const spotifyAuthenticated = document.querySelector('[href="/spotify/logout"]') !== null;

	function validateDataSources() {
		const valorantName = document.getElementById("valorant_name")?.value.trim();
		const valorantTag = document.getElementById("valorant_tag")?.value.trim();
		const anilistUser = document.getElementById("anilist_user")?.value.trim();
		const steamId = document.getElementById("steam_id")?.value.trim();
		const steamVanity = document.getElementById("steam_vanity")?.value.trim();

		const hasValorant = valorantName && valorantTag;
		const hasAnilist = anilistUser;
		const hasSteam = steamId || steamVanity;
		const hasSpotify = spotifyAuthenticated;

		const hasAnyData = hasValorant || hasAnilist || hasSteam || hasSpotify;

		if (submitButton) {
			if (hasAnyData) {
				submitButton.disabled = false;
				submitButton.classList.remove("opacity-50", "cursor-not-allowed");
				submitButton.classList.add("hover:bg-pink-500");
			} else {
				submitButton.disabled = true;
				submitButton.classList.add("opacity-50", "cursor-not-allowed");
				submitButton.classList.remove("hover:bg-pink-500");
			}
		}
	}

	const inputs = form.querySelectorAll("input, select");
	inputs.forEach((input) => {
		input.addEventListener("input", validateDataSources);
		input.addEventListener("change", validateDataSources);
	});

	validateDataSources();

	form.addEventListener("submit", async (e) => {
		e.preventDefault();
		roastText.textContent = "Generating...";
		resultBox.classList.remove("hidden");
		shareUrlBox.classList.add("hidden");

		const rawEntries = Object.fromEntries(new FormData(form).entries());

		const data = Object.fromEntries(
			Object.entries(rawEntries)
				.map(([k, v]) => [k, typeof v === "string" ? v.trim() : v])
				.filter(([_, v]) => v !== "" && v !== undefined && v !== null)
		);
		try {
			const res = await fetch("/api/roast", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(data),
			});
			const json = await res.json();
			currentRoastId = json.id;
			roastText.textContent = json.roast || "No roast generated.";
			rawJson.textContent = JSON.stringify(json.raw, null, 2);
		} catch (err) {
			roastText.textContent = "Error: " + err.message;
		}
	});

	shareBtn?.addEventListener("click", () => {
		if (!currentRoastId) return;
		const shareUrl = `${window.location.origin}/share/${currentRoastId}`;
		shareUrlInput.value = shareUrl;
		shareUrlBox.classList.remove("hidden");
	});

	copyUrlBtn?.addEventListener("click", async () => {
		try {
			await navigator.clipboard.writeText(shareUrlInput.value);
			copyUrlBtn.textContent = "✓ Copied!";
			setTimeout(() => (copyUrlBtn.textContent = "Copy"), 2000);
		} catch {
			shareUrlInput.select();
			document.execCommand("copy");
		}
	});

	saveBtn?.addEventListener("click", async () => {
		if (!currentRoastId) return;
		try {
			await fetch("/api/roast/save", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ id: currentRoastId }),
			});
			saveBtn.textContent = "✓ Saved!";
			setTimeout(() => (saveBtn.textContent = "💾 Save"), 2000);
			loadHistory();
		} catch (err) {
			console.error("Save failed:", err);
		}
	});

	async function loadHistory() {
		try {
			const res = await fetch("/api/roast/history");
			const data = await res.json();
			renderHistory(data.roasts || []);
		} catch (err) {
			console.error("Failed to load history:", err);
		}
	}

	function renderHistory(roasts) {
		if (!roasts.length) {
			historyList.innerHTML = '<p class="text-slate-400 text-sm">No saved roasts yet.</p>';
			return;
		}
		historyList.innerHTML = roasts
			.map(
				(r) => `
      <div class="bg-slate-800/50 p-3 rounded border border-slate-700 cursor-pointer hover:border-pink-500 transition" onclick="loadHistoryRoast('${r.id}')">
        <div class="flex justify-between items-start mb-1">
          <span class="text-sm font-medium">${formatInputs(r.inputs)}</span>
          <span class="text-xs text-slate-500">${formatDate(r.timestamp)}</span>
        </div>
        <p class="text-xs text-slate-400 line-clamp-2">${r.roast}</p>
      </div>
    `
			)
			.join("");
	}

	window.loadHistoryRoast = async (id) => {
		try {
			const res = await fetch(`/api/roast/${id}`);
			const data = await res.json();
			currentRoastId = id;
			roastText.textContent = data.roast;
			rawJson.textContent = JSON.stringify(data.raw, null, 2);
			resultBox.classList.remove("hidden");
			shareUrlBox.classList.add("hidden");
			window.scrollTo({ top: 0, behavior: "smooth" });
		} catch (err) {
			console.error("Failed to load roast:", err);
		}
	};

	async function loadSharedRoast(id) {
		await window.loadHistoryRoast(id);
	}

	function formatInputs(inputs) {
		const parts = [];
		if (inputs.valorant_name) parts.push(`🎮 ${inputs.valorant_name}#${inputs.valorant_tag}`);
		if (inputs.anilist_user) parts.push(`📺 ${inputs.anilist_user}`);
		if (inputs.steam_id || inputs.steam_vanity) parts.push(`🕹 ${inputs.steam_id || inputs.steam_vanity}`);
		return parts.join(" • ") || "Roast";
	}

	function formatDate(iso) {
		const date = new Date(iso);
		return date.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
	}
});
