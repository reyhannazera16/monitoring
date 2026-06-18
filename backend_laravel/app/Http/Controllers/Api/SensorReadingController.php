<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\SensorReading;
use App\Utils\AirQualityStandards;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\DB;

class SensorReadingController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $readings = SensorReading::orderBy('timestamp', 'desc')->paginate(50);
        return response()->json($readings);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'co2_ppm' => 'required|numeric',
            'co_ppm' => 'required|numeric',
            'mq7_detected' => 'boolean',
            'location' => 'string',
            'status' => 'string|nullable',
            'timestamp' => 'date_format:Y-m-d H:i:s|nullable',
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 422);
        }

        $data = $request->all();
        if (!isset($data['timestamp'])) {
            $data['timestamp'] = now()->format('Y-m-d H:i:s');
        }

        $reading = SensorReading::create($data);

        return response()->json([
            'success' => true,
            'data' => $reading,
        ], 210);
    }

    /**
     * Latest sensor reading
     */
    public function latest(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');
        $reading = SensorReading::where('location', $location)
            ->orderBy('timestamp', 'desc')
            ->first();

        if ($reading) {
            $reading->co2_classification = AirQualityStandards::classify('co2', $reading->co2_ppm);
            $reading->co_classification = AirQualityStandards::classify('co', $reading->co_ppm);
        }

        return response()->json([
            'success' => true,
            'data' => $reading
        ]);
    }

    /**
     * Historical data
     */
    public function historical(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');
        $limit = $request->query('limit', 500);
        $startDate = $request->query('start_date');
        $endDate = $request->query('end_date');

        $query = SensorReading::where('location', $location);

        if ($startDate) {
            $query->where('timestamp', '>=', $startDate);
        }
        if ($endDate) {
            $query->where('timestamp', '<=', $endDate . ' 23:59:59');
        }

        $readings = $query->orderBy('timestamp', 'desc')
            ->limit($limit)
            ->get();

        foreach ($readings as $reading) {
            $reading->co2_classification = AirQualityStandards::classify('co2', $reading->co2_ppm);
            $reading->co_classification = AirQualityStandards::classify('co', $reading->co_ppm);
        }

        return response()->json([
            'success' => true,
            'count' => count($readings),
            'data' => $readings->reverse()->values() // Return in chronological order for charts
        ]);
    }

    /**
     * Summary statistics
     */
    public function statistics(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');
        $startDate = $request->query('start_date');
        $endDate = $request->query('end_date');

        $query = SensorReading::where('location', $location);

        if ($startDate) {
            $query->where('timestamp', '>=', $startDate);
        }
        if ($endDate) {
            $query->where('timestamp', '<=', $endDate . ' 23:59:59');
        }

        $stats = $query->select(
            DB::raw('COUNT(*) as total_readings'),
            DB::raw('AVG(co2_ppm) as avg_co2'),
            DB::raw('AVG(co_ppm) as avg_co'),
            DB::raw('MIN(co2_ppm) as min_co2'),
            DB::raw('MAX(co2_ppm) as max_co2'),
            DB::raw('MIN(co_ppm) as min_co'),
            DB::raw('MAX(co_ppm) as max_co')
        )
            ->first();

        $statsArray = $stats->toArray();
        if ($statsArray['avg_co2']) {
            $statsArray['avg_co2_classification'] = AirQualityStandards::classify('co2', $statsArray['avg_co2']);
        }
        if ($statsArray['avg_co']) {
            $statsArray['avg_co_classification'] = AirQualityStandards::classify('co', $statsArray['avg_co']);
        }

        return response()->json([
            'success' => true,
            'statistics' => $statsArray
        ]);
    }

    /**
     * Build one-step-ahead predictions using Holt's linear method.
     */
    private function buildOneStepPredictions(array $values, float $alpha = 0.45, float $beta = 0.20): array
    {
        $count = count($values);
        if ($count === 0) {
            return [];
        }

        $level = (float) $values[0];
        $trend = $count > 1 ? ((float) $values[1] - (float) $values[0]) : 0.0;
        $predictions = [null];

        for ($i = 1; $i < $count; $i++) {
            $predictions[] = max(0, $level + $trend);
            $previousLevel = $level;
            $observed = (float) $values[$i];
            $level = ($alpha * $observed) + ((1 - $alpha) * ($level + $trend));
            $trend = ($beta * ($level - $previousLevel)) + ((1 - $beta) * $trend);
        }

        return $predictions;
    }

    /**
     * Generate future ARIMA-like forecast from latest historical values.
     */
    private function generateArimaLikeForecast(array $values, \Carbon\Carbon $startDate, string $parameter, int $count = 168): array
    {
        $values = array_values(array_map(fn($v) => (float) $v, $values));
        if (count($values) === 0) {
            return [];
        }

        $alpha = 0.45;
        $beta = 0.20;
        $oneStep = $this->buildOneStepPredictions($values, $alpha, $beta);

        // Residual std for confidence interval width
        $residuals = [];
        for ($i = 1; $i < count($values); $i++) {
            if ($oneStep[$i] !== null) {
                $residuals[] = $values[$i] - $oneStep[$i];
            }
        }

        $std = 0.0;
        if (count($residuals) > 1) {
            $mean = array_sum($residuals) / count($residuals);
            $variance = array_sum(array_map(fn($e) => pow($e - $mean, 2), $residuals)) / (count($residuals) - 1);
            $std = sqrt(max(0, $variance));
        }

        $lastIndex = count($values) - 1;
        $lastLevel = $values[$lastIndex];
        $lastTrend = $lastIndex > 0 ? ($values[$lastIndex] - $values[$lastIndex - 1]) : 0.0;

        // Recalculate level/trend with full series for stable latest state
        if (count($values) > 1) {
            $level = $values[0];
            $trend = $values[1] - $values[0];
            for ($i = 1; $i < count($values); $i++) {
                $previousLevel = $level;
                $level = ($alpha * $values[$i]) + ((1 - $alpha) * ($level + $trend));
                $trend = ($beta * ($level - $previousLevel)) + ((1 - $beta) * $trend);
            }
            $lastLevel = $level;
            $lastTrend = $trend;
        }

        $result = [];
        for ($step = 1; $step <= $count; $step++) {
            $forecast = max(0, $lastLevel + ($step * $lastTrend));
            $spread = 1.96 * $std * sqrt($step);
            $date = (clone $startDate)->addHours($step);

            $result[] = [
                'prediction_date' => $date->toIso8601String(),
                'predicted_value' => round($forecast, 2),
                'confidence_lower' => round(max(0, $forecast - $spread), 2),
                'confidence_upper' => round($forecast + $spread, 2),
                'classification' => AirQualityStandards::classify($parameter, $forecast),
            ];
        }

        return $result;
    }

    /**
     * Predictions endpoint
     */
    public function predictions(Request $request, $parameter)
    {
        if (!in_array($parameter, ['co2', 'co'])) {
            return response()->json(['success' => false, 'message' => 'Parameter tidak valid'], 422);
        }

        $location = $request->query('location', 'Perkotaan');
        $column = $parameter === 'co2' ? 'co2_ppm' : 'co_ppm';
        $historical = SensorReading::where('location', $location)
            ->orderBy('timestamp', 'asc')
            ->limit(500)
            ->get();

        $values = $historical->pluck($column)->toArray();
        $startDate = $historical->count() > 0
            ? \Carbon\Carbon::parse($historical->last()->timestamp)
            : now();
        $predictions = $this->generateArimaLikeForecast($values, $startDate, $parameter, 168);

        return response()->json([
            'success' => true,
            'parameter' => $parameter,
            'count' => count($predictions),
            'model_metadata' => [
                'model' => 'Holt Linear (ARIMA-like)',
                'alpha' => 0.45,
                'beta' => 0.20,
                'training_points' => count($values)
            ],
            'data' => $predictions
        ]);
    }

    /**
     * Survival analysis based on real sensor data with linear regression
     */
    public function survivalAnalysis(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');
        $locationLabel = $location === 'Perkotaan' ? 'Permukiman Industri' : 'Permukiman Industri Prediksi ARIMA';

        $readings = SensorReading::where('location', $location)
            ->orderBy('timestamp', 'asc')
            ->limit(500)
            ->get();

        if ($readings->count() < 2) {
            return response()->json([
                'success' => true,
                'analysis' => [
                    'summary_message' => 'Data tidak cukup untuk analisis waktu bertahan.',
                    'overall_assessment' => [
                        'days_until_unhealthy' => null,
                        'status' => 'good'
                    ]
                ]
            ]);
        }

        $thresholds = [
            'co2' => ['tidak_sehat' => 1000],
            'co'  => ['tidak_sehat' => 9],
        ];

        $avgCO2 = $readings->avg('co2_ppm');
        $avgCO = $readings->avg('co_ppm');

        $calcTrend = function ($values) {
            $n = count($values);
            if ($n < 2) return ['slope' => 0, 'lastValue' => $values[0] ?? 0];
            $sumX = 0; $sumY = 0; $sumXY = 0; $sumX2 = 0;
            for ($i = 0; $i < $n; $i++) {
                $sumX += $i;
                $sumY += $values[$i];
                $sumXY += $i * $values[$i];
                $sumX2 += $i * $i;
            }
            $slope = ($n * $sumXY - $sumX * $sumY) / ($n * $sumX2 - $sumX * $sumX);
            $intercept = ($sumY - $slope * $sumX) / $n;
            return ['slope' => $slope, 'lastValue' => $intercept + $slope * ($n - 1)];
        };

        $co2Trend = $calcTrend($readings->pluck('co2_ppm')->toArray());
        $coTrend = $calcTrend($readings->pluck('co_ppm')->toArray());

        $firstTime = strtotime($readings->first()->timestamp);
        $lastTime = strtotime($readings->last()->timestamp);
        $intervalDays = ($lastTime - $firstTime) / 86400 / ($readings->count() - 1);

        $projectDays = function ($trend, $threshold) use ($intervalDays) {
            if ($trend['lastValue'] >= $threshold) return 0;
            if ($trend['slope'] <= 0) return null;
            $steps = ($threshold - $trend['lastValue']) / $trend['slope'];
            $days = round($steps * $intervalDays);
            return $days > 0 ? (int) $days : null;
        };

        $co2Unhealthy = $projectDays($co2Trend, $thresholds['co2']['tidak_sehat']);
        $coUnhealthy = $projectDays($coTrend, $thresholds['co']['tidak_sehat']);

        $unhealthyArr = array_filter([$co2Unhealthy, $coUnhealthy], fn($v) => $v !== null);

        $daysUnhealthy = count($unhealthyArr) > 0 ? min($unhealthyArr) : null;

        if ($daysUnhealthy === 0) $status = 'critical';
        elseif ($daysUnhealthy !== null && $daysUnhealthy < 30) $status = 'warning';
        elseif ($daysUnhealthy !== null && $daysUnhealthy < 90) $status = 'caution';
        else $status = 'good';

        $avgCO2Str = number_format($avgCO2, 1);
        $avgCOStr = number_format($avgCO, 1);
        if ($daysUnhealthy === 0) {
            $summary = "PERINGATAN: Kualitas udara di wilayah {$locationLabel} sudah memasuki kategori Tidak Sehat. Rata-rata CO2: {$avgCO2Str} ppm, CO: {$avgCOStr} ppm.";
        } elseif ($daysUnhealthy !== null) {
            $summary = "Berdasarkan tren data sensor, wilayah {$locationLabel} diperkirakan dapat mempertahankan kualitas udara Baik-Sedang selama ~{$daysUnhealthy} hari ke depan. Rata-rata CO2: {$avgCO2Str} ppm, CO: {$avgCOStr} ppm.";
        } else {
            $summary = "Kualitas udara di wilayah {$locationLabel} terpantau stabil atau membaik. Rata-rata CO2: {$avgCO2Str} ppm, CO: {$avgCOStr} ppm. Tidak terdeteksi tren peningkatan menuju kategori Tidak Sehat.";
        }

        return response()->json([
            'success' => true,
            'analysis' => [
                'summary_message' => $summary,
                'overall_assessment' => [
                    'days_until_unhealthy' => $daysUnhealthy,
                    'status' => $status
                ]
            ]
        ]);
    }

    /**
     * Train models placeholder
     */
    public function train(Request $request)
    {
        return response()->json([
            'success' => true,
            'message' => 'Models trained successfully (Simulated)'
        ]);
    }

    /**
     * Export Excel - 2 sheet: Laporan CO2 dan Laporan CO
     */
    public function export(Request $request)
    {
        // Fetch latest historical data from main location
        $readings = SensorReading::where('location', 'Perkotaan')
            ->orderBy('timestamp', 'asc')
            ->get()
            ->values();

        // Helper to build rows for a given parameter using one-step predictions
        $buildRows = function ($param) use ($readings) {
            $col = ($param === 'co') ? 'co_ppm' : 'co2_ppm';
            $formatPpm = fn($value) => number_format((float) $value, 2, ',', '');
            $values = $readings->pluck($col)->map(fn($v) => (float) $v)->values()->all();
            $predictions = $this->buildOneStepPredictions($values);
            $rows = [];

            foreach ($readings as $idx => $reading) {
                $actual = (float) $reading->{$col};
                $pred = $predictions[$idx] ?? null;
                $waktu = \Carbon\Carbon::parse($reading->timestamp)->format('d/m/Y H:i');
                $classification = AirQualityStandards::classify($param, $actual);
                $status = $classification['label'] ?? 'Sedang';

                $rows[] = [
                    $waktu,
                    $formatPpm($actual),
                    $pred !== null ? $formatPpm($pred) : '-',
                    $status,
                ];
            }

            return $rows;
        };

        // Build Excel
        $spreadsheet = new \PhpOffice\PhpSpreadsheet\Spreadsheet();

        $headers = ['Waktu', 'Data Aktual (PPM)', 'Prediksi ARIMA (PPM)', 'Status Kualitas Udara'];
        $colWidths = [20, 18, 22, 22];

        $applySheet = function ($sheet, $title, $rows) use ($headers, $colWidths) {
            $sheet->setTitle($title);

            // Style header
            $headerStyle = [
                'font'      => ['bold' => true, 'color' => ['rgb' => 'FFFFFF'], 'size' => 11],
                'fill'      => ['fillType' => \PhpOffice\PhpSpreadsheet\Style\Fill::FILL_SOLID, 'startColor' => ['rgb' => '1E40AF']],
                'alignment' => ['horizontal' => \PhpOffice\PhpSpreadsheet\Style\Alignment::HORIZONTAL_CENTER, 'vertical' => \PhpOffice\PhpSpreadsheet\Style\Alignment::VERTICAL_CENTER],
                'borders'   => ['allBorders' => ['borderStyle' => \PhpOffice\PhpSpreadsheet\Style\Border::BORDER_THIN, 'color' => ['rgb' => 'CCCCCC']]],
            ];

            // Write headers
            foreach ($headers as $i => $h) {
                $col = \PhpOffice\PhpSpreadsheet\Cell\Coordinate::stringFromColumnIndex($i + 1);
                $sheet->setCellValue("{$col}1", $h);
                $sheet->getColumnDimension($col)->setWidth($colWidths[$i]);
            }
            $sheet->getStyle('A1:D1')->applyFromArray($headerStyle);
            $sheet->getRowDimension(1)->setRowHeight(22);

            // Alternate row fill colors
            $evenFill = ['fillType' => \PhpOffice\PhpSpreadsheet\Style\Fill::FILL_SOLID, 'startColor' => ['rgb' => 'EFF6FF']];
            $oddFill  = ['fillType' => \PhpOffice\PhpSpreadsheet\Style\Fill::FILL_SOLID, 'startColor' => ['rgb' => 'FFFFFF']];

            foreach ($rows as $ri => $row) {
                $rowNum = $ri + 2;
                foreach ($row as $ci => $val) {
                    $col = \PhpOffice\PhpSpreadsheet\Cell\Coordinate::stringFromColumnIndex($ci + 1);
                    $sheet->setCellValue("{$col}{$rowNum}", $val);
                }
                $fill = ($ri % 2 === 0) ? $evenFill : $oddFill;
                $sheet->getStyle("A{$rowNum}:D{$rowNum}")->applyFromArray([
                    'fill'      => $fill,
                    'borders'   => ['allBorders' => ['borderStyle' => \PhpOffice\PhpSpreadsheet\Style\Border::BORDER_THIN, 'color' => ['rgb' => 'DDDDDD']]],
                    'alignment' => ['horizontal' => \PhpOffice\PhpSpreadsheet\Style\Alignment::HORIZONTAL_CENTER],
                ]);
                // Left-align Waktu column
                $sheet->getStyle("A{$rowNum}")->getAlignment()->setHorizontal(\PhpOffice\PhpSpreadsheet\Style\Alignment::HORIZONTAL_LEFT);
            }

            // Freeze header row
            $sheet->freezePane('A2');
        };

        // Sheet 1: CO2
        $sheet1 = $spreadsheet->getActiveSheet();
        $applySheet($sheet1, 'Laporan CO2', $buildRows('co2'));

        // Sheet 2: CO
        $sheet2 = $spreadsheet->createSheet();
        $applySheet($sheet2, 'Laporan CO', $buildRows('co'));

        // Set active sheet to first
        $spreadsheet->setActiveSheetIndex(0);

        $filename = 'Laporan_Kualitas_Udara_' . date('Ymd') . '.xlsx';

        $writer = new \PhpOffice\PhpSpreadsheet\Writer\Xlsx($spreadsheet);

        return response()->stream(function () use ($writer) {
            $writer->save('php://output');
        }, 200, [
            'Content-Type'        => 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition' => "attachment; filename=\"{$filename}\"",
            'Cache-Control'       => 'max-age=0',
            'Pragma'              => 'no-cache',
            'Expires'             => '0',
        ]);
    }

    /**
     * Air quality standards
     */
    public function standards()
    {
        return response()->json([
            'success' => true,
            'standards' => [
                'co2' => AirQualityStandards::CO2_STANDARDS,
                'co' => AirQualityStandards::CO_STANDARDS
            ]
        ]);
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        $reading = SensorReading::find($id);
        if (!$reading) {
            return response()->json(['message' => 'Not Found'], 404);
        }
        return response()->json($reading);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        $reading = SensorReading::find($id);
        if (!$reading) {
            return response()->json(['message' => 'Not Found'], 404);
        }

        $reading->update($request->all());

        return response()->json([
            'success' => true,
            'data' => $reading,
        ]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        $reading = SensorReading::find($id);
        if (!$reading) {
            return response()->json(['message' => 'Not Found'], 404);
        }

        $reading->delete();

        return response()->json([
            'success' => true,
            'message' => 'Deleted successfully',
        ]);
    }
}
