import flickr_api
import argparse
import os


PHOTO_SIZES = ("Small", "Medium", "Large")
REPO_ASSETS_LOCATION = "/Users/esteele/Code/wordspeak.org/files"
WEBSERVER_PICTURE_PREFIX = "/assets/pictures/%s"


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)


def main(photo_id, desired_sizes, api_key, api_secret):
    flickr_api.set_keys(api_key=api_key, api_secret=api_secret)
    p = flickr_api.Photo(id=photo_id)

    sizes = p.getSizes()
    size_descs = sorted([(x, int(sizes[x]["width"])) for x in p.getSizes()],
                        key=lambda x: int(x[1]))

    wpp = WEBSERVER_PICTURE_PREFIX % (photo_id,)
    print "Widths available: ",
    for name, px_width in size_descs:
        print "%spx (%s)," % (px_width, name),

    print
    print "Anchor with Picture tag follows:\n\n"
    print '<a href="https://www.flickr.com/photos/edwin_steele/%s"' \
          ' title="%s">' % (photo_id, p.title)
    print '<picture>'
    # XXX - should be the same as my min media breakpoint
    print ' <source media="(max-width=30em)"\n' \
          '     srcset="%s/small_250.jpg 1x, %s/medium_500.jpg 2x">'
    print ' <source media="(min-width=30em)"\n' \
          '     srcset="%s/medium_500.jpg 1x, %s/large_1024.jpg 2x">'
    # If the browser can't understand source and picture tags, let's
    #  give a regularly sized image
    print ' <img srcset="%s/medium_500.jpg 1x,\n' \
          '         %s/large_1024.jpg 2x"\n' \
          '     src="%s/medium_500.jpg"\n' \
          '     alt="%s">' % (wpp, wpp, wpp, wpp, p.title,)
    print '</picture>'
    print '</a>'

    # Always make sure the directory exists
    # Don't use os.path.join, as it doesn't work with two absolute paths
    picture_output_dir = REPO_ASSETS_LOCATION + wpp
    if not os.path.exists(picture_output_dir):
        print "Making picture output directory: %s" % (picture_output_dir,)
        os.mkdir(picture_output_dir)

    for desired_size in desired_sizes:

        output_file = os.path.join(picture_output_dir,
                                   "%s_%s.jpg" %
                                   (desired_size.lower(), sizes[desired_size]["width"]))
        print "Saving %s version to %s" % (desired_size, output_file),
        p.save(output_file, size_label=desired_size)
        print " - Done. (%s bytes)" % os.stat(output_file).st_size


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process photos from flickr")
    parser.add_argument('photo_id', type=int,
                        help="Flickr photo ID (usually an 11 digit number")
    api_key = get_env_variable("FLICKR_API_KEY")
    api_secret = get_env_variable("FLICKR_API_SECRET")
    args = parser.parse_args()
    main(args.photo_id, PHOTO_SIZES, api_key, api_secret)
