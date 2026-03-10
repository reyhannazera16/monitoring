/**
 * Dashboard Controller
 * Main orchestration logic for the Air Quality Dashboard
 */

class Dashboard {
    constructor() {
        this.chartManager = new ChartManager();

        // Parameters for each location
        this.params = {
            Perkotaan: {
                historical: 'co2',
                prediction: 'co2'
            },
            Pedesaan: {
                historical: 'co2',
                prediction: 'co2'
            }
        };

        this.refreshInterval = null;
        this.init();
    }

    /**
     * Initialize dashboard
     */
    async init() {
        console.log('Initializing Dual Air Quality Dashboard...');

        // Set up event listeners
        this.setupEventListeners();

        // Load initial data (not quiet)
        await this.loadAllData(false);

        // Set up auto-refresh (every 10 seconds for realtime feel)
        this.startAutoRefresh(10000);

        console.log('Dual Dashboard initialized successfully!');
    }

    /**
     * Set up event listeners for UI controls
     */
    setupEventListeners() {
        // --- Urban Event Listeners ---
        document.getElementById('urban-historicalParameter').addEventListener('change', (e) => {
            this.params.Perkotaan.historical = e.target.value;
            this.loadHistoricalData('Perkotaan');
        });

        document.getElementById('urban-predictionParameter').addEventListener('change', (e) => {
            this.params.Perkotaan.prediction = e.target.value;
            this.loadPredictionData('Perkotaan');
        });

        // --- Rural Event Listeners ---
        const ruralHistParam = document.getElementById('rural-historicalParameter');
        if (ruralHistParam) {
            ruralHistParam.addEventListener('change', (e) => {
                this.params.Pedesaan.historical = e.target.value;
                this.loadHistoricalData('Pedesaan');
            });
        }

        document.getElementById('rural-predictionParameter').addEventListener('change', (e) => {
            this.params.Pedesaan.prediction = e.target.value;
            this.loadPredictionData('Pedesaan');
        });

        // --- Comparison & Global Listeners ---
        document.getElementById('comparisonParameter').addEventListener('change', (e) => {
            this.loadComparisonData();
        });

        document.getElementById('exportCSV').addEventListener('click', () => {
            this.exportData();
        });

        document.getElementById('trainModel').addEventListener('click', () => {
            this.trainAllModels();
        });
    }

    /**
     * Load all data for both locations
     */
    async loadAllData(isQuiet = true) {
        if (!isQuiet) this.showLoading(true);

        try {
            // Load both locations in parallel
            await Promise.all([
                this.loadLocationData('Perkotaan', isQuiet),
                this.loadLocationData('Pedesaan', isQuiet),
                this.loadComparisonData(isQuiet)
            ]);

            this.updateStatus('Connected', 'good');
        } catch (error) {
            console.error('Error loading data:', error);
            this.updateStatus('Error', 'error');
            if (!isQuiet) this.showError('Gagal memuat data dashboard.');
        } finally {
            if (!isQuiet) this.showLoading(false);
        }
    }

    /**
     * Load all components for a specific location
     */
    async loadLocationData(location, isQuiet = true) {
        return Promise.all([
            this.loadStatistics(location),
            this.loadHistoricalData(location, isQuiet),
            this.loadPredictionData(location, isQuiet),
            this.loadSurvivalAnalysis(location)
        ]);
    }

    /**
     * Load statistics for a location
     */
    async loadStatistics(location) {
        const prefix = location === 'Perkotaan' ? 'urban' : 'rural';
        try {
            const response = await APIClient.getStatistics({ location });
            if (!response || !response.statistics) return;
            const stats = response.statistics;

            document.getElementById(`${prefix}-statTotalReadings`).textContent =
                stats.total_readings?.toLocaleString() || '-';

            document.getElementById(`${prefix}-statAvgCO2`).textContent =
                (stats.avg_co2 !== null && stats.avg_co2 !== undefined) ? `${parseFloat(stats.avg_co2).toFixed(2)}` : '-';

            document.getElementById(`${prefix}-statAvgCO`).textContent =
                (stats.avg_co !== null && stats.avg_co !== undefined) ? `${parseFloat(stats.avg_co).toFixed(2)}` : '-';

        } catch (error) {
            console.error(`Error loading stats for ${location}:`, error);
        }
    }

