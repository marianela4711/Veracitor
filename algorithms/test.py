import networkx as nx
import matplotlib.pyplot as plt
from tidaltrust import TidalTrust as tt

G = nx.DiGraph()

G.add_weighted_edges_from([(1,2,10),
                           (1,3,8),
                           (1,4,9),
                           (2,5,9),
                           (3,5,10),
                           (3,6,10),
                           (4,5,8),
                           (4,6,9),
                           (5,7,8),
                           (6,7,6),
                           ])

#nx.draw(G)
nx.draw_circular(G)
#nx.draw_spectral(G)

print tt.tidal_trust(graph=G, source=1, sink=7)

plt.show()