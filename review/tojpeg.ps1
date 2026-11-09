# Converts the CAD/FEA render PNGs to compact JPEGs for the review page (called by review/build.mjs on Windows).
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File review\tojpeg.ps1 <src.png> <dst.jpg> [width] [quality]
param([string]$src, [string]$dst, [int]$width = 1400, [long]$quality = 84)
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile($src)
try {
    $w = [Math]::Min($width, $img.Width); $h = [int][Math]::Round($img.Height * $w / $img.Width)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = 'HighQualityBicubic'; $g.SmoothingMode = 'HighQuality'; $g.PixelOffsetMode = 'HighQuality'
    $g.Clear([System.Drawing.Color]::White); $g.DrawImage($img, 0, 0, $w, $h); $g.Dispose()
    $enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
    $p = New-Object System.Drawing.Imaging.EncoderParameters 1
    $p.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, $quality)
    $bmp.Save($dst, $enc, $p); $bmp.Dispose()
} finally { $img.Dispose() }
