#pragma once
#include <algorithm>
#include <vector>

template <typename T, typename Container = std::vector<T>,
          typename Comp = std::greater<typename Container::value_type>>
class PriorityQueue {
    Container c;
    Comp comp;

   public:
    PriorityQueue() {}

    void remove(const T& item) {
        c.erase(std::find(c.begin(),c.end(),item));
        std::make_heap(c.begin(), c.end(), comp);
    }

    void push(const T& item) {
        c.push_back(item);
        std::push_heap(c.begin(), c.end(), comp);
    }

    void pop() {
        std::pop_heap(c.begin(), c.end(), comp);
        c.pop_back();
    }

    T& front() { return c.front(); }

    std::size_t size() const { return c.size(); }

    bool empty() const { return c.empty(); }
};