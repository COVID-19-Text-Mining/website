import copy

# this is only for searching, not displaying, and should be as high as possible
max_results = 30

# The mapping of entity type to shortcode
entity_shortcode_map = {
    "material": "MAT",
    "characterization": "CMT",
    "property": "PRO",
    "synthesis": "SMT",
    "application": "APL",
    "descriptor": "DSC",
    "phase": "SPL",
}

# The mapping of entity type to color
entity_color_map = {
    "material": "blue",
    "application": "green",
    "property": "orange",
    "phase": "red",
    "synthesis": "turq",
    "characterization": "purple",
    "descriptor": "pink",
}

# The mapping of all search filters
search_filter_color_map = copy.deepcopy(entity_color_map)
search_filter_color_map["text"] = "grey"

# The valid entity types
valid_entity_filters = list(entity_shortcode_map.keys())
