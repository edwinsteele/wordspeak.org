import flickr_api
from flickr_api.api import flickr
import os


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)


def main(photo_id):
    api_key = get_env_variable("FLICKR_API_KEY")
    api_secret = get_env_variable("FLICKR_API_SECRET")

    flickr_api.set_keys(api_key=api_key, api_secret=api_secret)
    user = flickr_api.Person.findByUserName("edwin steele")
    photos = user.getPublicPhotos()

    p = flickr_api.Photo(id=photo_id)

    sizes = p.getSizes()
    size_descs = sorted([(x, int(sizes[x]["width"])) for x in p.getSizes()], key=lambda x: int(x[1]))

    print "Widths available: ",
    for name, px_width in size_descs:
        print "%spx (%s)," % (px_width, name),

    # 250w, 500w, 1024w
    #print sizes["Small"]
    #print sizes["Medium"]
    #print sizes["Large"]


if __name__ == "__main__":
    PHOTO_ID = "16101389873"
    main(PHOTO_ID)
