// Quantum AI Training Dashboard - Frontend Logic

let currentSessionId = null
let lastActionSessionId = null
let statusUpdateInterval = null
let lossChart = null
let accuracyChart = null
let circuitCanvas = null
let circuitCtx = null
let particleInterval = null
let datasetCatalog = []
let lastSelectedResultFilename = null

// API Base URL
const API_BASE = window.location.origin

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Quantum AI Dashboard initializing...")
    initializeCircuitCanvas()
    initializeCharts()
    loadDatasets()
    loadResults()
    refreshDashboardSummary()
    setupEventListeners()
})

// Setup Event Listeners
function setupEventListeners() {
    document
        .getElementById("start-training-btn")
        .addEventListener("click", startTraining)
    document
        .getElementById("stop-training-btn")
        .addEventListener("click", stopTraining)
    document
        .getElementById("evaluate-btn")
        .addEventListener("click", evaluateNow)
    document
        .getElementById("export-metrics-btn")
        .addEventListener("click", exportMetrics)
    document
        .getElementById("dataset-select")
        .addEventListener("change", updateDatasetInfo)

    // Add input validation
    const numericInputs = [
        "n-qubits",
        "n-layers",
        "learning-rate",
        "duration",
        "batch-size",
        "early-stopping",
        "checkpoint-every",
        "warmup-epochs",
        "max-grad-norm",
    ]
    numericInputs.forEach(id => {
        const input = document.getElementById(id)
        input.addEventListener("input", () => validateInput(input))
    })
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;")
}

function formatPercent(value) {
    return `${(value * 100).toFixed(2)}%`
}

function formatElapsed(seconds) {
    if (!Number.isFinite(seconds) || seconds < 0) {
        return "Unavailable"
    }

    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = Math.floor(seconds % 60)

    if (hours > 0) {
        return `${hours}h ${minutes}m`
    }

    if (minutes > 0) {
        return `${minutes}m ${remainingSeconds}s`
    }

    return `${remainingSeconds}s`
}

function getSessionActionTarget() {
    return currentSessionId || lastActionSessionId
}

async function refreshDashboardSummary() {
    try {
        const [healthResponse, statsResponse] = await Promise.all([
            fetch(`${API_BASE}/api/health`),
            fetch(`${API_BASE}/api/stats`),
        ])

        if (!healthResponse.ok || !statsResponse.ok) {
            throw new Error("Dashboard summary endpoints are unavailable")
        }

        const health = await healthResponse.json()
        const stats = await statsResponse.json()
        updateSystemStatus(health)
        updateOverviewCards(stats)
    } catch (error) {
        console.error("Error refreshing dashboard summary:", error)
        updateSystemStatus(null, error)
    }
}

function updateSystemStatus(health, error = null) {
    const badge = document.getElementById("system-status-badge")
    const label = document.getElementById("system-status-text")

    badge.classList.remove("degraded", "error")

    if (error || !health) {
        badge.classList.add("error")
        label.textContent = "API status unavailable"
        return
    }

    const activeSessions = health.active_sessions ?? 0
    if (health.status !== "healthy") {
        badge.classList.add("degraded")
        label.textContent = `Status: ${health.status}`
        return
    }

    label.textContent =
        activeSessions > 0
            ? `Healthy • ${activeSessions} active session${activeSessions === 1 ? "" : "s"}`
            : "Healthy • Ready for training"
}

function updateOverviewCards(stats) {
    document.getElementById("overview-datasets").textContent =
        datasetCatalog.length || "--"
    document.getElementById("overview-datasets-meta").textContent =
        datasetCatalog.length
            ? `${datasetCatalog
                  .map(dataset => dataset.name)
                  .slice(0, 3)
                  .join(", ")}${datasetCatalog.length > 3 ? "…" : ""}`
            : "No datasets discovered yet"

    document.getElementById("overview-active-sessions").textContent =
        stats.active_sessions ?? 0
    document.getElementById("overview-active-meta").textContent =
        `${stats.total_sessions ?? 0} total session${stats.total_sessions === 1 ? "" : "s"} tracked`

    document.getElementById("overview-completed-sessions").textContent =
        stats.completed_sessions ?? 0
    document.getElementById("overview-completed-meta").textContent =
        `${Math.round(stats.total_epochs_trained ?? 0)} total epochs processed`

    document.getElementById("overview-average-accuracy").textContent =
        Number.isFinite(stats.average_best_accuracy)
            ? formatPercent(stats.average_best_accuracy)
            : "--"
    document.getElementById("overview-uptime").textContent =
        `Uptime ${formatElapsed(stats.server_uptime ?? 0)}`
}

