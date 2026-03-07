/**
 * API Client for Air Quality Monitoring System
 * Handles all communication with the Flask backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

class APIClient {
    /**
     * Generic fetch wrapper with error handling
     */
    static async fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    /**
     * Get historical sensor data
     */
    static async getHistoricalData(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const endpoint = `/data/historical${queryParams ? '?' + queryParams : ''}`;
        return await this.fetch(endpoint);
    }

    /**
     * Get latest sensor reading
     */
    static async getLatestData(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const endpoint = `/data/latest${queryParams ? '?' + queryParams : ''}`;
        return await this.fetch(endpoint);
    }

    /**
     * Get predictions for a parameter
     */
    static async getPredictions(parameter, params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const endpoint = `/predictions/${parameter}${queryParams ? '?' + queryParams : ''}`;
        return await this.fetch(endpoint);
    }

    /**
     * Get survival time analysis
     */
    static async getSurvivalAnalysis(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const endpoint = `/analysis/survival${queryParams ? '?' + queryParams : ''}`;
        return await this.fetch(endpoint);
    }

    /**
     * Get statistics
     */
    static async getStatistics(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const endpoint = `/statistics${queryParams ? '?' + queryParams : ''}`;
        return await this.fetch(endpoint);
    }

    /**
     * Get air quality standards
     */
    static async getStandards() {
        return await this.fetch('/standards');
    }

    /**
     * Train models
     */
    static async trainModels(params = {}) {
        return await this.fetch('/model/train', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    /**
     * Export data as CSV
     */
    static exportCSV(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const url = `${API_BASE_URL}/export/csv${queryParams ? '?' + queryParams : ''}`;

        fetch(url)
            .then(response => response.text())
            .then(csvText => {
                // Replace location label
                const updatedCsv = csvText.replaceAll('Perkotaan', 'Permukiman Industri');

                // Trigger download
                const blob = new Blob([updatedCsv], { type: 'text/csv' });
                const downloadUrl = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = 'air_quality_data.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(downloadUrl);
            })
            .catch(error => {
                console.error('Export error:', error);
                alert('Gagal mengekspor data CSV');
            });
    }

    /**
     * Log sensor data (for Arduino)
     */
    static async logSensorData(data) {
        return await this.fetch('/log', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// Export for use in other modules
window.APIClient = APIClient;
