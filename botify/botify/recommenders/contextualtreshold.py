from .toppop import TopPop
from .random import Random
from .indexed import Indexed
from .recommender import Recommender
import random


class ContextualTreshold(Recommender):
    """
    Recommend tracks closest to the previous one.
    Fall back to the random recommender if no
    recommendations found for the track.
    """

    def __init__(self, tracks_redis, for_indexed, catalog):
        self.tracks_redis = tracks_redis
        self.fallback = Indexed(tracks_redis, for_indexed, catalog)
        self.catalog = catalog
        self.was = set()

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        previous_track = self.tracks_redis.get(prev_track)

        if not(previous_track is None):
            self.was.add((user, prev_track))

        if prev_track_time < 0.8 :
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        for track in shuffled:
            if (user, track) in self.was:
                continue
            return track
        return self.fallback.recommend_next(user, prev_track, prev_track_time)  
        