// Initialize Circuit Canvas
function initializeCircuitCanvas() {
    circuitCanvas = document.getElementById("circuit-canvas")
    circuitCtx = circuitCanvas.getContext("2d")

    // Set canvas size
    const rect = circuitCanvas.getBoundingClientRect()
    circuitCanvas.width = rect.width
    circuitCanvas.height = 300

    drawIdleCircuit()
}

// Draw idle circuit state
function drawIdleCircuit() {
    if (!circuitCtx) return

    const ctx = circuitCtx
    const width = circuitCanvas.width
    const height = circuitCanvas.height

    ctx.clearRect(0, 0, width, height)

    // Draw gradient background
    const gradient = ctx.createLinearGradient(0, 0, width, height)
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.1)")
    gradient.addColorStop(1, "rgba(139, 92, 246, 0.1)")
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)

    // Draw placeholder text
    ctx.font = 'bold 18px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'
    ctx.fillStyle = "#6366f1"
    ctx.textAlign = "center"
    ctx.fillText("⚛️ Quantum Circuit Visualization", width / 2, height / 2 - 15)

    ctx.font = '14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'
    ctx.fillStyle = "#94a3b8"
    ctx.fillText(
        "Start training to see live circuit diagram",
        width / 2,
        height / 2 + 15,
    )

    // Update stats
    document.getElementById("gate-count").textContent = "0"
    document.getElementById("circuit-depth").textContent = "0"
}