    /**
     * Load historical data for a location
     */
    async loadHistoricalData(location, isQuiet = true) {
        const prefix = location === 'Perkotaan' ? 'urban' : 'rural';
        const chartDiv = `${prefix}-historicalChart`;
        const parameter = this.params[location].historical;

        try {
            if (!isQuiet) this.chartManager.showLoading(chartDiv);

            const response = await APIClient.getHistoricalData({
                location,
                limit: 500
            });

            if (response.data && response.data.length > 0) {
                this.chartManager.renderHistoricalChart(response.data, parameter, chartDiv);
            } else {
                console.warn(`Empty historical data for ${location}`);
                if (!isQuiet) this.chartManager.showError(chartDiv, 'Data historis tidak tersedia');
            }
        } catch (error) {
            console.error(`Error loading historical for ${location}:`, error);
            if (!isQuiet) this.chartManager.showError(chartDiv, 'Gagal memuat data (Hubungi Admin)');
        }
    }

    /**
     * Load prediction data for a location
     */
    async loadPredictionData(location, isQuiet = true) {
        const prefix = location === 'Perkotaan' ? 'urban' : 'rural';
        const chartDiv = `${prefix}-predictionChart`;
        const parameter = this.params[location].prediction;

        try {
            if (!isQuiet) this.chartManager.showLoading(chartDiv);

            const predictionRes = await APIClient.getPredictions(parameter, { location });
            const historicalRes = await APIClient.getHistoricalData({ location, limit: 50 });

            if (predictionRes.data && predictionRes.data.length > 0) {
                this.chartManager.renderPredictionChart(
                    historicalRes.data || [],
                    predictionRes.data,
                    parameter,
                    chartDiv
                );

                // Update model info
                const metadata = predictionRes.model_metadata;
                if (metadata && metadata.model_params) {
                    const infoDiv = document.getElementById(`${prefix}-modelInfo`);
                    const aic = (metadata.aic !== null && metadata.aic !== undefined) ? parseFloat(metadata.aic).toFixed(1) : '-';
                    infoDiv.innerHTML = `ARIMA(${metadata.model_params.p},${metadata.model_params.d},${metadata.model_params.q}) | AIC: ${aic}`;
                }
            } else {
                console.warn(`No predictions available for ${location} ${parameter}`);
                if (!isQuiet) this.chartManager.showError(chartDiv, 'Prediksi belum tersedia (Latih Model)');
            }
        } catch (error) {
            console.error(`Error loading prediction for ${location}:`, error);
            if (!isQuiet) this.chartManager.showError(chartDiv, 'Gagal memuat prediksi');
        }
    }

