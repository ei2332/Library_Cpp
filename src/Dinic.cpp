//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/Dinic.cpp
//// @name Dinic
//// @expl Dinic法による最大流
//// ! include
#include <bits/stdc++.h>
using namespace std;
//// end

struct Dinic {
    struct E {
        int to, rev, cap;
    };
    vector<vector<E>> e;
    vector<int> l, it;
    Dinic(int n) : e(n), l(n), it(n) {}

    //// expl uからvへの容量capの有向辺を追加する。自己ループは追加せずfalseを返す
    //// comp O(1) 償却
    bool add_edge(int u, int v, int cap) {
        if (u == v) return 0;
        int a = e[u].size(), b = e[v].size();
        e[u].push_back({v, b, cap});
        e[v].push_back({u, a, 0});
        return 1;
    }
    bool bfs(int s, int t) {
        fill(l.begin(), l.end(), -1);
        queue<int> q;
        l[s] = 0;
        q.push(s);
        while (!q.empty()) {
            int v = q.front();
            q.pop();
            for (auto& i : e[v]) {
                if (i.cap > 0 && l[i.to] == -1) {
                    l[i.to] = l[v] + 1;
                    q.push(i.to);
                }
            }
        }
        return l[t] != -1;
    }
    int dfs(int v, int t, int f) {
        if (v == t) return f;
        for (int& i = it[v]; i < (int)e[v].size(); i++) {
            auto& x = e[v][i];
            if (x.cap == 0 || l[x.to] != l[v] + 1) continue;
            int d = dfs(x.to, t, min(f, x.cap));
            if (d) {
                x.cap -= d;
                e[x.to][x.rev].cap += d;
                return d;
            }
        }
        return 0;
    }
    //// expl sからtへの追加の最大流量を返す。sとtは異なる頂点とし、容量と流量はintの範囲内とする
    //// comp O(V^2 E)
    int max_flow(int s, int t) {
        int ans = 0;
        while (bfs(s, t)) {
            fill(it.begin(), it.end(), 0);
            while (int f = dfs(s, t, INT_MAX)) ans += f;
        }
        return ans;
    }
};
