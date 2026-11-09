//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/WeightedUnionFind.cpp
//// @name WeightedUnionFind
//// @check https://judge.yosupo.jp/problem/unionfind_with_potential include check
//// ! include
#include <bits/stdc++.h>
using namespace std;
#define int long long

#ifndef DEBUG_OUT
#define debug(...) ((void)0)
#endif
//// end
struct WeightedUnionFind {
    vector<int> p, d;
    WeightedUnionFind(int n) : p(n + 1, -1), d(n + 1) {}
    int root(int x) {
        if (p[x] < 0) return x;
        int y = root(p[x]);
        d[x] += d[p[x]];
        return p[x] = y;
    }
    int unite(int u, int v, int w) {
        int ru = root(u), rv = root(v);
        if (ru == rv) return d[v] - d[u] == w ? -1 : -2;
        w += d[u] - d[v];
        if (p[ru] > p[rv]) {
            swap(ru, rv);
            w = -w;
        }
        p[ru] += p[rv];
        p[rv] = ru;
        d[rv] = w;
        return ru;
    }
};
//// ! check
signed main() {
    int n, q;
    cin >> n >> q;
    WeightedUnionFind uf(n);
    constexpr int MOD = 998244353;
    auto norm = [&](int x) -> int {
        x %= MOD;
        if (x < 0) x += MOD;
        return x;
    };
    while (q--) {
        int t, u, v;
        cin >> t >> u >> v;
        if (t == 0) {
            int w;
            cin >> w;
            if (uf.root(u) == uf.root(v)) {
                int diff = uf.d[u] - uf.d[v];
                w = diff + norm(w - diff);
            }
            cout << (uf.unite(v, u, w) != -2) << '\n';
        } else {
            if (uf.root(u) != uf.root(v)) cout << -1 << '\n';
            else cout << norm(uf.d[u] - uf.d[v]) << '\n';
        }
    }
}
//// end
