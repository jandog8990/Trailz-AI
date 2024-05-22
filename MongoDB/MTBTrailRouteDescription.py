"""TrailRouteDescription class for storing route description 
    """

# TODO: Add a method to convert this object to a dict/json object

class TrailRouteDescription:
    def __init__(self, primaryKey, trailKey, trailDescription, trailRouteId): 
        self._id = primaryKey 
        self.key = trailKey 
        self.text = trailDescription 
        self.mtb_trail_route_id = trailRouteId 
