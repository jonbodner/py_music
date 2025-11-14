from ScriptingBridge import SBApplication

music = SBApplication.applicationWithBundleIdentifier_("com.apple.music")
playlists = music.playlists()
favorite_playlist = None
for playlist in playlists:
    if playlist.name() == "Favorite Songs":
        favorite_playlist = playlist
        break


class TrackKey:
    def __init__(self, name: str, artist: str, group_id: int = -1):
        self.name = name
        self.artist = artist
        self.group_id = group_id

    def __str__(self):
        if self.group_id != -1:
            return f"{self.name} - {self.artist} (group {self.group_id})"
        return f"{self.name} - {self.artist}"

    def __eq__(self, other):
        if not isinstance(other, TrackKey):
            return False
        return self.name == other.name and self.artist == other.artist and self.group_id == other.group_id

    def __hash__(self):
        return hash((self.name, self.artist, self.group_id))

    def __lt__(self, other: TrackKey):
        return (self.artist, self.name, self.group_id) < (other.artist, other.name, other.group_id)


class TrackData:
    def __init__(self, name: str, artist: str, album: str, duration: float, id: int):
        self.name = name
        self.artist = artist
        self.duration = duration
        self.album = album
        self.id = id

    def __str__(self):
        return f"{self.name} - {self.artist} - {self.album} - {self.duration} ({self.id}"


#  The map key is song/artist.
#  The value is a list of lists of track data. each element is called a group.
#  when a new track is found with the same song/artist, iterate through the list of lists of track data.
#  when you find a list where the first element in the list has a duration within 5 seconds of the new track,
#  add the new track to that list of tracks.
#  if there's no matching existing group, then create a new group.

all_tracks = dict()
sub_groups = 0
for favorite in favorite_playlist.tracks():
    tk = TrackKey(favorite.name(), favorite.artist())
    if tk not in all_tracks:
        # print(f"adding {tk}")
        groups = list()
        group = list()
        group.append(TrackData(favorite.name(), favorite.artist(), favorite.album(), favorite.duration(), favorite.id()))
        groups.append(group)
        all_tracks[tk] = groups
    else:
        groups = all_tracks[tk]
        found = False
        for group in groups:
            if abs(group[0].duration - favorite.duration()) < 5:
                group.append(TrackData(favorite.name(), favorite.artist(), favorite.album(), favorite.duration(), favorite.id()))
                found = True
                print(f"duplicate {tk} - existing group")
            break
        if not found:
            group = list()
            group.append(TrackData(favorite.name(), favorite.artist(), favorite.album(), favorite.duration(), favorite.id()))
            groups.append(group)
            print(f"duplicate {tk} - new group")
            sub_groups += 1

print(len(all_tracks))
print(sub_groups)


# build a list of all duplicated favorite songs
# key is track key + group id
# value is a list of album and id

class AlbumInfo:
    def __init__(self, name: str, id: int):
        self.name = name
        self.id = id

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __lt__(self, other: AlbumInfo):
        return (self.name, self.id) < (other.name, other.id)


duplicate_favorite_songs = dict()
for key, groups in all_tracks.items():
    for idx, group in enumerate(groups):
        if len(group) > 1:
            if len(groups) > 1:
                tk = TrackKey(key.name, key.artist, idx)
            else:
                tk = TrackKey(key.name, key.artist)
            # all tracks in this group are duplicates of each other
            album_infos = []
            for track in group:
                album_infos.append(AlbumInfo(track.album, track.id))
            duplicate_favorite_songs[tk] = album_infos

# at this point, duplicate_favorite_songs contains all duplicated tracks
print(f"Total duplicated favorite songs: {len(duplicate_favorite_songs)}")
for track, album_infos in sorted(duplicate_favorite_songs.items()):
    print(track)
    for album_info in sorted(album_infos):
        print(f"\t{album_info}")

# print out the multi-group tracks
multi_groups = {k: v for (k, v) in all_tracks.items() if len(v) > 1}
print(len(multi_groups))
for k, v in sorted(multi_groups.items()):
    print(f"{k} ({len(v)}):")
    for idx, group in enumerate(v):
        print(f"\t{idx}")
        for track in group:
            print(f"\t\t{track}")