    /**
     * Load survival analysis for a location (calculated client-side from real data)
     */
    async loadSurvivalAnalysis(location) {
        const prefix = location === 'Perkotaan' ? 'urban' : 'rural';
        const locationLabel = location === 'Perkotaan' ? 'Permukiman Industri' : 'Pedesaan';
        try {
            // Fetch actual historical data
            const response = await APIClient.getHistoricalData({ location, limit: 500 });
            if (!response || !response.data || response.data.length < 2) {
                document.getElementById(`${prefix}-survivalMessage`).textContent =
                    'Data tidak cukup untuk analisis waktu bertahan.';
                return;
            }

            const data = response.data;

            // Thresholds
            const thresholds = {
                co2: { tidak_sehat: 1000, berbahaya: 5000 },
                co: { tidak_sehat: 9, berbahaya: 30 }
            };

            // Calculate current averages
            const avgCO2 = data.reduce((s, d) => s + d.co2_ppm, 0) / data.length;
            const avgCO = data.reduce((s, d) => s + d.co_ppm, 0) / data.length;

            // Linear regression: predict trend
            const calcTrend = (values) => {
                const n = values.length;
                if (n < 2) return { slope: 0, intercept: values[0] || 0 };
                let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
                for (let i = 0; i < n; i++) {
                    sumX += i;
                    sumY += values[i];
                    sumXY += i * values[i];
                    sumX2 += i * i;
                }
                const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
                const intercept = (sumY - slope * sumX) / n;
                return { slope, intercept, lastValue: intercept + slope * (n - 1) };
            };

            // Sort data chronologically
            const sorted = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            const co2Values = sorted.map(d => d.co2_ppm);
            const coValues = sorted.map(d => d.co_ppm);

            const co2Trend = calcTrend(co2Values);
            const coTrend = calcTrend(coValues);

            // Calculate average time interval between readings (in days)
            const firstTime = new Date(sorted[0].timestamp).getTime();
            const lastTime = new Date(sorted[sorted.length - 1].timestamp).getTime();
            const intervalDays = (lastTime - firstTime) / (1000 * 60 * 60 * 24) / (sorted.length - 1);

            // Project days until threshold crossing
            const projectDays = (trend, threshold, currentIdx) => {
                if (trend.lastValue >= threshold) return 0; // Already crossed
                if (trend.slope <= 0) return null; // Not rising, won't cross
                const stepsToThreshold = (threshold - trend.lastValue) / trend.slope;
                const days = Math.round(stepsToThreshold * intervalDays);
                return days > 0 ? days : null;
            };

            const lastIdx = sorted.length - 1;
            const co2DaysUnhealthy = projectDays(co2Trend, thresholds.co2.tidak_sehat, lastIdx);
            const co2DaysHazardous = projectDays(co2Trend, thresholds.co2.berbahaya, lastIdx);
            const coDaysUnhealthy = projectDays(coTrend, thresholds.co.tidak_sehat, lastIdx);
            const coDaysHazardous = projectDays(coTrend, thresholds.co.berbahaya, lastIdx);

            // Overall: earliest crossing
            const unhealthyDays = [co2DaysUnhealthy, coDaysUnhealthy].filter(d => d !== null);
            const hazardousDays = [co2DaysHazardous, coDaysHazardous].filter(d => d !== null);

            const daysUntilUnhealthy = unhealthyDays.length > 0 ? Math.min(...unhealthyDays) : null;
            const daysUntilHazardous = hazardousDays.length > 0 ? Math.min(...hazardousDays) : null;

            // Determine status
            let status = 'good';
            if (daysUntilUnhealthy === 0) status = 'critical';
            else if (daysUntilUnhealthy !== null && daysUntilUnhealthy < 30) status = 'warning';
            else if (daysUntilUnhealthy !== null && daysUntilUnhealthy < 90) status = 'caution';
            else status = 'good';

            // Generate summary message
            let summaryMessage = '';
            if (daysUntilUnhealthy === 0) {
                summaryMessage = `PERINGATAN: Kualitas udara di wilayah ${locationLabel} sudah memasuki kategori 'Tidak Sehat'. ` +
                    `Rata-rata CO₂: ${avgCO2.toFixed(1)} ppm, CO: ${avgCO.toFixed(1)} ppm. Tindakan mitigasi segera diperlukan!`;
            } else if (daysUntilUnhealthy !== null) {
                summaryMessage = `Berdasarkan tren data sensor, wilayah ${locationLabel} diperkirakan dapat mempertahankan kualitas udara 'Baik-Sedang' ` +
                    `selama ~${daysUntilUnhealthy} hari ke depan. Rata-rata CO₂: ${avgCO2.toFixed(1)} ppm, CO: ${avgCO.toFixed(1)} ppm.`;
            } else {
                summaryMessage = `Kualitas udara di wilayah ${locationLabel} terpantau stabil atau membaik. ` +
                    `Rata-rata CO₂: ${avgCO2.toFixed(1)} ppm, CO: ${avgCO.toFixed(1)} ppm. Tidak terdeteksi tren peningkatan menuju kategori 'Tidak Sehat'.`;
            }

            // Update UI
            document.getElementById(`${prefix}-survivalMessage`).textContent = summaryMessage;

            const statsDiv = document.getElementById(`${prefix}-survivalStats`);
            let html = '';
            if (daysUntilUnhealthy !== null) {
                html += `<div class="alert-stat"><span class="alert-stat-label">Ke Tidak Sehat</span><span class="alert-stat-value">${daysUntilUnhealthy === 0 ? 'Sekarang!' : daysUntilUnhealthy + ' hari'}</span></div>`;
            }
            if (daysUntilHazardous !== null) {
                html += `<div class="alert-stat"><span class="alert-stat-label">Ke Berbahaya</span><span class="alert-stat-value">${daysUntilHazardous === 0 ? 'Sekarang!' : daysUntilHazardous + ' hari'}</span></div>`;
            }
            if (!html) {
                html = '<div class="alert-stat"><span class="alert-stat-label">Status</span><span class="alert-stat-value">Aman ✓</span></div>';
            }
            statsDiv.innerHTML = html;

            const alertDiv = document.getElementById(`${prefix}-survivalAlert`);
            alertDiv.style.borderLeftWidth = '6px';
            if (status === 'critical') alertDiv.style.borderLeftColor = '#ef4444';
            else if (status === 'warning') alertDiv.style.borderLeftColor = '#f97316';
            else alertDiv.style.borderLeftColor = '#10b981';

        } catch (error) {
            console.error(`Error loading survival for ${location}:`, error);
        }
    }

