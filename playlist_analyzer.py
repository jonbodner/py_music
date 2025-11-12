from ScriptingBridge import SBApplication

music = SBApplication.applicationWithBundleIdentifier_("com.apple.music")
playlists = music.playlists()
favorite_playlist = None
for playlist in playlists:
    if playlist.name() == "Favorite Songs":
        favorite_playlist = playlist
        break


class TrackKey:
    def __init__(self, name: str, artist: str):
        self.name = name
        self.artist = artist

    def __str__(self):
        return f"{self.name} - {self.artist}"

    def __eq__(self, other):
        if not isinstance(other, TrackKey):
            return False
        return self.name == other.name and self.artist == other.artist

    def __hash__(self):
        return hash((self.name, self.artist))


class TrackData:
    def __init__(self, name: str, artist: str, album: str, duration: float):
        self.name = name
        self.artist = artist
        self.duration = duration
        self.album = album

    def __str__(self):
        return f"{self.name} - {self.artist} - {self.album} - {self.duration}"


#  The map key is song/artist.
#  The value is a list of lists of track data.
#  when a new track is found with the same song/artist, iterate through the list of lists of track data.
#  when you find a list where the first element in the list has a duration within 5 seconds of the new track,
#  then add the new track to that list of tracks.
#  if no entry in that map has a duration within 5 seconds of the new track, then create a new entry in the map.

all_tracks = dict()
sub_groups = 0
for favorite in favorite_playlist.tracks():
    tk = TrackKey(favorite.name(), favorite.artist())
    if tk not in all_tracks:
        print(f"adding {tk}")
        groups = list()
        same = list()
        same.append(TrackData(favorite.name(), favorite.artist(), favorite.album(), favorite.duration()))
        groups.append(same)
        all_tracks[tk] = groups
    else:
        groups = all_tracks[tk]
        found = False
        for group in groups:
            if abs(group[0].duration - favorite.duration()) < 5:
                group.append(TrackData(favorite.name(), favorite.artist(), favorite.album(), favorite.duration()))
                found = True
                print(f"duplicate {tk} - existing group")
            break
        if not found:
            same = list()
            same.append(TrackData(favorite.name(), favorite.artist(), favorite.album(), favorite.duration()))
            groups.append(same)
            print(f"duplicate {tk} - new group")
            sub_groups += 1

print(len(all_tracks))
print(sub_groups)

# print out the multi-group tracks
multi_groups = {k: v for (k, v) in all_tracks.items() if len(v) > 1}
print(len(multi_groups))
for k, v in multi_groups.items():
    print(f"{k} ({len(v)}):")
    for idx, group in enumerate(v):
        print(f"\t{idx}")
        for track in group:
            print(f"\t\t{track}")
