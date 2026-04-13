$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$base   = 'http://localhost:4000/stevekelly-portfolio/samples'
$out    = 'C:\Users\Steven\Documents\stevekelly-portfolio\assets\pdf'

$slugs = @(
  'vpn-migration',
  'wan-failover-postmortem',
  'wan-failover-technical',
  'wan-failover-architecture',
  'aws-directconnect-migration'
)

foreach ($slug in $slugs) {
  $pdf = Join-Path $out "$slug.pdf"
  $url = "$base/$slug"
  Write-Host "Generating: $slug -> $pdf"

  $argList = @(
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--run-all-compositor-stages-before-draw',
    '--virtual-time-budget=8000',
    '--print-to-pdf-no-header',
    "--print-to-pdf=$pdf",
    $url
  )

  $proc = Start-Process -FilePath $chrome -ArgumentList $argList -Wait -PassThru -NoNewWindow
  $size = (Get-Item $pdf -ErrorAction SilentlyContinue).Length
  Write-Host "  Exit: $($proc.ExitCode)  Size: $size bytes"
}

Write-Host "Done."
