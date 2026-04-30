<?php
require 'vendor/autoload.php';
$s = \PhpOffice\PhpSpreadsheet\IOFactory::load('../test_export.xlsx');
echo 'Sheet count: ' . $s->getSheetCount() . PHP_EOL;
foreach ($s->getSheetNames() as $name) {
    echo '  Sheet: ' . $name . PHP_EOL;
}
$sheet = $s->getSheet(0);
$rows = $sheet->toArray();
echo 'Row 1 (header): ' . implode(' | ', $rows[0]) . PHP_EOL;
echo 'Row 2 (first data): ' . implode(' | ', $rows[1]) . PHP_EOL;
echo 'Total rows: ' . count($rows) . PHP_EOL;
