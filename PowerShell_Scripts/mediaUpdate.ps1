Token = ‘?X-Plex-Token=XXXXXXXXXXXXXXXXXXXX--XXXXXX’
$Plex = ‘http://127.0.0.1:32400’

[xml]$Library = (Invoke-WebRequest -Uri “$Plex/library/sections$Token”).Content

$LibraryItems = $Library.MediaContainer.Directory Write-Host “What do you want to refresh?”
$Counter = 0
foreach ($Element in $LibraryItems)
{
$Counter ++
$Title = $Element.Title
Write-Host “$Counter $Title”
}

$Selection = Read-Host
$Key = $library.MediaContainer.Directory[($Selection -1)].key

$DoRefresh = Invoke-WebRequest -Uri “$Plex/library/sections/$key/refresh$Token”
if ($DoRefresh.StatusCode -eq 200)
{
Write-Host “OK, refreshing library”
}
else
{
Write-Host “Ooops, something went wrong:nn$DoRefresh”
}