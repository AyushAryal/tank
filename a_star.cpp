#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <unordered_map>
#include <vector>

#include "priority_queue.hpp"

struct Node {
    std::uint32_t node_id;
    std::uint32_t distance;
    std::uint32_t parent;

    bool operator<(const Node& other) const {
        return distance < other.distance;
    }

    bool operator>(const Node& other) const {
        return distance > other.distance;
    }

    bool operator==(const Node& other) const {
        return distance == other.distance && node_id == other.node_id &&
               parent == other.parent;
    }
};

class Graph {
    std::vector<std::vector<std::pair<std::uint32_t, std::uint32_t>>> graph;

   public:
    Graph(std::uint32_t num = 0) : graph(num) {}

    void add_vertex(
        std::vector<std::pair<std::uint32_t, std::uint32_t>> connections = {}) {
        for (auto [i, weight] : connections) {
            if (i > graph.size()) {
                throw std::runtime_error("Vertex index out of range.");
            }
        }
        graph.emplace_back(std::move(connections));
    }

    void add_uedge(std::uint32_t vertA, std::uint32_t vertB,
                   std::uint32_t weight = 1) {
        add_edge(vertA, vertB, weight);
        add_edge(vertB, vertA, weight);
    }

    void add_edge(std::uint32_t vertA, std::uint32_t vertB,
                  std::uint32_t weight = 1) {
        assert(vertA >= graph.size() ||
               vertB >= graph.size() && "Vertex index not in range.");
        auto& vertA_conn = graph[vertA];
        auto ret =
            std::find_if(vertA_conn.begin(), vertA_conn.end(),
                         [vertB](const auto& i) { return i.first == vertB; });
        assert(ret != vertA_conn.end() && "Edge already exists.");
        vertA_conn.push_back({vertB, weight});
    }

    friend std::ostream& operator<<(std::ostream& out, const Graph& graph) {
        out << "[\n";
        for (auto l : graph.graph) {
            out << "    [";
            for (auto [i, weight] : l) {
                out << "(" << i << ", " << weight << ")"
                    << ", ";
            }
            out << "],\n";
        }
        out << "]";
        return out;
    }

    std::vector<std::uint32_t> bfs(std::uint32_t startVert,
                                   std::uint32_t endVert) {
        std::vector<bool> visited(graph.size());
        std::queue<std::uint32_t> q;
        q.push(startVert);

        std::unordered_map<std::uint32_t, std::uint32_t> mapping = {
            {startVert, startVert}};
        bool found = false;
        while (!q.empty()) {
            auto item = q.front();
            q.pop();
            if (item == endVert) {
                found = true;
                break;
            }

            auto& adj = graph[item];
            for (auto [vert_num, weight] : adj) {
                if (!visited[vert_num]) {
                    mapping[vert_num] = item;
                    q.push(vert_num);
                }
                visited[vert_num] = true;
            }
        }
        if (found) {
            auto parent = endVert;
            std::vector<std::uint32_t> path;
            path.push_back(endVert);
            while (parent != startVert) {
                parent = mapping[parent];
                path.push_back(parent);
            }
            std::reverse(path.begin(), path.end());
            return path;
        }
        return {};
    }

    std::vector<std::uint32_t> dijkstra(std::uint32_t startVert,
                                        std::uint32_t endVert) {
        PriorityQueue<Node> q;
        std::unordered_map<std::uint32_t, Node> q_map;
        std::unordered_map<std::uint32_t, Node> finished_pile;
        std::vector<bool> visited(graph.size());

        q.push({startVert, 0, startVert});
        q_map[startVert] = {startVert, 0, startVert};

        while (!q.empty()) {
            auto parent = q.front();
            q.pop();
            finished_pile[parent.node_id] = parent;
            q_map.erase(parent.node_id);
            if (parent.node_id == endVert) {
                break;
            }
            visited[parent.node_id] = true;

            auto adj = graph[parent.node_id];
            for (auto [i, weight] : adj) {
                auto it = q_map.find(i);
                if (it == q_map.end() && !visited[i]) {
                    q.push({i, weight + parent.distance, parent.node_id});
                    q_map[i] = {i, weight + parent.distance, parent.node_id};
                } else {
                    auto child = q_map[i];
                    if (parent.distance + weight < child.distance) {
                        q.remove(child);
                        child.distance = parent.distance + weight;
                        child.parent = parent.node_id;
                        q.push(child);
                        q_map[i] = child;
                    }
                }
            }
        }

        if (finished_pile.find(endVert) == finished_pile.end()) {
            return {};
        }

        std::vector<uint32_t> path;
        auto vert = endVert;
        do {
            path.push_back(vert);
            vert = finished_pile[vert].parent;
        } while (vert != startVert);
        path.push_back(startVert);
        std::reverse(path.begin(), path.end());
        return path;
    }
};

int main() {
    Graph graph(14);
    graph.add_uedge(13, 0, 7);
    graph.add_uedge(13, 1, 2);
    graph.add_uedge(13, 2, 3);
    graph.add_uedge(0, 1, 3);
    graph.add_uedge(0, 4, 4);
    graph.add_uedge(4, 1, 4);
    graph.add_uedge(1, 8, 1);
    graph.add_uedge(4, 6, 5);
    graph.add_uedge(6, 8, 3);
    graph.add_uedge(8, 7, 2);
    graph.add_uedge(7, 5, 2);
    graph.add_uedge(5, 11, 5);
    graph.add_uedge(11, 10, 4);
    graph.add_uedge(11, 9, 4);
    graph.add_uedge(10, 9, 6);
    graph.add_uedge(10, 12, 4);
    graph.add_uedge(9, 12, 4);
    graph.add_uedge(12, 2, 2);

    auto path = graph.dijkstra(13, 5);
    for (auto i : path) {
        std::cout << i << ",";
    }
}