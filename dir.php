$path = "/stg";
$dir = new DirectoryIterator($path);
foreach ($dir as $fileinfo) {
        if ($fileinfo->isDir() && !$fileinfo->isDot()) {
                echo $fileinfo->getFilename().'<br>';
        }
}
