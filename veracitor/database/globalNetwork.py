from networkx import to_dict_of_dicts, DiGraph
from tag import *
from producer import *
from information import *
from group import *
from user import *
from mongoengine import *
import extractor
import math
from numpy import array
connect('mydb')

graph = None

def get_global_network():
    """Returns a graph containing all the producers currently in 
    the database with their ratings set on each other.
    Creates it if it is not already created.

    """
    global graph
    if graph is None:
        # Create a new graph.
        graph = build_network_from_db()
    return graph


def build_network_from_db():
    """Creates a new graph with data inserted from the database,
    overwrites the current graph. Only inserts producers into the 
    database as of now.

    """

    global graph
    # Users not included in graph.
    producers = producer.Producer.objects(type_of__ne="User")
    graph = DiGraph()
   
    # Add all producers in the database as nodes.
    for p1 in producers:
        graph.add_node(p1.name)
    
    # Add all producers' source ratings to the database as edges.
    for p2 in producers:
        for s in p2.source_ratings:
            graph.add_edge(p2.name, s.source.name, {s.tag.name: s.rating})
    
    return graph

def get_dictionary_graph():
    """Returns a python dictionary representation of the graph.

    """
    return to_dict_of_dicts(graph)

def notify_producer_was_added(producer):
    """Adds a new producer into the graph,
    connects it with existing producers.

    """
    graph.add_node(producer.name)
    for s in producer.source_ratings:
        graph.add_edge(producer.name, s.source.name, {s.tag.name: s.rating})

def notify_producer_was_removed(producer):
    """Deletes a producer from the graph,
    removes outgoing and incoming edges.
    """
    try:
        # edges are removed automatically :)
        graph.remove_node(producer.name)
    except Exception:
        # Removing nonexistant node is allowed.
        pass
    


def notify_producer_was_updated(producer):
    """Updates the graph with the given producer.
    
    """
    # Possibly cheap/slow implementation.
    notify_producer_was_removed(producer)
    notify_producer_was_added(producer)

def get_overall_difference(producer_name1, producer_name2, tag_names):
    """Returns the average difference in ratings made by producer_name1 and producer_name2
    on the same informations. Informations need to contain at least one tag in tag_names.
    If no common_info_ratings exists -1 will be returned.

    """
    common_info_ratings = get_common_info_ratings(producer_name1, producer_name2, tag_names)
    if len(common_info_ratings) == 0:
        return -1
    sum_diff_ratings = 0
    for info_rating_t in common_info_ratings:
        sum_diff_ratings += math.fabs(info_rating_t[0].rating - info_rating_t[1].rating)
    avg = sum_diff_ratings/len(common_info_ratings)
    return avg

def get_common_info_ratings(producer_name1, producer_name2, tag_names):
    """Returns a list of tuples on the form (info rating rating A,
    info rating rating B), where both A and B are ratings on the same
    information but A is made by producer1 and B by producer2. Re-
    turned ratings need to have been set under at least one of the
    specified tags. Returns an empty list if no common ratings are
    found.
    
    """    
    p1_info_ratings = extractor.get_producer(producer_name1).info_ratings
    p2_info_ratings = extractor.get_producer(producer_name2).info_ratings
    
    common_info_ratings = []
    # Candidate for later optimization.
    for info_1 in p1_info_ratings:
        for info_2 in p2_info_ratings:
            # Are these ratings set on the same information?
            if info_1.information.title == info_2.information.title:
                # Does the information have a tag matching requested tags?
                if __contains_common_tags(info_1.information.tags, tag_names):
                    # The ratings are set on the same information and conforms to tags.
                    # Therefore considered as a common info rating.
                    common_info_ratings.append((info_1, info_2,))
                    
   
    return common_info_ratings

    
def __contains_common_tags(tags_1, tag2_names):
    for tag in tags_1:
        if tag.name in tag2_names:
            return True

    return False


def get_extreme_info_ratings(producer_name, tag_names):
    """Returns a list of info ratings who differ from the mean by
    one standard deviation of the specified producer (I.E. ratings that
    are unusually extreme relative to specified producer's ratings).
    Returned ratings need to have been set under at least one of
    specified tags.

    """
    producer = extractor.get_producer(producer_name)
    
    # Will contain info ratings set on informations
    relevant_info_ratings = []
    relevant_info_ratings_ints = []
    total_sum = 0.0
    for info in producer.info_ratings:
        for tag in info.information.tags:
            if tag.name in tag_names:
                relevant_info_ratings.append(info)
                relevant_info_ratings_ints.append(info.rating)
                total_sum += info.rating
                break
    
    mean = (total_sum)/len(relevant_info_ratings)

    extremes = []
    np_array = array(relevant_info_ratings_ints)
    std = np_array.std()
    for info in relevant_info_ratings:
        diff = math.fabs(info.rating - mean)
        if diff > std:
            extremes.append(info)
    return extremes
    
    

def get_max_rating_difference(producer_name1, producer_name2, tag_names):
    """Returns an int equal to the difference between the two most differ-
    ing ratings between producer1 and producer2.
    If no common info_ratings were found -1 will be returned
    
    """
    producer1 = extractor.get_producer(producer_name1)
    producer2 = extractor.get_producer(producer_name2)

    common_info_ratings = get_common_info_ratings(producer_name1, producer_name2,tag_names)
    if len(common_info_ratings) == 0:
        return -1 

    max_diff = 0
    for common_tuple in common_info_ratings:
       diff = math.fabs(common_tuple[0].rating - common_tuple[1].rating)
       if diff > max_diff:
           max_diff = diff

    return max_diff

if __name__ == "__main__":
    build_network_from_db()

"""
def notify_information_was_removed(information):

def notify_information_was_updated(information):
    pass
    # add/remove edges corr. to trust-relations
    
def notify_information_was_removed(information):
    graph.remove_node(information.id)
    # edges are removed automatically :)


"""
