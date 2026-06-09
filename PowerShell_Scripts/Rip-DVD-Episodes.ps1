# Rip-DVD-Episodes.ps1

$HandBrake = "C:\Program Files\HandBrake\HandBrakeCLI.exe"

# DVD drive letter
$DvdDrive = Read-Host "Enter DVD drive letter, example D:"
if ($DvdDrive -notmatch ":$") {
    $DvdDrive = "$DvdDrive`:"
}

# Plex naming info
$ShowName = Read-Host "Enter show name, example Pokemon"
$SeasonNumber = Read-Host "Enter season number, example 1"
$StartingEpisode = Read-Host "Enter starting episode number, example 1"

# Output folder
$BaseOutput = Read-Host "Enter output folder, example D:\Plex\TV Shows"
$SeasonFolder = Join-Path $BaseOutput "$ShowName\Season $($SeasonNumber.PadLeft(2,'0'))"

New-Item -ItemType Directory -Force -Path $SeasonFolder | Out-Null

Write-Host "`nScanning DVD titles..." -ForegroundColor Cyan
& $HandBrake -i $DvdDrive --scan

Write-Host "`nReview the scan above and enter the DVD title numbers for episodes." -ForegroundColor Yellow
Write-Host "Example: 1,2,3,4`n"

$TitlesInput = Read-Host "Enter title numbers"
$Titles = $TitlesInput -split "," | ForEach-Object { $_.Trim() }

$EpisodeNumber = [int]$StartingEpisode

$TotalTitles = $Titles.Count
$CurrentIndex = 0

foreach ($Title in $Titles) {
    $CurrentIndex++

    $SeasonPadded = $SeasonNumber.PadLeft(2,'0')
    $EpisodePadded = $EpisodeNumber.ToString().PadLeft(2,'0')

    $FileName = "$ShowName - S$SeasonPadded`E$EpisodePadded.mp4"
    $OutputFile = Join-Path $SeasonFolder $FileName

    $OverallPercent = [math]::Round(($CurrentIndex / $TotalTitles) * 100, 0)

    Write-Progress `
        -Id 1 `
        -Activity "DVD Conversion Progress" `
        -Status "Starting episode $CurrentIndex of $TotalTitles - Title $Title" `
        -PercentComplete $OverallPercent

    Write-Host "`nRipping title $Title to $FileName..." -ForegroundColor Green

    & $HandBrake `
        -i $DvdDrive `
        -t $Title `
        -o $OutputFile `
        --preset "Fast 480p30" `
        -e x264 `
        -q 20 `
        -B 160

    Write-Progress `
        -Id 1 `
        -Activity "DVD Conversion Progress" `
        -Status "Completed episode $CurrentIndex of $TotalTitles" `
        -PercentComplete $OverallPercent

    $EpisodeNumber++
}

Write-Progress -Id 1 -Activity "DVD Conversion Progress" -Completed