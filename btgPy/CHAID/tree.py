import numpy as np
from treelib import Tree as TreeLibTree
from .node import Node
from .split import Split
from .column import NominalColumn, OrdinalColumn, ContinuousColumn
from .stats import Stats
from .invalid_split_reason import InvalidSplitReason
from .graph import Graph


class Tree(object):
    def __init__(self, independent_columns, dependent_column, config={}):
        """
        Init method to derive the tree from the columns constructing it

        Parameters
        ----------
        independent_columns : array<Column>
            an array of CHAID columns
        dependent_column : Column
            a single CHAID column to use as the dependent variable
        config: Dict
            {
                alpha_merge=0.05,
                max_depth=2,
                min_parent_node_size=30,
                min_child_node_size=30,
                split_threshold=0
            }
        """
        self.max_depth = config.get('max_depth', 2)
        self.min_parent_node_size = config.get('min_parent_node_size', 30)
        self.vectorised_array = independent_columns
        self.data_size = dependent_column.arr.shape[0]
        self.node_count = 0
        self._tree_store = None
        self.observed = dependent_column
        self._stats = Stats(
            config.get('alpha_merge', 0.05),
            config.get('min_child_node_size', 30),
            config.get('split_threshold', 0),
            dependent_column.arr
        )

    @staticmethod
    def from_numpy(ndarr, arr, alpha_merge=0.05, max_depth=2, min_parent_node_size=30,
                   min_child_node_size=30, split_titles=None, split_threshold=0, weights=None,
                   variable_types=None, dep_variable_type='categorical'):
        """
        Create a CHAID object from numpy

        Parameters
        ----------
        ndarr : numpy.ndarray
            non-aggregated 2-dimensional array containing
            independent variables on the veritcal axis and (usually)
            respondent level data on the horizontal axis
        arr : numpy.ndarray
            1-dimensional array of the dependent variable associated with
            ndarr
        alpha_merge : float
            the threshold value in which to create a split (default 0.05)
        max_depth : float
            the threshold value for the maximum number of levels after the root
            node in the tree (default 2)
        min_parent_node_size : float
            the threshold value of the number of respondents that the node must
            contain (default 30)
        split_titles : array-like
            array of names for the independent variables in the data
        variable_types : array-like or dict
            array of variable types, or dict of column names to variable types.
            Supported variable types are the strings 'nominal' or 'ordinal' in
            lower case
        """
        vectorised_array = []
        variable_types = variable_types or ['nominal'] * ndarr.shape[1]
        for ind, col_type in enumerate(variable_types):
            title = None
            if split_titles is not None:
                title = split_titles[ind]
            if col_type == 'ordinal':
                col = OrdinalColumn(ndarr[:, ind], name=title)
            elif col_type == 'nominal':
                col = NominalColumn(ndarr[:, ind], name=title)
            else:
                raise NotImplementedError(
                    'Unknown independent variable type ' + col_type)
            vectorised_array.append(col)

        if dep_variable_type == 'categorical':
            observed = NominalColumn(arr, weights=weights)
        elif dep_variable_type == 'continuous':
            observed = ContinuousColumn(arr, weights=weights)
        else:
            raise NotImplementedError(
                'Unknown dependent variable type ' + dep_variable_type)
        config = {'alpha_merge': alpha_merge, 'max_depth': max_depth, 'min_parent_node_size': min_parent_node_size,
                  'min_child_node_size': min_child_node_size, 'split_threshold': split_threshold}
        return Tree(vectorised_array, observed, config)

    def build_tree(self):
        """ Build chaid tree """
        self._tree_store = []
        self.node(np.arange(0, self.data_size, dtype=np.int),
                  self.vectorised_array, self.observed)

    @property
    def tree_store(self):
        if not self._tree_store:
            self.build_tree()
        return self._tree_store

    @staticmethod
    def from_pandas_df(df, i_variables, d_variable, alpha_merge=0.05, max_depth=2,
                       min_parent_node_size=30, min_child_node_size=30, split_threshold=0,
                       weight=None, dep_variable_type='categorical'):
        """
        Helper method to pre-process a pandas data frame in order to run CHAID
        analysis

        Parameters
        ----------
        df : pandas.DataFrame
            the dataframe with the dependent and independent variables in which
            to slice from
        i_variables : dict
            dict of instance variable names with their variable types. Supported
            variable types are the strings 'nominal' or 'ordinal' in lower case
        d_variable : string
            the name of the dependent variable in the dataframe
        alpha_merge : float
            the threshold value in which to create a split (default 0.05)
        max_depth : float
            the threshold value for the maximum number of levels after the root
            node in the tree (default 2)
        split_threshold : float
            the variation in chi-score such that surrogate splits are created
            (default 0)
        min_parent_node_size : float
            the threshold value of the number of respondents that the node must
            contain (default 30)
        min_child_node_size : float
            the threshold value of the number of respondents that each child node must
            contain (default 30)
        weight : array-like
            the respondent weights. If passed, weighted chi-square calculation is run
        dep_variable_type : str
            the type of dependent variable. Supported variable types are 'categorical' or
            'continuous'
        """
        ind_df = df[list(i_variables.keys())]
        ind_values = ind_df.values
        dep_values = df[d_variable].values
        weights = df[weight] if weight is not None else None
        return Tree.from_numpy(ind_values, dep_values, alpha_merge, max_depth, min_parent_node_size,
                               min_child_node_size, list(
                                   ind_df.columns.values), split_threshold, weights,
                               list(i_variables.values()), dep_variable_type)

    def node(self, rows, ind, dep, depth=0, parent=None, parent_decisions=None):
        """ internal method to create a node in the tree """
        depth += 1

        if self.max_depth < depth:
            terminal_node = Node(choices=parent_decisions, node_id=self.node_count,
                                 parent=parent, indices=rows, dep_v=dep)
            self._tree_store.append(terminal_node)
            if parent != None:
                self.get_node(parent).children.append(terminal_node.node_id)
                terminal_node.level = self.get_node(parent).level + 1
            self.node_count += 1
            terminal_node.split.invalid_reason = InvalidSplitReason.MAX_DEPTH
            return self._tree_store

        split = self._stats.best_split(ind, dep)

        node = Node(choices=parent_decisions, node_id=self.node_count, indices=rows, dep_v=dep,
                    parent=parent, split=split)

        self._tree_store.append(node)
        if parent != None:
            self.get_node(parent).children.append(node.node_id)
            node.level = self.get_node(parent).level + 1
        parent = self.node_count
        self.node_count += 1

        if not split.valid():
            return self._tree_store

        for index, choices in enumerate(split.splits):
            correct_rows = np.in1d(ind[split.column_id].arr, choices)
            dep_slice = dep[correct_rows]
            ind_slice = [vect[correct_rows] for vect in ind]
            row_slice = rows[correct_rows]
            if self.min_parent_node_size < len(dep_slice.arr):
                self.node(row_slice, ind_slice, dep_slice, depth=depth, parent=parent,
                          parent_decisions=split.split_map[index])
            else:
                terminal_node = Node(choices=split.split_map[index], node_id=self.node_count,
                                     parent=parent, indices=row_slice, dep_v=dep_slice)
                terminal_node.split.invalid_reason = InvalidSplitReason.MIN_PARENT_NODE_SIZE
                self._tree_store.append(terminal_node)
                if parent != None:
                    self.get_node(parent).children.append(
                        terminal_node.node_id)
                    terminal_node.level = self.get_node(parent).level + 1
                self.node_count += 1
        return self._tree_store

    def generate_best_split(self, ind, dep):
        """ internal method to generate the best split """
        return self._stats.best_split(ind, dep)

    def to_tree(self):
        """ returns a TreeLib tree """
        tree = TreeLibTree()
        for node in self:
            tree.create_node(node, node.node_id, parent=node.parent)
        return tree

    def __iter__(self):
        """ Function to allow nodes to be iterated over """
        return iter(self.tree_store)

    def __repr__(self):
        return str(self.tree_store)

    def get_node(self, node_id):
        """
        Returns the node with the given id
        Parameters
        ----------
        node_id : integer
            Find the node with this ID
        """
        return self.tree_store[node_id]

    def print_tree(self):
        """ prints the tree out """
        self.to_tree().show(line_type='ascii')

    def node_predictions(self):
        """ Determines which rows fall into which node """
        pred = np.zeros(self.data_size)
        for node in self:
            if node.is_terminal:
                pred[node.indices] = node.node_id
        return pred

    def classification_rules(self, node=None, stack=None):
        if node is None:
            return [
                rule for t_node in self for rule in self.classification_rules(t_node) if t_node.is_terminal
            ]

        stack = stack or []
        stack.append(node)

        if node.parent is None:
            return [
                {
                    'node': stack[0].node_id,
                    'rules': [
                        {
                            # 'type': self.vectorised_array[x.tag.split.column_id].type,
                            'variable': self.get_node(ancestor.parent).split_variable,
                            'data': ancestor.choices
                        } for ancestor in stack[:-1]
                    ]
                }
            ]
        else:
            return self.classification_rules(self.get_node(node.parent), stack)

    def model_predictions(self):
        """
        Determines the highest frequency of
        categorical dependent variable in the
        terminal node where that row fell
        """
        if isinstance(self.observed, ContinuousColumn):
            return ValueError("Cannot make model predictions on a continuous scale")
        pred = np.zeros(self.data_size).astype('object')
        for node in self:
            if node.is_terminal:
                pred[node.indices] = max(node.members, key=node.members.get)
        return pred

    def risk(self):
        """
        Calculates the fraction of risk associated
        with the model predictions
        """
        return 1 - self.accuracy()

    def accuracy(self):
        """
        Calculates the accuracy of the tree by comparing
        the model predictions to the dataset
        (TP + TN) / (TP + TN + FP + FN) == (T / (T + F))
        """
        sub_observed = np.array([self.observed.metadata[i]
                                 for i in self.observed.arr])
        return float((self.model_predictions() == sub_observed).sum()) / self.data_size

    def render(self, path=None, view=False):
        Graph(self).render(path, view)

    def predict(self, dataset, titulos):
        new_list = []
        for x in range(np.size(dataset, axis=0)):
            node_id = 0
            node = self.get_node(node_id)
            while len(node.children) != 0:
                var = node.split.split_name
                ind = titulos.index(var)
                val = dataset[x][ind]
                for i in node.children:
                    nde = self.get_node(i)
                    if val in nde.choices:
                        node_id = nde.node_id
                        node = nde
                        break
            new_list.append([node_id])
        return new_list

    def predict_separated(self, dataset, titulos, res):
        new_list = []
        hojas = []
        titles = []
        ti = "a_"+res
        for z in self.tree_store:
            if len(z.children) == 0:
                hojas.append(z.node_id)
                titles.append(ti+"_"+str(z.node_id))

        for x in range(np.size(dataset, axis=0)):

            node_id = 0
            node = self.get_node(node_id)
            while len(node.children) != 0:
                var = node.split.split_name
                ind = titulos.index(var)
                val = dataset[x][ind]
                if type(val) == str:
                    for i in node.children:
                        nde = self.get_node(i)
                        if val in nde.choices:
                            node_id = nde.node_id
                            node = nde
                            break
                else:
                    auxi = 0
                    for i in node.children:
                        nde = self.get_node(i)
                        if auxi == 0:
                            if val <= nde.choices[len(nde.choices)-1]:
                                node_id = nde.node_id
                                node = nde
                                break
                        elif auxi == len(node.children)-1:
                            prev_n = self.get_node(i-1)
                            if val > prev_n.choices[len(prev_n.choices)-1]:
                                node_id = nde.node_id
                                node = nde
                                break
                        else:
                            prev_n = self.get_node(i-1)
                            if val > prev_n.choices[len(prev_n.choices)-1] and val <= nde.choices[len(nde.choices)-1]:
                                node_id = nde.node_id
                                node = nde
                                break

                        auxi = auxi + 1
            aux = []
            for h in hojas:
                if h == node_id:
                    aux.append(1)
                else:
                    aux.append(0)
            new_list.append(aux)

        return [new_list, titles]
