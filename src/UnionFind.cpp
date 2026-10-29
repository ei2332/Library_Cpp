//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/UnionFind.cpp
//// @name UnionFind
//// @check https://onlinejudge.u-aizu.ac.jp/courses/library/3/DSL/all/DSL_1_A include check
//// ! include
#include <bits/stdc++.h>
using namespace std;
#define int long long

#ifndef DEBUG_OUT
#define debug(...) ((void)0)
#endif
//// end
struct UnionFind {
    vector<int> p;
    UnionFind(int n) : p(n + 1, -1) {}
    int root(int x) {
        if (p[x] < 0) return x;
        return p[x] = root(p[x]);
    }
    bool unite(int u, int v) {
        int ru = root(u), rv = root(v);
        if (ru == rv) return false;
        if (p[ru] > p[rv]) swap(ru, rv);
        p[ru] += p[rv];
        p[rv] = ru;
        return true;
    }
    bool same(int u, int v) { return root(u) == root(v); }
};
//// ! check
signed main() {
    int n, q;
    cin >> n >> q;
    UnionFind uf(n);
    while (q--) {
        int c, x, y;
        cin >> c >> x >> y;
        if (c == 0) uf.unite(x, y);
        else cout << uf.same(x, y) << "\n";
    }
}
//// end
