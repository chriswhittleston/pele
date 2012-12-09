import networkx as nx

from pygmin.landscape import Graph

class _DistanceGraph(object):
    """
    This graph is used to guess a good method for connecting two minima
    
    Parameters
    ----------
    database : 
        the database in which to store newly found minima and transition states.
        If database contains contains previously found minima and transition states,
        those will be used to help with the connection.
    graph :
        the graph build from the database which contains the minima and transition states
    mindist : callable
        the routine which calculates the optimized distance between two structures
    verbosity :
        how much info to print (not very thoroughly implemented)
    defer_database_update : bool
        if true, save new distances and only update the database when enough new
        distances have been accumulated
    db_update_min : int
        only update the database when at least this many new distances have been found.
    
    This graph has a vertex for every minimum and an edge
    between (almost) every minima pairs. The edge weight between vertices u and v
    is
    
        if u and v are connected in "graph":
            weight(u,v) = 0.
        else:
            weight(u,v) = mindist(u,v)
            (or  = mindist(u,v)**2)
    
    Also, edges are removed from this graph when an NEB is done to try to
    connect them.  This is to ensure we don't repeat NEB runs over and over
    again.  The minimum weight path between min1 and min2 in this graph gives a
    good guess for the best way to try connect min1 and min2.  So the
    algorithm to find a pair of know minima (trial1, trial2) to try to
    connect is 

    path = Gdist.minimum_weight_path(min1, min2)
    trial1, trial2 = minima pair in path with lowest nonzero edge weight

    """
    def __init__(self, database, graph, mindist, verbosity=0,
                 defer_database_update=True, db_update_min=300):
        self.database = database
        self.graph = graph
        self.mindist = mindist
        self.verbosity = verbosity
        
        self.Gdist = nx.Graph()
        self.distance_map = dict() #place to store distances locally for faster lookup
        nx.set_edge_attributes(self.Gdist, "weight", dict())
        self.debug = True
        
        self.defer_database_update = defer_database_update
        
        self.new_distances = dict() #keep track of newly calculated distances
        self.db_update_min = db_update_min

    def distToWeight(self, dist):
        """
        this function defines how the edge weight is calculated.
        
        good options might be:
        
        weight = dist
        
        weight = dist**2
            this favors paths with many short edges over
            paths with fewer but longer edges.
        """
        return dist**2

    def updateDatabase(self, force=False):
        """update databases with new distances"""
        nnewdist = len(self.new_distances.items())
        if nnewdist == 0:
            return
        if not force:
            if nnewdist < self.db_update_min:
                return
        print "updating database with", nnewdist, "new distances"
        self.database.setDistanceBulk(self.new_distances.iteritems())
        self.new_distances = dict()

    def _setDist(self, min1, min2, dist):
        """
        this function saves newly calculated distances both to the local
        distance map and ultimately to the database
        """
        #add the distance to the database and the distance map
        if self.defer_database_update:
            self.new_distances[(min1, min2)] = dist
        else:
            self.database.setDistance(dist, min1, min2)
        self.distance_map[(min1, min2)] = dist
        
        #make sure a zeroed edge weight is not overwritten
        #if not self.edge_weight.has_key((min1, min2)):
        #    if not self.edge_weight.has_key((min2, min1)):
        #        self.edge_weight[(min1, min2)] = weight
    
    def _getDistNoCalc(self, min1, min2):
        """
        get distance from local memory.  don't calculate it.
        """
        #first try to get the distance from the dictionary 
        dist = self.distance_map.get((min1,min2))
        if dist is not None: return dist
        dist = self.distance_map.get((min2,min1))
        if dist is not None: return dist

        if False:
            #this is extremely slow for large databases (> 50% of time spent here)
            #also, it's not necessary if we load all the distances in initialize()
            #if that fails, try to get it from the database
            dist = self.database.getDistance(min1, min2)
            if dist is not None: 
                print "distance in database but not in distance_map"
                return dist
        return None

    def getDist(self, min1, min2):
        """
        return the distance between two minima.  Calculate it and store it if
        not already known
        """
        dist = self._getDistNoCalc(min1, min2)
        if dist is not None: return dist
        
        #if it's not already known we must calculate it
        dist, coords1, coords2 = self.mindist(min1.coords, min2.coords)
        if self.verbosity > 1:
            print "calculated distance between", min1._id, min2._id, dist
        self._setDist(min1, min2, dist)
        return dist
    
    def _addEdge(self, min1, min2):
        """
        add a new edge to the graph.  Calculate the distance
        between the minima and set the edge weight
        """
        if min1 == min2: return
        dist = self.getDist(min1, min2)
        weight = self.distToWeight(dist)
        self.Gdist.add_edge(min1, min2, {"weight":weight})
        if self.graph.areConnected(min1, min2):
            self.setTransitionStateConnection(min1, min2)
            #note: this is incomplete.  if a new edge between
            #min1 and min2 connects
            #two clusters that were previously unconnected
            #then the edge weight should be set to zero 
            #with self.setTransitionStateConnection() for all minima
            #in the two clusters.  Currently this is being fixed
            #by calling checkGraph() from time to time.  I'm not sure
            #which is better.
    
    def _addMinimum(self, m):
        self.Gdist.add_node(m)
        #for noded that are connected set the edge weight using setTransitionStateConnection
        cc = nx.node_connected_component(self.graph.graph, m)
        for m2 in cc:
            if m2 in self.Gdist:
                #self.Gdist.add_edge(m, m2, weight=0.)
                self.setTransitionStateConnection(m, m2)
        
        #for all other nodes set the weight to be the distance
        for m2 in self.Gdist.nodes():
            if not self.Gdist.has_edge(m, m2):
                dist = self.getDist(m, m2)
                weight = self.distToWeight(dist)
                self.Gdist.add_edge(m, m2, {"weight":weight})


        
        
    
    def addMinimum(self, m):
        """
        add a new minima to the graph and add an edge to all the other
        minima in the graph.  
        
        Note: this can take a very long time if there are lots of minima
        in the graph.  mindist need to be run many many times.
        """
        trans = self.database.connection.begin()
        try:
            if not m in self.Gdist:
                self._addMinimum(m)