// Draw active quantum circuit
function drawQuantumCircuit(nQubits, nLayers, epoch) {
    if (!circuitCtx) return

    const ctx = circuitCtx
    const width = circuitCanvas.width
    const height = circuitCanvas.height

    ctx.clearRect(0, 0, width, height)

    // Background
    const gradient = ctx.createLinearGradient(0, 0, width, height)
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.05)")
    gradient.addColorStop(1, "rgba(139, 92, 246, 0.05)")
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)

    const padding = 60
    const qubitSpacing = (height - 2 * padding) / (nQubits - 1 || 1)
    const layerWidth = (width - 2 * padding) / (nLayers + 2)

    // Draw qubit lines
    ctx.strokeStyle = "#475569"
    ctx.lineWidth = 2
    for (let i = 0; i < nQubits; i++) {
        const y = padding + i * qubitSpacing
        ctx.beginPath()
        ctx.moveTo(padding, y)
        ctx.lineTo(width - padding, y)
        ctx.stroke()

        // Qubit label
        ctx.fillStyle = "#cbd5e1"
        ctx.font = "14px monospace"
        ctx.textAlign = "right"
        ctx.fillText(`|q${i}⟩`, padding - 10, y + 5)
    }

    // Animate based on epoch
    const pulsePhase = (epoch % 10) / 10

    // Draw gates with animation
    for (let layer = 0; layer < nLayers; layer++) {
        const x = padding + (layer + 1) * layerWidth

        for (let i = 0; i < nQubits; i++) {
            const y = padding + i * qubitSpacing

            // Rotation gate (pulsing)
            const gateSize = 25 + Math.sin(pulsePhase * Math.PI * 2) * 3
            ctx.fillStyle = `rgba(239, 68, 68, ${0.7 + Math.sin(pulsePhase * Math.PI * 2) * 0.3})`
            ctx.beginPath()
            ctx.arc(x, y, gateSize / 2, 0, Math.PI * 2)
            ctx.fill()

            // Gate label
            ctx.fillStyle = "#fff"
            ctx.font = "bold 11px monospace"
            ctx.textAlign = "center"
            ctx.fillText("Ry", x, y + 4)
        }

        // CNOT gates (entanglement)
        if (nQubits > 1) {
            const cnotX = x + layerWidth / 2
            ctx.strokeStyle = `rgba(16, 185, 129, ${0.7 + Math.sin(pulsePhase * Math.PI * 2 + Math.PI) * 0.3})`
            ctx.lineWidth = 3

            for (let i = 0; i < nQubits - 1; i++) {
                const y1 = padding + i * qubitSpacing
                const y2 = padding + (i + 1) * qubitSpacing

                // Vertical line
                ctx.beginPath()
                ctx.moveTo(cnotX, y1)
                ctx.lineTo(cnotX, y2)
                ctx.stroke()

                // Control dot
                ctx.fillStyle = "#10b981"
                ctx.beginPath()
                ctx.arc(cnotX, y1, 5, 0, Math.PI * 2)
                ctx.fill()

                // Target circle
                ctx.strokeStyle = "#10b981"
                ctx.lineWidth = 2
                ctx.beginPath()
                ctx.arc(cnotX, y2, 12, 0, Math.PI * 2)
                ctx.stroke()
                ctx.beginPath()
                ctx.moveTo(cnotX - 8, y2)
                ctx.lineTo(cnotX + 8, y2)
                ctx.stroke()
                ctx.beginPath()
                ctx.moveTo(cnotX, y2 - 8)
                ctx.lineTo(cnotX, y2 + 8)
                ctx.stroke()
            }
        }
    }

    // Measurement symbols
    const measX = width - padding - 20
    for (let i = 0; i < nQubits; i++) {
        const y = padding + i * qubitSpacing

        // Measurement box
        ctx.strokeStyle = "#f59e0b"
        ctx.lineWidth = 2
        ctx.strokeRect(measX - 15, y - 15, 30, 30)

        // Meter symbol
        ctx.beginPath()
        ctx.arc(measX, y + 5, 10, Math.PI, 0)
        ctx.stroke()
        ctx.beginPath()
        ctx.moveTo(measX, y + 5)
        ctx.lineTo(measX + 7, y - 2)
        ctx.stroke()
    }

    // Epoch indicator with glow
    ctx.save()
    ctx.shadowColor = "#6366f1"
    ctx.shadowBlur = 10
    ctx.fillStyle = "#6366f1"
    ctx.font = "bold 16px monospace"
    ctx.textAlign = "left"
    ctx.fillText(`EPOCH ${epoch}`, 15, 25)
    ctx.restore()

    // Update circuit stats
    const gateCount = nQubits * nLayers + (nQubits - 1) * nLayers
    const circuitDepth = nLayers * 2
    document.getElementById("gate-count").textContent = gateCount
    document.getElementById("circuit-depth").textContent = circuitDepth
}

// Create particle effect
function createParticle(x, y) {
    const particle = document.createElement("div")
    particle.className = "particle"
    particle.style.left = x + "px"
    particle.style.top = y + "px"
    particle.style.background = `hsl(${Math.random() * 60 + 200}, 70%, 60%)`
    document.body.appendChild(particle)

    setTimeout(() => particle.remove(), 2000)
}

// Start particle animation
function startParticleAnimation() {
    if (particleInterval) return

    particleInterval = setInterval(() => {
        const canvas = document.getElementById("circuit-canvas")
        if (!canvas) return

        const rect = canvas.getBoundingClientRect()
        const x = rect.left + Math.random() * rect.width
        const y = rect.top + Math.random() * rect.height
        createParticle(x, y)
    }, 300)
}

// Stop particle animation
function stopParticleAnimation() {
    if (particleInterval) {
        clearInterval(particleInterval)
        particleInterval = null
    }
}

