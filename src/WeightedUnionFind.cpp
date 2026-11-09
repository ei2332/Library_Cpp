//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/WeightedUnionFind.cpp
//// @name WeightedUnionFind
//// @check https://onlinejudge.u-aizu.ac.jp/courses/library/3/DSL/all/DSL_1_B include check
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
    while (q--) {
        int c, x, y;
        cin >> c >> x >> y;
        if (c == 0) {
            int w;
            cin >> w;
            uf.unite(x, y, w);
        } else {
            if (uf.root(x) != uf.root(y)) cout << "?\n";
            else cout << uf.d[y] - uf.d[x] << "\n";
        }
    }
}
//// end
