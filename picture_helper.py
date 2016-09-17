import argparse
import ast
import os

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


def extract_image_params(wordspeak_image_element):
    """Return dictionary of parameters that define a wordspeak image

    <!-- image: {"flickr_id":8412934156,"cloudinary_id":"IMG_1970_gykmv0",
                 "title":"Temple of Baal Cave: Another shawl feature"} -->
    """
    # Ignore enclosing whitespace
    wsie = wordspeak_image_element.strip()
    # Opening HTML comment
    if wsie[:4] != '<!--':
        return {}
    wsie = wsie[4:]
    # Closing HTML comment
    if wsie[-3:] != '-->':
        return {}
    wsie = wsie[:-3]
    # Ignore enclosing whitespace
    wsie = wsie.strip()
    # image: literal
    if wsie[:6] != 'image:':
        return {}
    wsie = wsie[6:]
    # Remove enclosing whitespace (required by ast.literal_eval)
    wsie = wsie.strip()
    try:
        d = ast.literal_eval(wsie)
        if isinstance(d, dict):
            return d
        return {}
    except ValueError:
        return {}


def main(element_string):
    image_params = extract_image_params(element_string)
    img_markup = generate_image_markup(image_params["title"],
                                       image_params["flickr_id"],
                                       image_params["cloudinary_id"])
    print img_markup


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate responsive image markup")
    parser.add_argument('img_element',
                        help="Image Element string")
    args = parser.parse_args()
    main(args.img_element)
