param(
    [string]$BarotraumaRoot = "D:\SteamLibrary\steamapps\common\Barotrauma",
    [string]$OutputAtlasName = "ColoredStatusIconsAtlas.png",
    [string]$OutputMapName = "ColoredStatusIconsAtlas.csv",
    [int]$Columns = 8
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$afflictionsPath = Join-Path $BarotraumaRoot "Content\Afflictions.xml"
$talentAfflictionsDir = Join-Path $BarotraumaRoot "Content\Talents"
$sourceAtlasPath = Join-Path $BarotraumaRoot "Content\UI\MainIconsAtlas.png"
$outputAtlasPath = Join-Path $scriptDir $OutputAtlasName
$outputMapPath = Join-Path $scriptDir $OutputMapName

if (-not (Test-Path -LiteralPath $afflictionsPath)) {
    throw "Afflictions.xml not found: $afflictionsPath"
}
if (-not (Test-Path -LiteralPath $sourceAtlasPath)) {
    throw "MainIconsAtlas.png not found: $sourceAtlasPath"
}
if ($Columns -lt 1) {
    throw "Columns must be 1 or greater."
}

$xmlPaths = @($afflictionsPath)
if (Test-Path -LiteralPath $talentAfflictionsDir) {
    $xmlPaths += Get-ChildItem -LiteralPath $talentAfflictionsDir -Recurse -File -Filter "Afflictions*.xml" |
        ForEach-Object { $_.FullName }
}
$xmlPaths = $xmlPaths | Select-Object -Unique

function Parse-IntList {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value,
        [Parameter(Mandatory = $true)]
        [int]$ExpectedCount
    )

    $parts = $Value.Split(",") | ForEach-Object { [int]($_.Trim()) }
    if ($parts.Count -ne $ExpectedCount) {
        throw "Expected $ExpectedCount comma-separated integers, got '$Value'."
    }
    return $parts
}

function Get-AncestorIdentifier {
    param(
        [Parameter(Mandatory = $true)]
        [System.Xml.XmlNode]$Node
    )

    $current = $Node.ParentNode
    while ($null -ne $current) {
        if ($current.Attributes -and $current.Attributes["identifier"]) {
            return $current.Attributes["identifier"].Value
        }
        $current = $current.ParentNode
    }
    return ""
}

function New-TintedIcon {
    param(
        [Parameter(Mandatory = $true)]
        [System.Drawing.Bitmap]$SourceAtlas,
        [Parameter(Mandatory = $true)]
        [int[]]$Rect,
        [Parameter(Mandatory = $true)]
        [int[]]$Color
    )

    $sourceX = $Rect[0]
    $sourceY = $Rect[1]
    $width = $Rect[2]
    $height = $Rect[3]
    $tintR = $Color[0]
    $tintG = $Color[1]
    $tintB = $Color[2]
    $tintA = if ($Color.Count -ge 4) { $Color[3] } else { 255 }

    $icon = New-Object System.Drawing.Bitmap $width, $height, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)

    for ($y = 0; $y -lt $height; $y++) {
        for ($x = 0; $x -lt $width; $x++) {
            $pixel = $SourceAtlas.GetPixel($sourceX + $x, $sourceY + $y)
            if ($pixel.A -eq 0) {
                $icon.SetPixel($x, $y, [System.Drawing.Color]::FromArgb(0, 0, 0, 0))
                continue
            }

            $intensity = (($pixel.R + $pixel.G + $pixel.B) / 3.0) / 255.0
            $alpha = [Math]::Round(($pixel.A * $tintA) / 255.0)
            $red = [Math]::Min(255, [Math]::Round($tintR * $intensity))
            $green = [Math]::Min(255, [Math]::Round($tintG * $intensity))
            $blue = [Math]::Min(255, [Math]::Round($tintB * $intensity))

            $icon.SetPixel($x, $y, [System.Drawing.Color]::FromArgb($alpha, $red, $green, $blue))
        }
    }

    return $icon
}

$entries = @()
foreach ($xmlPath in $xmlPaths) {
    [xml]$xml = Get-Content -LiteralPath $xmlPath -Raw
    $iconNodes = $xml.SelectNodes("//icon[contains(translate(@texture, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'mainiconsatlas.png') and @sourcerect and @color]")

    foreach ($node in $iconNodes) {
        $rect = @(Parse-IntList -Value $node.sourcerect -ExpectedCount 4)
        $color = @(Parse-IntList -Value $node.color -ExpectedCount 4)
        $entries += [pscustomobject]@{
            Identifier = Get-AncestorIdentifier -Node $node
            SourceXml = $xmlPath.Substring($BarotraumaRoot.Length + 1)
            SourceRect = $node.sourcerect
            Color = $node.color
            X = $rect[0]
            Y = $rect[1]
            Width = $rect[2]
            Height = $rect[3]
            ColorR = $color[0]
            ColorG = $color[1]
            ColorB = $color[2]
            ColorA = $color[3]
        }
    }
}

if ($entries.Count -eq 0) {
    throw "No colored MainIconsAtlas icon entries found in $afflictionsPath"
}

$maxWidth = ($entries | Measure-Object Width -Maximum).Maximum
$maxHeight = ($entries | Measure-Object Height -Maximum).Maximum
$rows = [Math]::Ceiling($entries.Count / [double]$Columns)
$outputWidth = $Columns * $maxWidth
$outputHeight = $rows * $maxHeight

$sourceAtlas = [System.Drawing.Bitmap]::FromFile($sourceAtlasPath)
$outputAtlas = New-Object System.Drawing.Bitmap $outputWidth, $outputHeight, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$graphics = [System.Drawing.Graphics]::FromImage($outputAtlas)
$graphics.Clear([System.Drawing.Color]::FromArgb(0, 0, 0, 0))
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half

$mapRows = @()
for ($i = 0; $i -lt $entries.Count; $i++) {
    $entry = $entries[$i]
    $col = $i % $Columns
    $row = [Math]::Floor($i / $Columns)
    $destX = $col * $maxWidth
    $destY = $row * $maxHeight

    $tinted = New-TintedIcon -SourceAtlas $sourceAtlas -Rect @($entry.X, $entry.Y, $entry.Width, $entry.Height) -Color @($entry.ColorR, $entry.ColorG, $entry.ColorB, $entry.ColorA)
    $graphics.DrawImage($tinted, $destX, $destY, $entry.Width, $entry.Height)
    $tinted.Dispose()

    $mapRows += [pscustomobject]@{
        index = $i
        identifier = $entry.Identifier
        source_xml = $entry.SourceXml
        source_texture = "Content/UI/MainIconsAtlas.png"
        source_rect = $entry.SourceRect
        color = $entry.Color
        output_texture = $OutputAtlasName
        output_rect = "$destX,$destY,$($entry.Width),$($entry.Height)"
    }
}

$outputAtlas.Save($outputAtlasPath, [System.Drawing.Imaging.ImageFormat]::Png)
$mapRows | Export-Csv -LiteralPath $outputMapPath -NoTypeInformation -Encoding UTF8

$graphics.Dispose()
$outputAtlas.Dispose()
$sourceAtlas.Dispose()

Write-Host "Wrote $($entries.Count) colored status icons."
Write-Host "Atlas: $outputAtlasPath"
Write-Host "Map:   $outputMapPath"
