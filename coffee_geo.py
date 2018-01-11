from geopy.geocoders import Nominatim

SINGLE_ORIGIN_DEF_FILE = "files/assets/single_origin_coffee_data.txt"


class SingleOriginCoffee:
    def __init__(self, country, title, region, varietal, lat, lon):
        self.country = country
        self.title = title
        self.region = region
        self.varietal = varietal
        self.lat = lat
        self.lon = lon

    def as_statement(self):
        return '  L.marker([%s, %s]).addTo(map).bindPopup("%s (%s, %s)");' % \
                (self.lat, self.lon, self.title, self.region, self.country)


def extract_coffee_definitions(filename):
    soc_list = []

    with open(filename) as fd:
        lines = fd.readlines()

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


soc_list = extract_coffee_definitions(SINGLE_ORIGIN_DEF_FILE)
geolocator = Nominatim(timeout=10)

unable_to_resolve = []

print("function addPoints() {")
for soc in soc_list:
    location_str = "%s, %s" % (soc.region, soc.country)
    loc = geolocator.geocode(location_str)
    if loc:
        soc.lat = loc.latitude
        soc.lon = loc.longitude
        print(soc.as_statement())
    else:
        unable_to_resolve.append("Unable to resolve %s" % (location_str,))

print("};")

print()
print("\n\/\/ ".join(unable_to_resolve))
