# -*- coding: utf-8 -*-

'''
build suffix tree with ukk algo in O(n) time
class: Suffix_tree
input A and B
output SP_score, align_A and align_B
author Juntao Chen
'''

from PSA_Kband import Compute_two, PSA_AGP_Kband
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

end = -1

class Node(object):
    def __init__(self, leaf):
        # the start & end
        self.start = None
        self.end = None
        self.leaf = leaf
        # self.length = 0
        self.children = {}
        self.suffix_link = None
    
    def __getattribute__(self, name: str):
        if name == 'end':
            if self.leaf:
                return end
        return super(Node, self).__getattribute__(name)

class PSA_Suffixtree(object):
    def __init__(self, strings):
        self.T = strings + '#'
        self.actNode = None
        self.actEdge = -1
        self.actLength = 0
        self.remainder = 0
        self.insideNode = None
        # the length of strings
        self.len = -1
        self.root = None

    def _edge_length(self, node):
        return node.end - node.start + 1

    def _walk_down(self, node):
        length = self._edge_length(node)
        if self.actLength >= length:
            self.actEdge += length
            self.actLength -= length
            self.actNode = node
            return True
        return False

    def _gen_node(self, start, end=None, leaf=False):
        node = Node(leaf)
        node.suffix_link = self.root
        node.start = start
        # end is None which means it is a leaf node.
        node.end = end
        return node
    
    def _gen_trie(self, pos):
        global end
        # init
        end = pos
        self.remainder += 1
        self.insideNode = None

        while self.remainder > 0:
            if self.actLength == 0:
                self.actEdge = pos
            
            if self.actNode.children.get(self.T[self.actEdge]) is None:
                # creat the leaf node
                self.actNode.children[self.T[self.actEdge]] = self._gen_node(pos, leaf=True)
                if self.insideNode:
                    self.insideNode.suffix_link = self.actNode
                    self.insideNode = None

            else:
                nextNode = self.actNode.children.get(self.T[self.actEdge])
                '''当前节点是否存在跨点'''
                if self._walk_down(nextNode):
                    continue
                '''当前字符在边上'''
                if self.T[nextNode.start + self.actLength] == self.T[pos]:
                    if self.insideNode and (self.actNode != self.root):
                        self.insideNode.suffix_link = self.actNode
                        self.insideNode = None

                    self.actLength += 1
                    break
                '''当前字符不在边上'''
                splitEnd = nextNode.start + self.actLength - 1
                # 新的内部节点
                split_node = self._gen_node(nextNode.start, splitEnd)
                # 活跃点的孩子重新设置
                self.actNode.children[self.T[self.actEdge]] = split_node
                # 将两个孩子节点添加至内部节点上
                split_node.children[self.T[pos]] = self._gen_node(pos, leaf=True)
                # 重新设置节点的范围
                nextNode.start += self.actLength
                split_node.children[self.T[nextNode.start]] = nextNode

                if self.insideNode:
                    self.insideNode.suffix_link = split_node
                self.insideNode = split_node

            self.remainder -= 1
            if (self.actNode == self.root) and (self.remainder > 0):
                self.actLength -= 1
                self.actEdge = pos - self.remainder + 1
            elif self.actNode != self.root:
                self.actNode = self.actNode.suffix_link
    
    def build_tree(self):
        self.len = len(self.T)
        rootEnd = -1
        self.root = self._gen_node(-1, rootEnd)
        self.actNode = self.root
        for i in range(self.len):
            self._gen_trie(i)
        
    def _creat_graph(self, node, deepth=1, edges=[]):
        if node.start != -1:
            strs = self.T[node.start:(node.end+1)]
        else:
            strs = 'Root'
        if node.children:
            sons = node.children.keys()
            for k, son in enumerate(sons):
                strs_son = self.T[node.children[son].start:(node.children[son].end+1)]
                edges.append([strs, strs_son, deepth, k])
                self._creat_graph(node.children[son], deepth+1, edges)
        return edges
    
    # draw the tree in a pic
    def draw(self):
        edges = self._creat_graph(self.root)
        G = nx.DiGraph()

        i, j = 0, 1
        pos = {}
        pos[i] = (0,0)
        record = {0:{}}
        for k in range(len(edges)):
            print(edges[k][0]+'-->'+edges[k][1])
            record[edges[k][2]] = {}
            if k >= 1 :
                if edges[k][0] == 'Root':
                    i = 0
                else:
                    i = record[edges[k][2]-1][edges[k][0]]
                j += 1
            record[edges[k][2]][edges[k][1]] = j
            pos[j] = (edges[k][3]+2*k, -edges[k][2])
            G.add_edge(i,j, name=edges[k][1])

        nx.draw(G, pos)
        edge_labels = nx.get_edge_attributes(G, 'name')
        nx.draw_networkx_edge_labels(G,pos, edge_labels=edge_labels)
        plt.show()
    
    def __walk_down_fcs(self, node, step):
        if self._edge_length(node) <= step:
            return True
        return False

    def _dfs_leaves(self, node, results, length):
        sons = node.children.values()
        for son in sons:
            if son.leaf:
                results.append(son.start-length)
            else:
                tmp = length + self._edge_length(son)
                self._dfs_leaves(son, results, tmp)
        return results

    def _select_prefix(self, s:str):
        node = self.root
        starts = []
        length, step, tag = 0, 0, 0
        while node.children.get(s[step+length]) is not None:
            node = node.children[s[step+length]]
            step += 1
            if len(s) >= step + length:
                if self.__walk_down_fcs(node, step):
                    length += step
                    step = 0
                    if len(s) == length:
                        break
                    else:
                        continue
                if len(s) == step + length:
                    break
            else:
                break
            while self.T[node.start + step] == s[step+length]:
                step += 1
                if len(s) >= step + length:
                    if self.__walk_down_fcs(node, step):
                        length += step
                        step = 0
                        if len(s) == length:
                            tag = 1
                        break
                    if len(s) == step + length:
                        tag = 1
                        break
                else:
                    tag = 1
                    break
            if tag:
                break
        if node.leaf:
            starts.append(node.start-length)
        else:
            starts = self._dfs_leaves(node, starts, length)
        return starts, length + step

    def _findCommonStrings(self, s2:str):
        index = 0
        results = []
        while index <= len(s2) - 1:
            starts, length = self._select_prefix(s2[index:])
            if starts and length > 1:
                results.append([index, length, starts])
                index += length
            else:
                index += 1
        return results
    
    def _MultiReg(self, results):
        start = float('Inf')
        end = -float('Inf')
        length = results[-1][0] + results[-1][1]
        for result in results:
            s = min(result[2])
            e = max(result[2]) + result[1]
            start = s if s < start else start
            end = e if e > end else end
        delete_k = []
        for k, result in enumerate(results):
            if len(result[2]) > 1:
                rate = result[0] / length
                temp = np.array(result[2])
                temp = (temp / (end - start)) - rate
                temp = list(abs(temp))
                index = temp.index(min(temp))
                result[2] = result[2][index]
            else:
                result[2] = result[2][0]
            if result[1] < length // 100:
                delete_k.append(k)
        de_results = []
        for i in range(len(results)):
            if i not in delete_k:
                de_results.append(results[i])
        return de_results

    def _trace_back(self, results, p, s):
        i = p.index(max(p))
        track = []
        while i > 0:
            if s[i-1] == None:
                if p[i] == results[i-1][1]:
                    track.append(i-1)
                    break
                i -= 1
            elif p[s[i-1]+1] + results[i-1][1] == p[i]:
                track.append(i-1)
                i = s[i-1] + 1
        return track

    def _select_CommonStrings(self, s2):
        results = self._findCommonStrings(s2)
        select_results = self._MultiReg(results)
        m = len(select_results)
        p = [0]*(m+1)
        s = [None]*(m)
        for i in range(m-1,-1,-1):
            j = i - 1
            while j >= 0:
                if select_results[i][2] >= (select_results[j][2]+select_results[j][1]):
                    s[i] = j
                    break
                j -= 1
        p[0] = 0
        for i in range(1, m+1):
            if s[i-1] == None:
                p[i] = select_results[i-1][1]
            else:    
                p[i] = p[s[i-1]+1] + select_results[i-1][1]
        track = self._trace_back(select_results, p, s)[::-1]
        selected_results = []
        for i in track:
            selected_results.append(select_results[i])
        return selected_results, p[-1]

    def align(self, s2):
        self.build_tree()
        results, _ = self._select_CommonStrings(s2)
        A, B = [], []
        align_A, align_B = [], []
        s_a, s_b = 0, 0
        for r in results:
            A.append(self.T[s_a:r[2]])
            B.append(s2[s_b:r[0]])
            s_a = r[1] + r[2]
            s_b = r[1] + r[0]
        A.append(self.T[s_a:-1])
        B.append(s2[s_b:])
        for i in range(len(A)):
            _, temp_A, temp_B = PSA_AGP_Kband(A[i], B[i])
            align_A.append(temp_A)
            align_B.append(temp_B)
        s_A, s_B = '', ''
        for j in range(len(results)):
            s_A += align_A[j]
            s_B += align_B[j]
            s_A += s2[results[j][0]:(results[j][0]+results[j][1])]
            s_B += s2[results[j][0]:(results[j][0]+results[j][1])]
        s_A += align_A[-1]
        s_B += align_B[-1]
        score = Compute_two(s_A, s_B)
        return score, s_A, s_B
        