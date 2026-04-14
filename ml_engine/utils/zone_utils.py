from config import ZONES


def assign_zone(bbox, fw, fh, distance=None) -> dict:
    if distance is not None:
        for zid, cfg in ZONES.items():
            if cfg.get("z_start", 0) <= distance < cfg.get("z_end", 100):
                return {"id": zid, **cfg}
    
    cx_norm = ((bbox[0] + bbox[2]) / 2) / fw
    cy_norm = ((bbox[1] + bbox[3]) / 2) / fh
    for zid, cfg in ZONES.items():
        if cfg["x_start"] <= cx_norm < cfg["x_end"] and cfg["y_start"] <= cy_norm < cfg["y_end"]:
            return {"id": zid, **cfg}
    return {"id": "ZONE_2", **ZONES["ZONE_2"]}


def get_zone_color(zid):
    return ZONES[zid]["color_bgr"]


def is_class_monitored(cls, zid):
    return cls in ZONES[zid]["monitored_classes"]


def get_all_zone_ids():
    return list(ZONES.keys())
