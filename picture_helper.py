import argparse
import os
import flickr_api

EXAMPLE_DEFINITION = \
    "<!-- image: flickr=8412934156,cloudinary=IMG_1970_gykmv0 -->"

PHOTO_SIZES_PX = (180, 375, 768, 1536)
DEFAULT_PHOTO_SIZE = 375
REPO_ASSETS_LOCATION = "/Users/esteele/Code/wordspeak.org/files"
FLICKR_URL_TEMPLATE = "https://www.flickr.com/photos/edwin_steele/%s"
CLOUDINARY_URL_TEMPLATE = \
    "https://res.cloudinary.com/wordspeak/image/upload/" \
    "f_auto%%2Cq_auto%%2Cw_%s/%s"


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)


def generate_image_markup(img_title, flickr_img_id, cloudinary_img_id):
    print "Anchor with reponsive img tag follows:\n"
    markup_lines = []
    markup_lines.append('<a href="' +
                        FLICKR_URL_TEMPLATE % (flickr_img_id,) +
                        '" title="%s">' % (img_title,))
    # If the browser can't understand source and picture tags, let's
    #  give a regularly sized image
    markup_lines.append(' <img class="ri"')
    markup_lines.append('   alt="%s"' % (img_title,))
    markup_lines.append(
        '   src="' +
        CLOUDINARY_URL_TEMPLATE % (DEFAULT_PHOTO_SIZE, cloudinary_img_id) +
        '"'
    )
    markup_lines.append('   sizes="(max-width: 50em) 100vw%2C')
    markup_lines.append('          (min-width: 50em) 66vw"')

    srcset_images = []
    for photo_size in PHOTO_SIZES_PX:
        srcset_images.append(
            CLOUDINARY_URL_TEMPLATE % (photo_size, cloudinary_img_id) +
            ' %sw' % (photo_size,)
        )
    markup_lines.append('   srcset="%s"' % ("%2C\n".join(srcset_images),))
    markup_lines.append('</a>')
    return "\n".join(markup_lines)


def main(flickr_img_id, cloudinary_img_id, api_key, api_secret):
    flickr_api.set_keys(api_key=api_key, api_secret=api_secret)
    p = flickr_api.Photo(id=flickr_img_id)

    img_markup = generate_image_markup(p.title,
                                       flickr_img_id,
                                       cloudinary_img_id)
    print img_markup


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate responsive image markup")
    parser.add_argument('flickr_img_id', type=int,
                        help="Flickr photo ID (usually an 11 digit number")
    parser.add_argument('cloudinary_img_id',
                        help="Cloudinary photo ID")
    flickr_api_key = get_env_variable("FLICKR_API_KEY")
    flickr_api_secret = get_env_variable("FLICKR_API_SECRET")
    args = parser.parse_args()
    main(args.flickr_img_id, args.cloudinary_img_id,
         flickr_api_key, flickr_api_secret)
