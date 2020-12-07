""" This module provides class Ostov, which can generate minimal ostov from
weight graph matrix.
"""

class Ostov:

    def __init__(self, matrix, nX_count, is_or_graph):
        self.matrix = matrix
        self.nX_count = nX_count
        self.is_or_graph = is_or_graph
        self.ostov_ribs = []
        self.listing = []

    def generate_ribs(self):
        """ This method takes class variable adjacency matrix and generate
        ribs from it. After generating calls function delete_repeating_ribs.
        """

        self.ribs_with_weights = {}
        self.ribs = {}
        for i in range(self.nX_count):
            for j in range(self.nX_count):
                if self.matrix[i][j] != 0:
                    self.ribs[i, j] = self.matrix[i][j]
                    self.ribs_with_weights[i, j] = self.matrix[i][j]

        self.ribs = list(sorted(self.ribs.items(), key=lambda item: item[1]))
        self.ribs = [i[0] for i in self.ribs]
        if self.is_or_graph == False:
            self.delete_repeating_ribs(count=round(len(self.matrix)/2))

        self.listing.append("Отсортированный список ребер")
        for i in self.ribs:
            edge = str(i) + ' - ' + str(self.ribs_with_weights[i])
            self.listing.append(edge)

    def delete_repeating_ribs(self, count=2):
        """ This method deletes repeating ribs from general list of ribs, which
        have been taken from adjacency matrix given to __init__.

        count argument needs to prevent missed ribs, which can appear when we are
        deleting some rib and all ribs going to 1 postion back, but for statement
        continue watching ribs from last postion.
        """

        for k in range(count):
            slice_ = 1
            for i in self.ribs:
                for j in self.ribs[slice_::]:
                    if i[0]==j[1] and i[1]==j[0]:
                        self.ribs.remove(i)
                        break
                slice_ += 1

    def is_cyclic_util_or(self, v, visited, recStack):
        """ This method finds cycles for given node in or graph.

        If cycle appears return True, otherwise False.
        """

        visited[v]= True
        recStack[v] = True
        adj_list = []

        # Form adjacency list for current node, except prev edge.
        for i in self.ostov_ribs:
            if i[0] == v:
                adj_list.append(i[1])

        # Recursive call for every node in adj_list if it hadn't
        # been visited yet.
        for i in adj_list: 
            if visited[i] == False: 
                if self.is_cyclic_util_or(i, visited, recStack) == True: 
                    return True
            elif recStack[i] == True: 
                return True

        # The node needs to be poped from  
        # recursion stack before function ends 
        recStack[v] = False
        return False

    def is_cyclic_util_neor(self, v, visited, parent):
        """ This method finds cycles for given node in neor graph.

        If cycle appears return True, otherwise False.
        """

        visited[v]= True
        adj_list = []
        
        # Form adjacency list for current node, except prev edge.
        for i in self.ostov_ribs:
            if i[0] == v and i[1] != parent:
                adj_list.append(i[1])
            elif i[1] == v and i[0] != parent:
                adj_list.append(i[0])

        # Recursive call for every node in adj_list if it hadn't
        # been visited yet.
        for i in adj_list: 
            if visited[i] == False:  
                if self.is_cyclic_util_neor(i, visited, v): 
                    return True
            elif parent != i: 
                return True
        return False

    def is_cyclic(self):
        """ This method checks for cycle in formed minimal ostov, using is_cyclic_util()
        recursive call fo every node.

        If cycle is appear, returns True, otherwise False.
        """

        visited = [False]* self.nX_count
        recStack = [False] * self.nX_count

        for i in range(self.nX_count): 
            if visited[i] == False:
                if self.is_or_graph == False:
                    if self.is_cyclic_util_neor(i, visited, -1): 
                        return True
                else:
                    if self.is_cyclic_util_or(i, visited, recStack): 
                        return True
        return False

    def find_min_ostov(self):
        """ This method builds minimal ostov of graph, which is given as list of
        sorted ribs by their weights.

        At start, we add edge to ostov_ribs and call is_cyclic() function to
        find out if we have cycle with this edge. If there is no cycle, then
        we go to the next edge, otherwise we remove this edge from ostov_ribs.
        """
        
        for added_rib in self.ribs:
            self.listing.append("Текущий остовный список ребер")
            self.listing.append(', '.join(map(str, self.ostov_ribs)))
            if len(self.ostov_ribs) == self.nX_count-1:
                break
            self.ostov_ribs.append(added_rib)
            if self.is_cyclic() == False:
                self.listing.append("Добавим ребро - " + str(added_rib) + \
                                    " так как оно не создает цикл")
            else:
                self.listing.append("Ребро - " + str(added_rib) + " Добавить не можем "\
                                    "так как оно создает цикл")
                self.ostov_ribs.remove(added_rib)

        self.listing.append("Минимальный остов")
        self.listing.append(', '.join(map(str, self.ostov_ribs)))

        weight = 0
        weight_list = [self.ribs_with_weights[i] for i in self.ostov_ribs]
        for i in weight_list:
            weight += i
        self.listing.append("Вес - "+str(weight))

        return self.ostov_ribs