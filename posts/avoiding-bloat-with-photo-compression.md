<!--
.. title: Avoiding bloat with photo compression
.. slug: avoiding-bloat-with-photo-compression
.. date: 2018-04-14 06:38:45 UTC+10:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. spellcheck_exceptions: imageOptim, JPEGmini, resize
.. type: text
-->

I'm reviewing image sizes to improve download times in my photo galleries and I've produced best results by performing a single compression step rather than allowing each tool to compress as it processes the images.

Each tool in my workflow has defaults that work well if there is no subsequent or proceeding compression, but produce suboptimal results when used in an image pipeline where each tool performs compression. My workflow is:

1. Load and edit photos in Apple's Photos.app. 
1. Export from Photos.app. I choose a "JPEG Quality" level at export time.
1. Stamp copyright and licencing info using exiftool
1. Resize images as a part of image gallery creation using Pillow, which generally involves a compression step
1. Perform final optimisation using imageOptim. I've used this tool in the past to reduce jpg sizes with great success and it's consistently given me the best image compression. Adding this step was the trigger point for this investigation.

I did experiments on my [Arches gallery](https://images.wordspeak.org/arches/) whose photos have a total uncompressed size of 103.6MB. I tried four permutations of compression with the results below, noting that the Pillow step also includes resizing:

1. Compression by Photos.app, Pillow and imageOptim: Final size 4.6MB
    * Photos.app (medium quality) _103.6MB &#8594; 19.1MB_
    * Pillow (75% quality) _19.1MB &#8594; 5.2MB_
    * imageOptim (74% quality) _5.2MB &#8594; 4.6MB_
2. Compression by Pillow and imageOptim: Final size 4.6MB
    * Photos.app (maximum quality) _103.6MB &#8594; 103.6MB_
    * Pillow (75% quality) _103.6MB &#8594; 5.2MB_
    * imageOptim (74% quality) _5.2MB &#8594; 4.6MB_
3. Compression by jpegMini and imageOptim: Final size 4.3MB
    * Photos.app (maximum quality) _103.6MB &#8594; 103.6MB_
    * Pillow (100% quality) _103.6MB &#8594; 27.8MB_
    * JPEGmini (no user-selectable settings) _27.8MB &#8594; 7.1MB_
    * imageOptim (74% quality) _7.1MB &#8594; 4.3MB_
4. **Compression by imageOptim only: Final size 4.1MB** (best result)
    * Photos.app (maximum quality) _103.6MB &#8594; 103.6MB_
    * Pillow (100% quality) _103.6MB &#8594; 27.8MB_
    * imageOptim (74% quality) _27.8MB &#8594; 4.1MB_

The best result comes from performing a single compression step with the best compression tool. 

I expected that the individual compression tools would have complementary compression schemes and chaining them together would give the best compression. I suspect now that imageOptim uses all the types of compression schemes available in the other tools and gets the best result because it can take an image with low [entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) image i.e. an uncompressed image and introduce all the entropy (compression) in a single step.
