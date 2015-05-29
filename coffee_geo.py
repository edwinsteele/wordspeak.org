from geopy.geocoders import Nominatim
import json

SINGLE_ORIGIN_DEF_FILE = "files/assets/single_origin_coffee_data.txt"


class SingleOriginCoffee:
    def __init__(self, country, title, region, varietal, lat, lon):
        self.country = country
        self.title = title
        self.region = region
        self.varietal = varietal
        self.lat = lat
        self.lon = lon


def get_location_from_str(location_str, locator):
    location = locator.geocode(location_str)
    return location


def extract_details_from_file(filename):
    soc_list = []

    with open(filename) as f:
        lines = f.readlines()

    for line in lines:
        # Country is always first
        country_str = line.partition(" ")[0].strip()
        title_str = line.partition(".")[0].strip()
        # Optional region after the first period
        dot_sep = line.split(".")
        if len(dot_sep) > 1:
            full_region_str = dot_sep[1].partition("(")[0].strip()
            end_of_region_data_idx = full_region_str.lower().find("region")
            if end_of_region_data_idx != -1:
                region_str = full_region_str[:end_of_region_data_idx-1]
            else:
                region_str = full_region_str
        else:
            region_str = ""

        soc = SingleOriginCoffee(country_str, title_str, region_str, "", 0, 0)
        soc_list.append(soc)

    return soc_list


def soc_as_statement(soc):
    return '  L.marker([%s, %s]).addTo(map).bindPopup("%s (%s, %s)");' % \
            (soc.lat, soc.lon, soc.title, soc.region, soc.country)


def soc_as_debug(soc):
    if l:
        return "%s, %s -> %s (%s, %s)" % (soc.region,
                                          soc.country,
                                          l.address,
                                          l.latitude,
                                          l.longitude)
    else:
        return "%s, %s -> FAILED LOOKUP" % (soc.region, soc.country)


soc_list = extract_details_from_file(SINGLE_ORIGIN_DEF_FILE)
geolocator = Nominatim(timeout=10)

unable_to_resolve = []

print "function addPoints() {"
for soc in soc_list:
    location_str = "%s, %s" % (soc.region, soc.country)
    l = get_location_from_str(location_str, geolocator)
    if l:
        soc.lat = l.latitude
        soc.lon = l.longitude
        #print soc_as_debug(l)
        print soc_as_statement(soc)
    else:
        unable_to_resolve.append("Unable to resolve %s" % (location_str,))

print "};"

print
print "\n\/\/ ".join(unable_to_resolve)
