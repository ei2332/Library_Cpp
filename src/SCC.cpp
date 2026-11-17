//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/SCC.cpp
//// @name SCC
//// @expl 強連結成分分解（Kosaraju法）
//// @checked https://judge.yosupo.jp/problem/scc include check
//// ! include
#include <bits/stdc++.h>
using namespace std;
#define int long long
//// end

struct SCC {
    vector<vector<int>> g, rg;
    vector<int> id, order;

    SCC(int n) : g(n), rg(n), id(n) {}

    void add_edge(int u, int v) {
        g[u].push_back(v);
        rg[v].push_back(u);
    }

    void dfs1(int v) {
        id[v] = -1;
        for (int u : g[v]) if (id[u] == 0) dfs1(u);
        order.push_back(v);
    }

    void dfs2(int v, int k) {
        id[v] = k;
        for (int u : rg[v]) if (id[u] == -1) dfs2(u, k);
    }

    //// expl 成分数を返す。idはトポロジカル順に付与
    //// comp O(N+M)
    int build() {
        int n = g.size();
        id.assign(n, 0);
        order.clear();
        for (int v = 0; v < n; v++) if (id[v] == 0) dfs1(v);
        int k = 0;
        for (int i = n - 1; i >= 0; i--) {
            int v = order[i];
            if (id[v] == -1) dfs2(v, k++);
        }
        return k;
    }
};

//// ! check
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    SCC scc(n);
    while (m--) {
        int u, v;
        cin >> u >> v;
        scc.add_edge(u, v);
    }
    int k = scc.build();
    vector<vector<int>> groups(k);
    for (int v = 0; v < n; v++) groups[scc.id[v]].push_back(v);

    cout << k << '\n';
    for (auto& a : groups) {
        cout << a.size();
        for (int v : a) cout << ' ' << v;
        cout << '\n';
    }
}
//// end
