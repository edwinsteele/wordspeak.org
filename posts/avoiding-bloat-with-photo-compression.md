<!--
.. title: Avoiding bloat with photo compression
.. slug: avoiding-bloat-with-photo-compression
.. date: 2018-04-14 06:38:45 UTC+10:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

I'm reviewing image sizes to improve download times in my photo galleries and I've produced best results by performing a single compression step rather than allowing each tool to compress as it processes the images.

Each tool in my workflow has defaults that work well if there is no subsequent or proceeding compression, but produce suboptimal results when used in an image pipeline where each tool performs compression. My workflow is:

* Load and edit photos in Apple's Photos.app. 
* Export from Photos.app. I choose a "JPEG Quality" level at export time.
* Stamp copyright and licencing info using exiftool
* Resize images as a part of image gallery creation using Pillow, which generally involves a compression step
* Perform final optimisation using imageOptim. I've used this tool in the past to reduce jpg sizes with great success and it optimises my images, along with images that ship with sigal and it's libraries. Adding this step was the trigger point for this investigation.

For my arches gallery
Compression levels and resulting file sizes at each stage Photos.app compression, Pillow resize and compression, jpegmini compression, imageOptim compression

| Photos.app (size) | Pillow (filesize) | jpegmini (filesize) | imageOptim (filesize) |
|-------------------|-------------------|---------------------|-----------------------|
| medium (19.1MB)   | 75% (5.2MB)       | not used            | 74% (4.6MB)           |
| maximum (103.6MB) | 75% (5.2MB)       | not used            | 74% (4.6MB)           |
| maximum (103.6MB) | 100% (27.8MB)     | not used            | 74% (4.1MB)           |
| maximum (103.6MB) | 100% (27.8MB)     | used (7.1MB)        | 74% (4.3MB)           |



medium (19.1) -> 75 w/ resize (5.2) -> 74 (4.6)
maximum (103.6) -> 75 w/ resize (5.2) -> 74 (4.6)
maximum (103.6) -> 100 w/ resize (27.8) -> 74 (4.1)
maximum (103.6) -> 100 w/ resize (27.8) -> 66 (3.3)
maximum (103.6) -> 100 w/ resize no-prog (30.9) -> 74 (4.1)


imageOptim: 74@normal -> 4072kb

(Photos.app, Pillow, imageOptim)


maximum (103.6) -> 100 w/ resize (27.8) -> jpegmini (7.1) -> 74 (4.3)
