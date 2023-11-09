"""TrailRoute class for storing route info
    """

# TODO: Add a method to convert this object to a dict/json object


class TrailRoute:
    def __init__(self, trailId, trailTitle, trailArea, difficulty, avgRating, numRatings):
        self._id = trailId
        self.route_name = trailTitle
        self.trail_area = trailArea
        self.difficulty = difficulty
        self.average_rating = avgRating
        self.num_ratings = numRatings