// Initialize Charts
function initializeCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: "#cbd5e1",
                },
            },
        },
        scales: {
            x: {
                ticks: { color: "#94a3b8" },
                grid: { color: "#334155" },
            },
            y: {
                ticks: { color: "#94a3b8" },
                grid: { color: "#334155" },
            },
        },
    }

    // Loss Chart
    const lossCtx = document.getElementById("loss-chart").getContext("2d")
    lossChart = new Chart(lossCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Training Loss",
                    data: [],
                    borderColor: "#ef4444",
                    backgroundColor: "rgba(239, 68, 68, 0.1)",
                    tension: 0.4,
                },
                {
                    label: "Validation Loss",
                    data: [],
                    borderColor: "#f59e0b",
                    backgroundColor: "rgba(245, 158, 11, 0.1)",
                    tension: 0.4,
                },
            ],
        },
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                title: {
                    display: true,
                    text: "Training & Validation Loss",
                    color: "#cbd5e1",
                },
            },
        },
    })

    // Accuracy Chart
    const accCtx = document.getElementById("accuracy-chart").getContext("2d")
    accuracyChart = new Chart(accCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Validation Accuracy",
                    data: [],
                    borderColor: "#10b981",
                    backgroundColor: "rgba(16, 185, 129, 0.1)",
                    tension: 0.4,
                    fill: true,
                },
            ],
        },
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                title: {
                    display: true,
                    text: "Validation Accuracy",
                    color: "#cbd5e1",
                },
            },
            scales: {
                ...chartOptions.scales,
                y: {
                    ...chartOptions.scales.y,
                    min: 0,
                    max: 1,
                    ticks: {
                        ...chartOptions.scales.y.ticks,
                        callback: function (value) {
                            return (value * 100).toFixed(0) + "%"
                        },
                    },
                },
            },
        },
    })
}

// Load Available Datasets
async function loadDatasets() {
    try {
        const response = await fetch(`${API_BASE}/api/datasets`)
        if (!response.ok) {
            throw new Error("Dataset request failed")
        }
        const datasets = await response.json()
        datasetCatalog = datasets

        const select = document.getElementById("dataset-select")
        select.innerHTML = '<option value="">Select a dataset...</option>'

        datasets.forEach(dataset => {
            const option = document.createElement("option")
            option.value = dataset.name
            option.textContent = `${dataset.name} (${dataset.features} features)`
            select.appendChild(option)
        })

        console.log(`✅ Loaded ${datasets.length} datasets`)
        updateDatasetInfo()
        refreshDashboardSummary()
    } catch (error) {
        console.error("Error loading datasets:", error)
        showError("Failed to load datasets")
    }
}

// Update Dataset Info
function updateDatasetInfo() {
    const select = document.getElementById("dataset-select")
    const infoDiv = document.getElementById("dataset-info")
    const guidanceCard = document.getElementById("dataset-guidance")
    const guidanceText = document.getElementById("dataset-guidance-text")
    const selectedDataset = datasetCatalog.find(
        dataset => dataset.name === select.value,
    )

    if (selectedDataset) {
        const recommendedQubits = Math.min(
            Math.max(2, selectedDataset.features),
            8,
        )
        const recommendedLayers = selectedDataset.features > 20 ? 3 : 2
        const recommendedBatchSize = selectedDataset.features > 20 ? 16 : 32

        infoDiv.textContent = `${selectedDataset.name} • ${selectedDataset.features} input features • ${selectedDataset.exists ? "dataset ready" : "dataset missing"}`
        guidanceText.textContent = `Start with ${recommendedQubits} qubits, ${recommendedLayers} layers, and batch size ${recommendedBatchSize} to match this dataset's feature count without over-sizing the circuit.`
        guidanceCard.hidden = false
    } else {
        infoDiv.textContent = ""
        guidanceText.textContent = ""
        guidanceCard.hidden = true
    }
}

