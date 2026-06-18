        /**
         * Dashboard Controller
         * Main orchestration logic for the Air Quality Dashboard
         */

        class Dashboard {
            constructor() {
                this.chartManager = new ChartManager();

                // Fixed date range: 1-7 March 2026
                this.DATE_START = '2026-03-01';
                this.DATE_END   = '2026-03-07';

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
                const ruralHistoricalEl = document.getElementById('rural-historicalParameter');
                if (ruralHistoricalEl) {
                    ruralHistoricalEl.addEventListener('change', (e) => {
                        this.params.Pedesaan.historical = e.target.value;
                        this.loadHistoricalData('Pedesaan');
                    });
                }

                const ruralPredictionEl = document.getElementById('rural-predictionParameter');
                if (ruralPredictionEl) {
                    ruralPredictionEl.addEventListener('change', (e) => {
                        this.params.Pedesaan.prediction = e.target.value;
                        this.loadPredictionData('Pedesaan');
                    });
                }

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
                    const response = await APIClient.getStatistics({
                        location
                    });
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
                        start_date: this.DATE_START,
                        end_date: this.DATE_END,
                        limit: 168
                    });

                    // Filter data client-side to strictly enforce 1-7 March range
                    const startTs = new Date(this.DATE_START).getTime();
                    const endTs   = new Date(this.DATE_END + 'T23:59:59').getTime();
                    const filtered = (response.data || []).filter(d => {
                        const t = new Date(d.timestamp).getTime();
                        return t >= startTs && t <= endTs;
                    });

                    if (filtered.length > 0) {
                        this.chartManager.renderHistoricalChart(filtered, parameter, chartDiv);
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

                if (!document.getElementById(chartDiv)) {
                    return;
                }

                try {
                    if (!isQuiet) this.chartManager.showLoading(chartDiv);

                    // Historical data for selected location
                    const historicalRes = await APIClient.getHistoricalData({
                        location,
                        start_date: this.DATE_START,
                        end_date: this.DATE_END,
                        limit: 200
                    });

                    // ARIMA prediction from backend model (latest forecast horizon)
                    const predictionRes = await APIClient.getPredictions(parameter, {
                        location
                    });

                    const startTs = new Date(this.DATE_START).getTime();
                    const endTs   = new Date(this.DATE_END + 'T23:59:59').getTime();

                    // Filter historical data to fixed date range
                    const filteredHistorical = (historicalRes.data || []).filter(d => {
                        const t = new Date(d.timestamp).getTime();
                        return t >= startTs && t <= endTs;
                    });

                    const futurePredictions = (predictionRes.data || []).map(d => ({
                        prediction_date: d.prediction_date,
                        predicted_value: d.predicted_value,
                        confidence_lower: d.confidence_lower,
                        confidence_upper: d.confidence_upper
                    }));

                    // Build in-sample ARIMA-like prediction so Actual and Prediction
                    // are both visible over the same historical timeline.
                    const inSamplePredictions = this.buildInSamplePredictions(filteredHistorical, parameter);

                    const predictionMap = new Map();
                    [...inSamplePredictions, ...futurePredictions].forEach(p => {
                        predictionMap.set(p.prediction_date, p);
                    });
                    const mergedPredictions = Array.from(predictionMap.values());

                    if (mergedPredictions.length > 0) {
                        this.chartManager.renderPredictionChart(
                            filteredHistorical,
                            mergedPredictions,
                            parameter,
                            chartDiv
                        );
                    } else {
                        console.warn(`No comparison data available for ${parameter}`);
                        if (!isQuiet) this.chartManager.showError(chartDiv, 'Data tidak tersedia untuk range 1-7 Maret');
                    }
                } catch (error) {
                    console.error(`Error loading prediction for ${location}:`, error);
                    if (!isQuiet) this.chartManager.showError(chartDiv, 'Gagal memuat prediksi');
                }
            }

            /**
             * Build one-step-ahead predictions aligned with historical timestamps.
             */
            buildInSamplePredictions(historicalData, parameter) {
                const parameterKey = parameter === 'co2' ? 'co2_ppm' : 'co_ppm';
                const sorted = [...(historicalData || [])]
                    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

                if (sorted.length < 3) return [];

                const values = sorted.map(d => Number(d[parameterKey]) || 0);
                const alpha = 0.45;
                const beta = 0.20;

                let level = values[0];
                let trend = values[1] - values[0];
                const oneStep = [null];

                for (let i = 1; i < values.length; i++) {
                    oneStep.push(Math.max(0, level + trend));
                    const prevLevel = level;
                    level = (alpha * values[i]) + ((1 - alpha) * (level + trend));
                    trend = (beta * (level - prevLevel)) + ((1 - beta) * trend);
                }

                const errors = [];
                for (let i = 1; i < values.length; i++) {
                    if (oneStep[i] !== null) errors.push(values[i] - oneStep[i]);
                }
                const mean = errors.length ? (errors.reduce((s, e) => s + e, 0) / errors.length) : 0;
                const variance = errors.length > 1
                    ? errors.reduce((s, e) => s + Math.pow(e - mean, 2), 0) / (errors.length - 1)
                    : 0;
                const std = Math.sqrt(Math.max(0, variance));

                const result = [];
                for (let i = 1; i < sorted.length; i++) {
                    const pred = oneStep[i];
                    if (pred === null) continue;
                    const spread = 1.96 * std;
                    result.push({
                        prediction_date: sorted[i].timestamp,
                        predicted_value: Number(pred.toFixed(2)),
                        confidence_lower: Number(Math.max(0, pred - spread).toFixed(2)),
                        confidence_upper: Number((pred + spread).toFixed(2))
                    });
                }

                return result;
            }

            /**
             * Load survival analysis for a location (calculated client-side from real data)
             */
            async loadSurvivalAnalysis(location) {
                const prefix = location === 'Perkotaan' ? 'urban' : 'rural';
                const locationLabel = location === 'Perkotaan' ? 'Permukiman Industri' : 'Permukiman Industri Prediksi ARIMA';
                try {
                    // Fetch actual historical data (strictly 1-7 March)
                    const response = await APIClient.getHistoricalData({
                        location,
                        start_date: this.DATE_START,
                        end_date: this.DATE_END,
                        limit: 168
                    });
                    if (!response || !response.data || response.data.length < 2) {
                        document.getElementById(`${prefix}-survivalMessage`).textContent =
                            'Data tidak cukup untuk analisis waktu bertahan.';
                        return;
                    }

                    const data = response.data;

                    // Thresholds
                    const thresholds = {
                        co2: { tidak_sehat: 1000 },
                        co: { tidak_sehat: 9 }
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
                    const coDaysUnhealthy = projectDays(coTrend, thresholds.co.tidak_sehat, lastIdx);

                    // Overall: earliest crossing
                    const unhealthyDays = [co2DaysUnhealthy, coDaysUnhealthy].filter(d => d !== null);

                    const daysUntilUnhealthy = unhealthyDays.length > 0 ? Math.min(...unhealthyDays) : null;

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

                    // Fetch historical data for both locations (1-7 March)
                    const [urbanRes, ruralRes] = await Promise.all([
                        APIClient.getHistoricalData({ location: 'Perkotaan', start_date: this.DATE_START, end_date: this.DATE_END, limit: 1000 }),
                        APIClient.getHistoricalData({ location: 'Pedesaan', start_date: this.DATE_START, end_date: this.DATE_END, limit: 1000 })
                    ]);

                    const startTs = new Date(this.DATE_START).getTime();
                    const endTs   = new Date(this.DATE_END + 'T23:59:59').getTime();
                    
                    const mapHistoricalToPred = (arr) => (arr || []).filter(d => {
                        const t = new Date(d.timestamp).getTime();
                        return t >= startTs && t <= endTs;
                    }).map(d => ({
                        prediction_date: d.timestamp,
                        predicted_value: parameter === 'co2' ? d.co2_ppm : d.co_ppm
                    }));

                    const urbanFiltered = mapHistoricalToPred(urbanRes.data);
                    const ruralFiltered = mapHistoricalToPred(ruralRes.data);

                    if (urbanFiltered.length > 0 && ruralFiltered.length > 0) {
                        this.chartManager.renderComparisonChart(urbanFiltered, ruralFiltered, parameter);
                    } else {
                        if (!isQuiet) this.chartManager.showError(chartDiv, 'Data perbandingan tidak tersedia untuk range 1-7 Maret');
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
                if (!confirm('Latih ulang semua model (Permukiman Industri & Permukiman Industri Prediksi ARIMA)?')) return;
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
             * Export all data - 1 file Excel dengan 2 sheet (CO2 dan CO)
             */
            exportData() {
                APIClient.exportCSV({}, 'Laporan_Kualitas_Udara.xlsx');
                this.showSuccess('Mengekspor laporan Excel (CO2 & CO)...');
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
