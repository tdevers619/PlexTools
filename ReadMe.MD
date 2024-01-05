# How it Works

This script uses Get-ChildItem to retrieve all zip files in the specified source folder that meet the size criterion. It then iterates through the filtered zip files and uses the 7zip command to extract them to the destination folder.

# Set Paths

Remember to customize the paths ($7zipPath, $sourceFolder, and $destinationFolder) and the minimum file size ($minFileSizeMB) according to your requirements. Also, ensure that you have appropriate permissions to read files from the source folder and write to the destination folder.