    /**
     * Load comparison chart
     */
    async loadComparisonData(isQuiet = true) {
        const parameter = document.getElementById('comparisonParameter').value;
        const chartDiv = 'comparisonChart';

        try {
            if (!isQuiet) this.chartManager.showLoading(chartDiv);

            const [urbanRes, ruralRes] = await Promise.all([
                APIClient.getPredictions(parameter, { location: 'Perkotaan' }),
                APIClient.getPredictions(parameter, { location: 'Pedesaan' })
            ]);

            if (urbanRes.data && ruralRes.data) {
                this.chartManager.renderComparisonChart(urbanRes.data, ruralRes.data, parameter);
            } else {
                if (!isQuiet) this.chartManager.showError(chartDiv, 'Data prediksi perbandingan belum tersedia');
            }
        } catch (error) {
            console.error('Error loading comparison:', error);
            if (!isQuiet) this.chartManager.showError(chartDiv, 'Gagal memuat perbandingan');
        }
    }

    /**
     * Train models for all locations
     */
    async trainAllModels() {
        if (!confirm('Latih ulang semua model (Permukiman Industri & Pedesaan)?')) return;
        this.showLoading(true);
        try {
            await Promise.all([
                APIClient.trainModels({ location: 'Perkotaan' }),
                APIClient.trainModels({ location: 'Pedesaan' })
            ]);
            this.showSuccess('Semua model berhasil dilatih!');
            await this.loadAllData();
        } catch (error) {
            this.showError('Gagal melatih model');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Export all data
     */
    exportData() {
        APIClient.exportCSV({ location: 'Perkotaan' });
        setTimeout(() => APIClient.exportCSV({ location: 'Pedesaan' }), 1000);
        this.showSuccess('Mengekspor data untuk kedua wilayah...');
    }

    updateStatus(text, status = 'good') {
        const indicator = document.getElementById('statusIndicator');
        const dot = indicator.querySelector('.status-dot');
        const txt = indicator.querySelector('.status-text');
        txt.textContent = text;
        if (status === 'good') {
            indicator.style.borderColor = '#10b981';
            dot.style.background = '#10b981';
        } else {
            indicator.style.borderColor = '#ef4444';
            dot.style.background = '#ef4444';
        }
    }

    showLoading(show) {
        document.getElementById('loadingOverlay').classList.toggle('active', show);
    }

    showSuccess(m) { alert('✓ ' + m); }
    showError(m) { alert('✗ ' + m); }

    startAutoRefresh(interval) {
        if (this.refreshInterval) clearInterval(this.refreshInterval);
        this.refreshInterval = setInterval(() => this.loadAllData(), interval);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});
