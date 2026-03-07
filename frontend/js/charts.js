/**
 * Chart Rendering Module
 * Handles Plotly.js chart creation and updates
 */

class ChartManager {
    constructor() {
        this.historicalChartDiv = 'historicalChart';
        this.predictionChartDiv = 'predictionChart';

        // Air quality color mapping
        this.colorMap = {
            'baik': '#10b981',
            'sedang': '#fbbf24',
            'tidak_sehat': '#f97316',
            'sangat_tidak_sehat': '#ef4444',
            'berbahaya': '#a855f7'
        };

        // Common layout settings
        this.commonLayout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(30, 41, 59, 0.5)',
            font: {
                family: 'Inter, sans-serif',
                color: '#f1f5f9'
            },
            xaxis: {
                gridcolor: '#334155',
                showgrid: true
            },
            yaxis: {
                gridcolor: '#334155',
                showgrid: true
            },
            hovermode: 'closest',
            margin: { t: 60, r: 40, b: 60, l: 60 }
        };

        this.config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
        };
    }

    /**
     * Render historical data chart
     */
    renderHistoricalChart(data, parameter = 'co2', chartDiv = null) {
        const targetDiv = chartDiv || this.historicalChartDiv;
        try {
            if (!data || data.length === 0) {
                this.showError(targetDiv, 'Data historis tidak tersedia');
                return;
            }

            const parameterKey = parameter === 'co2' ? 'co2_ppm' : 'co_ppm';
            const parameterLabel = parameter === 'co2' ? 'CO₂ (ppm)' : 'CO (ppm)';

            // Sort data by timestamp
            const sortedData = [...data].sort((a, b) =>
                new Date(a.timestamp) - new Date(b.timestamp)
            );

            // Extract timestamps and values
            const timestamps = sortedData.map(d => new Date(d.timestamp));
            const values = sortedData.map(d => d[parameterKey]);

            // Get classifications for colors
            const classifications = sortedData.map(d =>
                parameter === 'co2' ? d.co2_classification : d.co_classification
            );
            const colors = classifications.map(c => (c && c.category) ? this.colorMap[c.category] : '#3b82f6');

            // Create trace
            const trace = {
                x: timestamps,
                y: values,
                type: 'scatter',
                mode: 'lines+markers',
                name: parameterLabel,
                line: {
                    color: '#3b82f6',
                    width: 2
                },
                marker: {
                    size: 6,
                    color: colors,
                    line: {
                        color: '#1e293b',
                        width: 1
                    }
                },
                hovertemplate:
                    '<b>%{x|%Y-%m-%d %H:%M}</b><br>' +
                    parameterLabel + ': %{y:.2f}<br>' +
                    '<extra></extra>'
            };

            // Add threshold lines
            const thresholds = this.getThresholds(parameter);
            const shapes = thresholds.map(t => ({
                type: 'line',
                x0: timestamps[0],
                x1: timestamps[timestamps.length - 1],
                y0: t.value,
                y1: t.value,
                line: {
                    color: t.color,
                    width: 2,
                    dash: 'dash'
                }
            }));

            const annotations = thresholds.map(t => ({
                x: timestamps[timestamps.length - 1],
                y: t.value,
                text: t.label,
                showarrow: false,
                xanchor: 'left',
                xshift: 5,
                font: {
                    size: 10,
                    color: t.color
                }
            }));

            const maxValue = values.length ? Math.max(...values) : 0;
            let yRange = null;
            if (parameter === 'co2') {
                const extendY = Math.max(50, (maxValue - 300) * 0.1);
                yRange = [300, maxValue + extendY];
            } else {
                const minCO = values.length ? Math.min(...values) : 0;
                const extendY = Math.max(1, (maxValue - minCO) * 0.1);
                yRange = [Math.max(0, minCO - extendY), maxValue + extendY];
            }

            const layout = {
                ...this.commonLayout,
                title: {
                    text: `Data Historis ${parameterLabel}`,
                    font: { size: 16, weight: 600 },
                    y: 0.95,
                    x: 0.05,
                    xanchor: 'left',
                    yanchor: 'top'
                },
                xaxis: {
                    ...this.commonLayout.xaxis,
                    title: 'Waktu'
                },
                yaxis: {
                    ...this.commonLayout.yaxis,
                    title: parameterLabel,
                    ...(yRange ? { range: yRange } : {})
                },
                shapes: shapes,
                annotations: annotations
            };

            // Remove loading/error overlays if they exist
            const container = document.getElementById(targetDiv);
            if (container) {
                const overlay = container.querySelector('.chart-status-overlay');
                if (overlay) overlay.remove();
            }

            // Use Plotly.react for smooth updates (no flicker)
            Plotly.react(targetDiv, [trace], layout, this.config);
        } catch (error) {
            console.error('Error in renderHistoricalChart:', error);
            this.showError(targetDiv, 'Kesalahan rendering grafik historis');
        }
    }

    /**
     * Render prediction chart with confidence intervals
     */
    renderPredictionChart(historicalData, predictionData, parameter = 'co2', chartDiv = null) {
        const targetDiv = chartDiv || this.predictionChartDiv;
        try {
            if (!predictionData || predictionData.length === 0) {
                this.showError(targetDiv, 'Model belum dilatih atau data tidak cukup');
                return;
            }

            const parameterKey = parameter === 'co2' ? 'co2_ppm' : 'co_ppm';
            const parameterLabel = parameter === 'co2' ? 'CO₂ (ppm)' : 'CO (ppm)';

            // Sort historical data
            const sortedHistorical = [...(historicalData || [])]
                .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
                .slice(-30); // Last 30 points

            // Sort prediction data
            const sortedPredictions = [...predictionData].sort((a, b) =>
                new Date(a.prediction_date) - new Date(b.prediction_date)
            );

            // Historical trace
            const historicalTrace = {
                x: sortedHistorical.map(d => new Date(d.timestamp)),
                y: sortedHistorical.map(d => d[parameterKey]),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Data Aktual',
                line: {
                    color: '#3b82f6',
                    width: 2
                },
                marker: {
                    size: 6,
                    color: '#3b82f6'
                }
            };

            // Prediction trace
            const predictionTrace = {
                x: sortedPredictions.map(d => new Date(d.prediction_date)),
                y: sortedPredictions.map(d => d.predicted_value),
                type: 'scatter',
                mode: 'lines',
                name: 'Prediksi ARIMA',
                line: {
                    color: '#8b5cf6',
                    width: 3,
                    dash: 'dot'
                }
            };

            // Confidence interval (upper bound)
            const upperBound = {
                x: sortedPredictions.map(d => new Date(d.prediction_date)),
                y: sortedPredictions.map(d => d.confidence_upper),
                type: 'scatter',
                mode: 'lines',
                name: 'Batas Atas (95%)',
                line: {
                    color: 'rgba(139, 92, 246, 0.3)',
                    width: 0
                },
                fillcolor: 'rgba(139, 92, 246, 0.2)',
                fill: 'tonexty',
                showlegend: false
            };

            // Confidence interval (lower bound)
            const lowerBound = {
                x: sortedPredictions.map(d => new Date(d.prediction_date)),
                y: sortedPredictions.map(d => d.confidence_lower),
                type: 'scatter',
                mode: 'lines',
                name: 'Interval Kepercayaan 95%',
                line: {
                    color: 'rgba(139, 92, 246, 0.3)',
                    width: 0
                }
            };

            // Add threshold lines
            const thresholds = this.getThresholds(parameter);
            const allDates = [
                ...sortedHistorical.map(d => new Date(d.timestamp)),
                ...sortedPredictions.map(d => new Date(d.prediction_date))
            ];

            const shapes = thresholds.map(t => ({
                type: 'line',
                x0: allDates[0],
                x1: allDates[allDates.length - 1],
                y0: t.value,
                y1: t.value,
                line: {
                    color: t.color,
                    width: 2,
                    dash: 'dash'
                }
            }));

            const annotations = thresholds.map(t => ({
                x: allDates[allDates.length - 1],
                y: t.value,
                text: t.label,
                showarrow: false,
                xanchor: 'left',
                xshift: 5,
                font: {
                    size: 10,
                    color: t.color
                }
            }));

            const maxHistorical = sortedHistorical.length ? Math.max(...sortedHistorical.map(d => d[parameterKey])) : 0;
            const maxPredicted = sortedPredictions.length ? Math.max(...sortedPredictions.map(d => Math.max(d.confidence_upper || 0, d.predicted_value || 0))) : 0;
            const maxValue = Math.max(maxHistorical, maxPredicted);

            let yRange = null;
            if (parameter === 'co2') {
                const minHistorical = sortedHistorical.length ? Math.min(...sortedHistorical.map(d => d[parameterKey])) : 1000;
                const minPredicted = sortedPredictions.length ? Math.min(...sortedPredictions.map(d => Math.min(d.confidence_lower || 1000, d.predicted_value || 1000))) : 1000;
                const minValue = Math.min(minHistorical, minPredicted);

                const extendY = Math.max(50, (maxValue - minValue) * 0.1);
                yRange = [Math.max(0, minValue - extendY), maxValue + extendY];
            } else {
                const minHistorical = sortedHistorical.length ? Math.min(...sortedHistorical.map(d => d[parameterKey])) : 1000;
                const minPredicted = sortedPredictions.length ? Math.min(...sortedPredictions.map(d => Math.min(d.confidence_lower || 1000, d.predicted_value || 1000))) : 1000;
                const minValue = Math.min(minHistorical, minPredicted);

                const extendY = Math.max(1, (maxValue - minValue) * 0.1);
                yRange = [Math.max(0, minValue - extendY), maxValue + extendY];
            }

            const layout = {
                ...this.commonLayout,
                title: {
                    text: `Prediksi ${parameterLabel} dengan ARIMA`,
                    font: { size: 16, weight: 600 },
                    y: 0.95,
                    x: 0.05,
                    xanchor: 'left',
                    yanchor: 'top'
                },
                xaxis: {
                    ...this.commonLayout.xaxis,
                    title: 'Waktu'
                },
                yaxis: {
                    ...this.commonLayout.yaxis,
                    title: parameterLabel,
                    ...(yRange ? { range: yRange } : {})
                },
                shapes: shapes,
                annotations: annotations
            };

            const traces = [lowerBound, upperBound, historicalTrace, predictionTrace];

            // Remove loading/error overlays
            const container = document.getElementById(targetDiv);
            if (container) {
                const overlay = container.querySelector('.chart-status-overlay');
                if (overlay) overlay.remove();
            }

            // Use Plotly.react for smooth updates
            Plotly.react(targetDiv, traces, layout, this.config);
        } catch (error) {
            console.error('Error in renderPredictionChart:', error);
            this.showError(targetDiv, 'Kesalahan rendering grafik prediksi');
        }
    }

    /**
     * Get threshold values for a parameter
     */
    getThresholds(parameter) {
        if (parameter === 'co2') {
            return [
                { value: 400, label: 'Sedang', color: '#fbbf24' },
                { value: 1000, label: 'Tidak Sehat', color: '#f97316' },
                { value: 2000, label: 'Sangat Tidak Sehat', color: '#ef4444' },
                { value: 5000, label: 'Berbahaya', color: '#a855f7' }
            ];
        } else {
            return [
                { value: 4, label: 'Sedang', color: '#fbbf24' },
                { value: 9, label: 'Tidak Sehat', color: '#f97316' },
                { value: 15, label: 'Sangat Tidak Sehat', color: '#ef4444' },
                { value: 30, label: 'Berbahaya', color: '#a855f7' }
            ];
        }
    }

    /**
     * Show loading state on chart
     */
    showLoading(chartDiv) {
        const div = document.getElementById(chartDiv);
        if (!div) return;

        // Determine height based on container or common patterns
        const height = chartDiv.includes('comparison') ? '400px' : '300px';

        div.innerHTML = `
            <div class="chart-status-overlay" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: ${height}; color: #94a3b8; background: rgba(30, 41, 59, 0.5); border-radius: 8px;">
                <div class="loading-spinner-small" style="width: 30px; height: 30px; border: 3px solid rgba(59, 130, 246, 0.2); border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 15px;"></div>
                <div style="font-weight: 500; letter-spacing: 0.025em;">Memuat grafik...</div>
            </div>`;
    }

    /**
     * Show error state on chart
     */
    showError(chartDiv, message) {
        const div = document.getElementById(chartDiv);
        if (!div) return;
        const height = chartDiv.includes('comparison') ? '400px' : '300px';

        div.innerHTML = `
            <div class="chart-status-overlay" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: ${height}; color: #ef4444; background: rgba(239, 68, 68, 0.05); border-radius: 8px; border: 1px dashed rgba(239, 68, 68, 0.3);">
                <div style="font-size: 1.5rem; margin-bottom: 10px;">⚠️</div>
                <div style="font-weight: 500;">${message}</div>
            </div>`;
    }

    /**
     * Render comparison chart between Urban and Rural
     */
    renderComparisonChart(urbanData, ruralData, parameter = 'co2') {
        const parameterLabel = parameter === 'co2' ? 'CO₂ (ppm)' : 'CO (ppm)';
        const chartDiv = 'comparisonChart';

        try {
            if (!urbanData || !ruralData || urbanData.length === 0 || ruralData.length === 0) {
                this.showError(chartDiv, 'Data perbandingan tidak cukup (Pedesaan atau Permukiman Industri kosong)');
                return;
            }

            // Sort both datasets
            const sortedUrban = [...urbanData].sort((a, b) => new Date(a.prediction_date) - new Date(b.prediction_date));
            const sortedRural = [...ruralData].sort((a, b) => new Date(a.prediction_date) - new Date(b.prediction_date));

            const urbanTrace = {
                x: sortedUrban.map(d => new Date(d.prediction_date)),
                y: sortedUrban.map(d => d.predicted_value),
                type: 'scatter',
                mode: 'lines',
                name: '🏭 Permukiman Industri',
                line: { color: '#3b82f6', width: 3 }
            };

            const ruralTrace = {
                x: sortedRural.map(d => new Date(d.prediction_date)),
                y: sortedRural.map(d => d.predicted_value),
                type: 'scatter',
                mode: 'lines',
                name: '🏡 Prediksi ARIMA Permukiman Industri',
                line: { color: '#f97316', width: 3 }
            };

            // Calculate bounds based on max of both datasets
            const maxUrban = sortedUrban.length ? Math.max(...sortedUrban.map(d => d.predicted_value)) : 1000;
            const maxRural = sortedRural.length ? Math.max(...sortedRural.map(d => d.predicted_value)) : 1000;
            const maxValue = Math.max(maxUrban, maxRural);

            const minUrban = sortedUrban.length ? Math.min(...sortedUrban.map(d => d.predicted_value)) : 1000;
            const minRural = sortedRural.length ? Math.min(...sortedRural.map(d => d.predicted_value)) : 1000;
            const minValue = Math.min(minUrban, minRural);

            let yRange = null;
            if (parameter === 'co2') {
                const extendY = Math.max(50, (maxValue - minValue) * 0.1);
                yRange = [Math.max(0, minValue - extendY), maxValue + extendY];
            } else {
                const extendY = Math.max(1, (maxValue - minValue) * 0.1);
                yRange = [Math.max(0, minValue - extendY), maxValue + extendY];
            }

            const layout = {
                ...this.commonLayout,
                title: {
                    text: `Perbandingan Prediksi ${parameterLabel}`,
                    font: { size: 16, weight: 600 },
                    y: 0.95,
                    x: 0.05,
                    xanchor: 'left',
                    yanchor: 'top'
                },
                xaxis: { ...this.commonLayout.xaxis, title: 'Waktu' },
                yaxis: {
                    ...this.commonLayout.yaxis,
                    title: parameterLabel,
                    ...(yRange ? { range: yRange } : {})
                },
                legend: {
                    orientation: 'h',
                    y: -0.2,
                    font: { color: '#f1f5f9' }
                }
            };

            // Add thresholds if they fit the range
            const thresholds = this.getThresholds(parameter);
            layout.shapes = thresholds.map(t => ({
                type: 'line',
                x0: sortedUrban[0].prediction_date,
                x1: sortedUrban[sortedUrban.length - 1].prediction_date,
                y0: t.value,
                y1: t.value,
                line: { color: t.color, width: 1, dash: 'dot' }
            }));

            // Remove loading/error overlays
            const container = document.getElementById(chartDiv);
            if (container) {
                const overlay = container.querySelector('.chart-status-overlay');
                if (overlay) overlay.remove();
            }

            // Use Plotly.react for smooth updates
            Plotly.react(chartDiv, [urbanTrace, ruralTrace], layout, this.config);
        } catch (error) {
            console.error('Error in renderComparisonChart:', error);
            this.showError(chartDiv, 'Kesalahan rendering grafik perbandingan');
        }
    }
}

// Export for use in other modules
window.ChartManager = ChartManager;
