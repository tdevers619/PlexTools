$7zipPath = "C:\Path\To\7zip\7z.exe"
$sourceFolder = "C:\Path\To\Source\Folder"
$destinationFolder = "C:\Path\To\Extract\Destination"
$minFileSizeMB = 150  # Set the minimum file size in megabytes

# Get all zip files in the source folder with a size greater than or equal to the specified minimum size
$zipFiles = Get-ChildItem -Path $sourceFolder -Filter *.zip, *.rar | Where-Object { $_.Length -ge ($minFileSizeMB * 1MB) }

foreach ($zipFile in $zipFiles) {
    $zipFilePath = $zipFile.FullName

    # Construct the 7zip command to extract the zip file to the destination folder
    $extractCommand = "$7zipPath x `"$zipFilePath`" -o`"$destinationFolder`""

    # Run the 7zip command
    Invoke-Expression $extractCommand
}