#                self.Gdist.add_node(m)
#                #add an edge to all other minima
#                for m2 in self.Gdist.nodes():
#                    self._addEdge(m, m2)
        except:
            trans.rollback()
            raise
        trans.commit()
                               

    def removeEdge(self, min1, min2):
        """remove an edge from the graph
        
        used to indicate that the routine should not try to connect
        these minima again.
        """
        self.Gdist.add_edge(min1, min2, weight=10e10)
        try:
            self.Gdist.remove_edge(min1, min2)
        except nx.NetworkXError:
            pass
        return True

    def _initializeDistances(self):
        """put all distances in the database into distance_map for faster access"""
#        from pygmin.storage.database import Distance
#        from sqlalchemy.sql import select
#        conn = self.database.engine.connect()
#        sql = select([Distance.__table__])
#        for tmp, dist, id1, id2 in conn.execute(sql):
#            #m1 = self.database.getMinimum(id1)
#            #m2 = self.database.getMinimum(id2)
#            self.distance_map[id1, id2] = dist
        if False:
            for d in self.database.distances():
                self.distance_map[(d.minimum1, d.minimum2)] = d.dist
        else:
            for d in self.database.distances():
                self.distance_map[(d._minimum1_id, d._minimum2_id)] = d.dist

    def replaceTransitionStateGraph(self, graph):
        self.graph = graph

    def _addRelevantMinima(self, minstart, minend):
        """
        add all the relevant minima from the database to the distance graph
        
        a minima is considered relevant if distance(min1, minstart) and
        distance(min1, minend) are both less than distance(minstart, minend)
        
        also, don't calculate any new distances, only add a minima if all distances
        are already known. 
        """
        start_end_distance = self.getDist(minstart, minend)
        count = 0
        naccept = 0
        for m in self.graph.graph.nodes():
            count += 1
            d1 = self._getDistNoCalc(m, minstart)
            if d1 is None: continue
            if d1 > start_end_distance: continue
            
            d2 = self._getDistNoCalc(m, minend)
            if d2 is None: continue
            if d2 > start_end_distance: continue
            
            print "    accepting minimum", d1, d2, start_end_distance
            
            naccept += 1
            self.addMinimum(m)
        print "    found", naccept, "relevant minima out of", count


    def initialize(self, minstart, minend, use_all_min=False, use_limited_min=True):
        """
        set up the distance graph
        
        initialize distance_map, add the start and end minima and load any other
        minima that should be used in the connect routine.
        """
        #raw_input("Press Enter to continue:")
        print "loading distances from database"
        self._initializeDistances()
        #raw_input("Press Enter to continue:")
        dist = self.getDist(minstart, minend)
        self.addMinimum(minstart)
        self.addMinimum(minend)
        if use_all_min:
            """
            add all minima in self.graph to self.Gdist
            """
            print "adding all minima to distance graph (Gdist)."
            print "    This might take a while."
            for m in self.database.minima():
                self.addMinimum(m)
        elif use_limited_min:
            print "adding relevant minima to distance graph (Gdist)."
            print "    This might take a while."
            self._addRelevantMinima(minstart, minend)
        #raw_input("Press Enter to continue:")

    def setTransitionStateConnection(self, min1, min2):
        """use this function to tell _DistanceGraph that
        there exists a known transition state connection between min1 and min2
        
        The edge weight will be set to zero
        """
        weight = 0.
        self.Gdist.add_edge(min1, min2, {"weight":weight})

    def shortestPath(self, min1, min2):
        """return the minimum weight path path between min1 and min2""" 
        if True:
            print "Gdist has", self.Gdist.number_of_nodes(), "nodes and", self.Gdist.number_of_edges(), "edges"
        try:
            path = nx.shortest_path(
                    self.Gdist, min1, min2, weight="weight")
        except nx.NetworkXNoPath:
            return None, None
        
        #get_edge attributes is really slow:
        #weights = nx.get_edge_attributes(self.Gdist, "weight") #this takes order number_of_edges
        weights = [ self.Gdist[path[i]][path[i+1]]["weight"] for i in range(len(path)-1) ]
        
        return path, weights
        
    def mergeMinima(self, min1, min2):
        """
        rebuild the graph with min2 deleted and 
        everything pointing to min1 pointing to min2 instead
        """
        print "    rebuilding Gdist"
        weights = nx.get_edge_attributes(self.Gdist, "weight")
        newgraph = nx.Graph()
        nx.set_edge_attributes(newgraph, "weight", dict())
        for node in self.Gdist.nodes():
            if node != min2:
                newgraph.add_node(node)
        for e in self.Gdist.edges():
            if not min1 in e and not min2 in e:
                newgraph.add_edge(e[0], e[1], {"weight":weights[e]})
            if min1 in e and min2 in e:
                continue
            #if e already exists in newgraph, make sure we don't overwrite
            #a zeroed edge weight
            if min2 in e:
                if e[0] == min2:
                    enew = (min1, e[1])
                else:
                    enew = (e[0], min1)
            else:
                enew = e
            existing_weight = weights.get(enew)
            if existing_weight is not None:
                if existing_weight < 1e-10:
                    #existing weight is zero.  don't overwrite
                    continue
            newgraph.add_edge(enew[0], enew[1], {"weight":weights[e]})
        
        #done, replace Gdist with newgraph
        self.Gdist = newgraph
        if self.debug:
            self.checkGraph()

    def checkGraph(self):
        """
        make sure graph is up to date.
        and make any corrections
        """
        print "checking Gdist"
        #check that all edges that are connected in self.graph
        #have zero edge weight
        #note: this could be done a lot more efficiently
        weights = nx.get_edge_attributes(self.Gdist, "weight")
        count = 0
        for e in self.Gdist.edges():
            are_connected = self.graph.areConnected(e[0], e[1])
            zero_weight = weights[e] < 1e-10
            #if they are connected they should have zero_weight
            if are_connected and not zero_weight:
                #print "    problem: are_connected", are_connected, "but weight", weights[e], "dist", dist
                if True:
                    #note: this is an inconsistency, but it's only a problem if
                    #there is no zero weight path from e[0] to e[1]
                    path, path_weight = self.shortestPath(e[0], e[1])
                    weight_sum = sum(path_weight)
#                    for i in range(len(path)-1):
#                        m1, m2 = path[i], path[i+1]
#                        try:
#                            w = weights[(m1, m2)]
#                        except KeyError:
#                            w = weights[(m2, m1)]
#                        weight_sum += w
                    if weight_sum > 10e-6:
                        #now there is definitely a problem.
                        count += 1
                        dist = self.getDist(e[0], e[1])
                        print "    problem: are_connected", are_connected, "but weight", weights[e], "dist", dist, "path_weight", weight_sum
                self.setTransitionStateConnection(e[0], e[1])
                            
                     
            if not are_connected and zero_weight:
                dist = self.getDist(e[0], e[1])
                print "    problem: are_connected", are_connected, "but weight", weights[e], "dist", dist
                w = self.distToWeight(dist)
                self.Gdist.add_edge(e[0], e[1], {"weight":w})
        if count > 0:
            print "    found", count, "inconsistencies in Gdist"
                     
