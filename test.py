# %%

from igo import *

HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'
highways = download_highways(HIGHWAYS_URL)
congestions = download_congestions(CONGESTIONS_URL)


def find_corresponding_congestion_data(highway):
    corresponding_congestion_data = None
    for cong in congestions:
        if cong[0] == highway[0]:
            corresponding_congestion_data = cong
            break
    return corresponding_congestion_data


def repack(highway, congestion):
    id, name, orig_lat, orig_lng, dest_lat, dest_lng = highway
    _, datetime, current_state, _ = congestion
    return [id, name, orig_lat, orig_lng, dest_lat, dest_lng, datetime, current_state]


def build_complete_traffic_data(highways, congestions):
    complete_traffic_state_data = list()
    for highway in highways:
        congestion = find_corresponding_congestion_data(highway)
        repacked_data = repack(highway, congestion)
        complete_traffic_state_data.append(repacked_data)
    return complete_traffic_state_data


complete_data = build_complete_traffic_data(highways, congestions)

# %%