// Start Training
async function startTraining() {
    const dataset = document.getElementById("dataset-select").value

    if (!dataset) {
        showError("Please select a dataset before starting training.")
        return
    }

    const config = {
        dataset: dataset,
        n_qubits: parseInt(document.getElementById("n-qubits").value),
        n_layers: parseInt(document.getElementById("n-layers").value),
        learning_rate: parseFloat(
            document.getElementById("learning-rate").value,
        ),
        duration_minutes: parseInt(document.getElementById("duration").value),
        batch_size: parseInt(document.getElementById("batch-size").value),
        optimizer: document.getElementById("optimizer-select").value,
        early_stopping_patience: parseInt(
            document.getElementById("early-stopping").value,
        ),
        checkpoint_every: parseInt(
            document.getElementById("checkpoint-every").value,
        ),
        use_parameter_shift: document.getElementById("use-param-shift").checked,
        use_warmup: document.getElementById("use-warmup").checked,
        warmup_epochs: parseInt(document.getElementById("warmup-epochs").value),
        use_lr_decay: document.getElementById("use-lr-decay").checked,
        use_gradient_clipping: document.getElementById("use-grad-clip").checked,
        max_grad_norm: parseFloat(
            document.getElementById("max-grad-norm").value,
        ),
    }

    console.log("🚀 Starting training with config:", config)

    try {
        const response = await fetch(`${API_BASE}/api/train/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(config),
        })

        if (!response.ok) {
            const errorPayload = await response.json().catch(() => ({}))
            throw new Error(errorPayload.error || "Failed to start training")
        }

        const result = await response.json()
        currentSessionId = result.session_id
        lastActionSessionId = result.session_id

        // Update UI
        document.getElementById("start-training-btn").disabled = true
        document.getElementById("stop-training-btn").disabled = false
        document.getElementById("status-idle").style.display = "none"
        document.getElementById("status-training").style.display = "block"
        document.getElementById("progress-container").style.display = "block"
        document.getElementById("evaluation-section").style.display = "none"
        document.getElementById("evaluate-btn").disabled = true

        // Start visual effects
        const nQubits = parseInt(document.getElementById("n-qubits").value)
        const nLayers = parseInt(document.getElementById("n-layers").value)
        drawQuantumCircuit(nQubits, nLayers, 0)
        startParticleAnimation()

        // Start polling for updates
        startStatusPolling()

        console.log(`✅ Training started: ${currentSessionId}`)
        showSuccess(`Training started for ${dataset}.`)
        refreshDashboardSummary()
    } catch (error) {
        console.error("Error starting training:", error)
        showError(error.message || "Failed to start training")
    }
}

// Stop Training
async function stopTraining() {
    if (!currentSessionId) return

    try {
        await fetch(`${API_BASE}/api/train/stop/${currentSessionId}`, {
            method: "POST",
        })

        stopStatusPolling()
        showSuccess("Training stop requested.")
        refreshDashboardSummary()
        console.log("⏹️ Training stopped")
    } catch (error) {
        console.error("Error stopping training:", error)
        showError("Failed to stop training")
    }
}

// Start Status Polling
function startStatusPolling() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval)
    }

    statusUpdateInterval = setInterval(updateTrainingStatus, 1000)
}

// Stop Status Polling
function stopStatusPolling(options = {}) {
    const { preserveSessionId = false, allowPostTrainingActions = false } =
        options

    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval)
        statusUpdateInterval = null
    }

    // Stop visual effects
    stopParticleAnimation()
    drawIdleCircuit()

    // Reset UI
    document.getElementById("start-training-btn").disabled = false
    document.getElementById("stop-training-btn").disabled = true
    document.getElementById("status-idle").style.display = "block"
    document.getElementById("status-training").style.display = "none"
    document.getElementById("progress-container").style.display = "none"
    document.getElementById("evaluate-btn").disabled = !allowPostTrainingActions
    document.getElementById("evaluation-section").style.display = "none"
    document.getElementById("export-metrics-btn").disabled =
        !allowPostTrainingActions

    if (!preserveSessionId) {
        currentSessionId = null
    }

    loadResults() // Refresh results list
}

// Update Training Status
async function updateTrainingStatus() {
    if (!currentSessionId) return

    try {
        const response = await fetch(
            `${API_BASE}/api/train/status/${currentSessionId}`,
        )
        const status = await response.json()

        // Update status text
        document.getElementById("status-text").textContent = status.status
        document.getElementById("current-epoch").textContent =
            status.current_epoch
        document.getElementById("current-loss").textContent = Number.isFinite(
            status.current_loss,
        )
            ? status.current_loss.toFixed(4)
            : "-"
        document.getElementById("best-val-acc").textContent = formatPercent(
            status.best_val_acc || 0,
        )

        // Update performance metrics
        if (status.epochs_per_second > 0) {
            document.getElementById("training-speed").textContent =
                status.epochs_per_second.toFixed(2) + " ep/s"
        }

        if (status.eta_seconds) {
            const etaMinutes = Math.floor(status.eta_seconds / 60)
            const etaSeconds = Math.floor(status.eta_seconds % 60)
            document.getElementById("eta-time").textContent =
                `${etaMinutes}:${etaSeconds.toString().padStart(2, "0")}`
        } else {
            document.getElementById("eta-time").textContent = "-"
        }

        // Enable export button when training has data
        if (status.metrics && status.metrics.epochs.length > 0) {
            document.getElementById("export-metrics-btn").disabled = false
        }

        // Update elapsed time
        if (status.elapsed_time) {
            const minutes = Math.floor(status.elapsed_time / 60)
            const seconds = Math.floor(status.elapsed_time % 60)
            document.getElementById("elapsed-time").textContent =
                `${minutes}:${seconds.toString().padStart(2, "0")}`

            // Update progress bar
            const configDuration =
                parseInt(document.getElementById("duration").value) * 60
            const progress = Math.min(
                (status.elapsed_time / configDuration) * 100,
                100,
            )
            document.getElementById("progress-fill").style.width =
                progress + "%"
            document.getElementById("progress-text").textContent =
                progress.toFixed(0) + "% complete"
        }

        // Update visual accuracy bar
        const accuracy = status.best_val_acc * 100
        document.getElementById("accuracy-bar").style.width = accuracy + "%"
        document.getElementById("accuracy-percent").textContent =
            accuracy.toFixed(1) + "%"

        // Update circuit visualization
        const nQubits = parseInt(document.getElementById("n-qubits").value)
        const nLayers = parseInt(document.getElementById("n-layers").value)
        drawQuantumCircuit(nQubits, nLayers, status.current_epoch)

        // Update charts
        if (status.metrics && status.metrics.epochs.length > 0) {
            updateCharts(status.metrics)
        }

        // Check if completed
        if (
            status.status === "completed" ||
            status.status === "early_stopped" ||
            status.status === "error" ||
            status.status === "stopped"
        ) {
            const completedSuccessfully =
                status.status === "completed" ||
                status.status === "early_stopped"
            stopStatusPolling({
                preserveSessionId: completedSuccessfully,
                allowPostTrainingActions: completedSuccessfully,
            })

            if (completedSuccessfully) {
                showSuccess("Training completed successfully!")
                // Auto-evaluate if checkpoint exists
                if (status.checkpoint_path) {
                    evaluateNow()
                }
            } else if (status.status === "error") {
                showError(
                    "Training failed: " +
                        (status.error_message || "Unknown error"),
                )
            }

            refreshDashboardSummary()
        }
    } catch (error) {
        console.error("Error updating status:", error)
    }
}

// Update Charts with New Data
function updateCharts(metrics) {
    // Loss Chart
    lossChart.data.labels = metrics.epochs
    lossChart.data.datasets[0].data = metrics.train_loss
    lossChart.data.datasets[1].data = metrics.val_loss
    lossChart.update("none") // Update without animation for smoothness

    // Accuracy Chart
    accuracyChart.data.labels = metrics.epochs
    accuracyChart.data.datasets[0].data = metrics.val_accuracy
    accuracyChart.update("none")
}

// Load Training Results
async function loadResults() {
    try {
        const response = await fetch(`${API_BASE}/api/results`)
        if (!response.ok) {
            throw new Error("Results request failed")
        }
        const results = await response.json()

        const resultsDiv = document.getElementById("results-list")

        if (results.length === 0) {
            resultsDiv.innerHTML =
                '<p class="info-text">No training sessions yet. Start training to see results here.</p>'
            return
        }

        resultsDiv.innerHTML = ""

        results.forEach(result => {
            const item = document.createElement("div")
            item.className = "result-item"
            item.dataset.filename = result.filename
            item.onclick = () => viewResultDetails(result.filename)

            item.innerHTML = `
                <div class="result-header">
                    <div class="result-title">${escapeHtml(result.dataset)}</div>
                    <div class="result-badge success">${(result.best_acc * 100).toFixed(2)}% acc</div>
                </div>
                <div class="result-meta">
                    <span>📅 ${escapeHtml(result.timestamp.join("_"))}</span>
                    <span>🔄 ${result.epochs} epochs</span>
                </div>
            `

            resultsDiv.appendChild(item)
        })

        console.log(`✅ Loaded ${results.length} training results`)
        refreshDashboardSummary()

        const preferredResult =
            results.find(
                result => result.filename === lastSelectedResultFilename,
            ) || results[0]
        if (preferredResult) {
            viewResultDetails(preferredResult.filename, { quiet: true })
        }
    } catch (error) {
        console.error("Error loading results:", error)
        showError("Failed to load saved results")
    }
}

// Input Validation
function validateInput(input) {
    const errorDiv = document.getElementById("validation-error")
    const value = parseFloat(input.value)
    let error = null

    switch (input.id) {
        case "n-qubits":
            if (value < 1 || value > 10)
                error = "Qubits must be between 1 and 10"
            break
        case "n-layers":
            if (value < 1 || value > 20)
                error = "Layers must be between 1 and 20"
            break
        case "learning-rate":
            if (value <= 0 || value > 1)
                error = "Learning rate must be between 0 and 1"
            break
        case "duration":
            if (value < 1 || value > 120)
                error = "Duration must be between 1 and 120 minutes"
            break
        case "batch-size":
            if (value < 8 || value > 128)
                error = "Batch size must be between 8 and 128"
            break
    }

    if (error) {
        input.classList.add("invalid")
        errorDiv.textContent = error
        errorDiv.style.display = "block"
        document.getElementById("start-training-btn").disabled = true
    } else {
        input.classList.remove("invalid")
        errorDiv.style.display = "none"
        document.getElementById("start-training-btn").disabled = false
    }
}

// Export Metrics
async function exportMetrics() {
    const sessionId = getSessionActionTarget()
    if (!sessionId) {
        showError("No session available to export.")
        return
    }

    try {
        const response = await fetch(
            `${API_BASE}/api/export/metrics/${sessionId}`,
        )
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}))
            throw new Error(payload.error || "Failed to export metrics")
        }
        const blob = await response.blob()

        // Create download link
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `metrics_${sessionId}.csv`
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)

        showSuccess("Metrics exported successfully!")
    } catch (error) {
        console.error("Error exporting metrics:", error)
        showError("Failed to export metrics")
    }
}

// Evaluation
async function evaluateNow() {
    const sessionId = getSessionActionTarget()
    if (!sessionId) {
        showError("No completed session available to evaluate.")
        return
    }
    try {
        const res = await fetch(`${API_BASE}/api/train/evaluate/${sessionId}`)
        const data = await res.json()
        if (data.error) {
            showError("Evaluation failed: " + data.error)
            return
        }
        renderEvaluation(data)
        showSuccess("Evaluation complete")
    } catch (e) {
        console.error("Evaluation error", e)
        showError("Failed to evaluate")
    }
}

function renderEvaluation(result) {
    const section = document.getElementById("evaluation-section")
    const metricsDiv = document.getElementById("eval-metrics")
    const cmDiv = document.getElementById("confusion-matrix")
    section.style.display = "block"

    const m = result.metrics
    metricsDiv.innerHTML = `
        Accuracy: <b>${(m.accuracy * 100).toFixed(2)}%</b> ·
        Precision: <b>${(m.precision * 100).toFixed(2)}%</b> ·
        Recall: <b>${(m.recall * 100).toFixed(2)}%</b> ·
        F1: <b>${(m.f1 * 100).toFixed(2)}%</b>
        ${m.roc_auc !== null ? ` · ROC AUC: <b>${m.roc_auc.toFixed(3)}</b>` : ""}
    `
    renderConfusionMatrix(cmDiv, result.confusion_matrix, result.labels)
}

function renderConfusionMatrix(container, matrix, labels) {
    if (!matrix || !matrix.length) {
        container.innerHTML =
            '<p class="info-text">No confusion matrix available.</p>'
        return
    }
    const n = matrix.length
    let html = '<table class="cm-table"><thead><tr><th></th>'
    for (let j = 0; j < n; j++) html += `<th>Pred ${labels[j] ?? j}</th>`
    html += "</tr></thead><tbody>"
    for (let i = 0; i < n; i++) {
        html += `<tr><th>True ${labels[i] ?? i}</th>`
        for (let j = 0; j < n; j++) html += `<td>${matrix[i][j]}</td>`
        html += "</tr>"
    }
    html += "</tbody></table>"
    container.innerHTML = html
}

// View Result Details
function markActiveResult(filename) {
    document.querySelectorAll(".result-item").forEach(item => {
        item.classList.toggle("active", item.dataset.filename === filename)
    })
}

function renderResultDetails(data) {
    const details = document.getElementById("result-details")
    const config = data.config || {}
    const detailRows = [
        ["Dataset", config.dataset || "Unknown"],
        ["Qubits", config.n_qubits ?? "—"],
        ["Layers", config.n_layers ?? "—"],
        ["Learning rate", config.learning_rate ?? "—"],
        ["Batch size", config.batch_size ?? "—"],
        ["Optimizer", config.optimizer || "adam"],
    ]

    details.innerHTML = `
        <div class="details-section">
            <h3>${escapeHtml(config.dataset || "Training Run")}</h3>
            <p>Inspect the best checkpoint and configuration without leaving the dashboard.</p>
            <div class="details-grid">
                <div class="details-metric">
                    <span>Best validation accuracy</span>
                    <strong>${formatPercent(data.best_val_acc || 0)}</strong>
                </div>
                <div class="details-metric">
                    <span>Total epochs</span>
                    <strong>${data.total_epochs ?? 0}</strong>
                </div>
                <div class="details-metric">
                    <span>Current status</span>
                    <strong>${escapeHtml(data.status || "completed")}</strong>
                </div>
                <div class="details-metric">
                    <span>Checkpoint</span>
                    <strong>${data.checkpoint_path ? "Available" : "Not saved"}</strong>
                </div>
            </div>
            <div class="details-config">
                ${detailRows
                    .map(
                        ([label, value]) => `
                    <div class="details-config-item">
                        <span>${escapeHtml(label)}</span>
                        <strong>${escapeHtml(value)}</strong>
                    </div>
                `,
                    )
                    .join("")}
            </div>
        </div>
    `
}

async function viewResultDetails(filename, options = {}) {
    const { quiet = false } = options
    try {
        const response = await fetch(`${API_BASE}/api/results/${filename}`)
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}))
            throw new Error(payload.error || "Failed to load result details")
        }
        const data = await response.json()

        console.log("📊 Result details:", data)

        // Update charts with historical data
        if (data.metrics) {
            updateCharts(data.metrics)
        }

        renderResultDetails(data)
        lastSelectedResultFilename = filename
        markActiveResult(filename)
        lastActionSessionId = data.session_id || lastActionSessionId

        if (!quiet) {
            showToast(
                "info",
                "Loaded run details",
                `Showing metrics for ${data.config?.dataset || "saved run"}.`,
            )
        }
    } catch (error) {
        console.error("Error loading result details:", error)
        showError(error.message || "Failed to load result details")
    }
}

function showToast(type, title, message) {
    const container = document.getElementById("toast-container")
    if (!container) {
        return
    }

    const toast = document.createElement("div")
    toast.className = `toast ${type}`
    toast.innerHTML = `
        <span class="toast-title">${escapeHtml(title)}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
    `
    container.appendChild(toast)

    setTimeout(() => {
        toast.remove()
    }, 3500)
}

// Show Success Message
function showSuccess(message) {
    console.log("✅", message)
    showToast("success", "Success", message)
}

// Show Error Message
function showError(message) {
    console.error("❌", message)
    showToast("error", "Error", message)
}
