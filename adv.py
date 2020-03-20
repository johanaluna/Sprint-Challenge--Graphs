from room import Room
from player import Player
from world import World
import pdb
import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []
class Queue():
    def __init__(self):
        self.queue = []
    def enqueue(self, value):
        self.queue.append(value)
    def dequeue(self):
        if self.size() > 0:
            #O(n) porque tengo que mover todo desde el beginning
            return self.queue.pop(0)
        else:
            return None
    def size(self):
        return len(self.queue)

def add_exist_to_map(mapa,current_room):
    for exits in current_room.get_exits():
        mapa[current_room.id][exits] = '?'
    return mapa

#pick_unexplored(mapa[id room)

def pick_direction(mapa, current_room=None, id_room=None):
    """
    Input : player.current_room
    Output : exists of that room
    """
    if id_room is None:
        exists = current_room.get_exits()
        random.shuffle(exists)
        for ex in exists:
            if mapa[current_room.id][ex]=='?':
                return ex

    if current_room is None:
        for ex in id_room.keys():
            # print("ID*****************",id_room, id_room.get(ex))
            visited = id_room.get(ex)
            if visited == '?':
                return ex
    
    return False

def path_to_unexplored(mapa, path):
    """
    CHECK go back 1 room an find a direction unexplored and
    return a new path to go to that direction
    """
    new_path = []
    # from 1 to all the 
    for i in range(1, len(path)):
        """
        I'm going to check each room in the path less the last room 
        because I come from there
        """
        for room_direction, room_id in mapa[path[i-1]].items():
            # print("AGAIN",room_direction, room_id)
            if room_id == path[i]:
                new_path.append(room_direction)
                break
    return new_path

def traverse_world(player, traversal_path):
    reverse = {'n': 's', 's': 'n', 'w': 'e', 'e': 'w'}
    # initialize the map
    mapa = {player.current_room.id: {}}
    # Populate the map with all the exist with a value '?
    mapa = add_exist_to_map(mapa, player.current_room)
    # Find all the exists unvisited
    move = pick_direction(mapa, player.current_room, None)
    if move is False:
        print("There are no more exits to visit")
    # Make a copy of the previous room
    previous_room = player.current_room
    #Go to the next room 
    player.travel(move)
    #Add this move to the path
    traversal_path.append(move)

    while True:
        # if the room is not in the map then add it
        if player.current_room.id not in mapa:
            mapa[player.current_room.id] = {}
            mapa = add_exist_to_map(mapa, player.current_room)

        # if in the current room there is not a value in the previous room
        # make a connection between them
        if mapa[player.current_room.id][reverse[move]] == '?':
            mapa[player.current_room.id][reverse[move]] = previous_room.id
            mapa[previous_room.id][move] = player.current_room.id

        # if there is an unexplored exit:
        move = pick_direction(mapa, player.current_room, None)
        # If there are no more exits unvisited....
        if move is False:
            # map a path to the closest unexplored exit
            return_path = bfs_unexplore_room( mapa,player.current_room.id)
            # if there are no unexplored exits, traversal is complete
            if return_path is None:
                """If None then I have visited all my rooms"""
                break
            # walk path while adding to traversal_path
            while return_path:
                move = return_path.pop(0)
                player.travel(move)
                traversal_path.append(move)
        else:
            # Make a copy of the previous room
            previous_room = player.current_room
            #Go to the next room 
            player.travel(move)
            #Add this move to the path
            traversal_path.append(move)
    return mapa


def bfs_unexplore_room(mapa,current_room):
    """
    Find an unexplored room that is close to my current room
    I'm using BFS becuase ..
    BFS goes Broad (to neighbors) before going deep
    """
    # Create an empty queue
    queue = Queue()
    # Add a path to the room_id to the queue
    queue.enqueue([current_room])
    # Create an empty set to store visited rooms
    visited = set()
    # While the queue is not empty...
    while queue.size() > 0:
        # Dequeue the first path
        path = queue.dequeue()
        # grab the last room from the path
        # make the current room the most recent added
        current_room = path[-1]
        # print('mapava values',mapa[current_room.id].values())
        if pick_direction(mapa,None,mapa[current_room]):
            # print('current_room.id',current_room.id,current_room_id)
            new_path= path_to_unexplored(mapa, path)
            return new_path
        # If the room has not been visited...
        if current_room not in visited:
            # print("Entre aca")
            # Mark it as visited
            visited.add(current_room)
            # Then add a path to all unvisited rooms to the back of the queue
            # print(mapa[current_room].values())
            # breakpoint()
            for next_room in mapa[current_room].values():
                if next_room not in visited:
                    # queue.append(path + [next_room])
                    new_path = path + [next_room]
                    queue.enqueue(new_path)

    return None

# TRAVERSAL TEST
traverse_world(player, traversal_path)
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")