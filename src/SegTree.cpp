//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/SegTree.cpp
//// @name SegTree
//// @check https://judge.yosupo.jp/problem/point_add_range_sum include check_sum
//// @check https://atcoder.jp/contests/abc340/tasks/abc340_e include lazy check_mancala
//// @check https://judge.yosupo.jp/problem/range_affine_range_sum include lazy check_affine
//// ! include
#include <bits/stdc++.h>
using namespace std;
#define int long long

#ifndef DEBUG_OUT
#define debug(...) ((void)0)
#endif
//// end
//// ! check_affine
struct Mint {
    static constexpr int mod = 998244353;
    int v;
    Mint(int x = 0) : v((x % mod + mod) % mod) {}
    friend Mint operator+(Mint a, Mint b) { return a.v + b.v; }
    friend Mint operator*(Mint a, Mint b) { return a.v * b.v; }
    bool operator==(const Mint&) const = default;
    friend ostream& operator<<(ostream& os, Mint a) { return os << a.v; }
};
//// end
template <class T = int>
struct SegTree {
    T f1(T x, T y) { return x + y; }
    T e = 0;
    //// ! lazy
    using S = pair<T, T>;
    T f2(T x, S f, int len) { return f.first * x + f.second * len; }
    S f3(S o, S n) { return {o.first * n.first, n.first * o.second + n.second}; }
    S le = {1, 0};
    //// end

    vector<T> d;
    //// !! lazy
    vector<S> lz;
    int sz = 1, log = 0;

    SegTree(int n) {
        while (sz < n) sz *= 2, log++;
        d.assign(2 * sz, e);
        //// !! lazy
        lz.assign(sz, le);
    }
    //// ! lazy
    void push(int k, int len) {
        if (lz[k] == le) return;
        int l = k * 2, r = l + 1;
        d[l] = f2(d[l], lz[k], len / 2);
        d[r] = f2(d[r], lz[k], len / 2);
        if (l < sz) {
            lz[l] = f3(lz[l], lz[k]);
            lz[r] = f3(lz[r], lz[k]);
        }
        lz[k] = le;
    }
    //// end
    void set(int i, T x) {
        int k = i + sz;
        //// !! lazy
        for (int h = log; h > 0; h--) push(k >> h, 1LL << h);
        d[k] = x;
        while (k >>= 1) d[k] = f1(d[k * 2], d[k * 2 + 1]);
    }
    T query(int l, int r, int k = 1, int a = 0, int b = -1) {
        if (b < 0) b = sz;
        if (r <= a || b <= l) return e;
        if (l <= a && b <= r) return d[k];
        //// !! lazy
        push(k, b - a);
        int m = (a + b) / 2;
        return f1(query(l, r, k * 2, a, m), query(l, r, k * 2 + 1, m, b));
    }
    //// ! lazy
    void apply(int l, int r, S f, int k = 1, int a = 0, int b = -1) {
        if (b < 0) b = sz;
        if (r <= a || b <= l) return;
        if (l <= a && b <= r) {
            d[k] = f2(d[k], f, b - a);
            if (k < sz) lz[k] = f3(lz[k], f);
            return;
        }
        push(k, b - a);
        int m = (a + b) / 2;
        apply(l, r, f, k * 2, a, m);
        apply(l, r, f, k * 2 + 1, m, b);
        d[k] = f1(d[k * 2], d[k * 2 + 1]);
    }
    //// end
    T get(int i) { return query(i, i + 1); }
};
//// ! check_sum
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    SegTree st(n);
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        st.set(i, x);
    }
    while (q--) {
        int t, a, b;
        cin >> t >> a >> b;
        if (t == 0) st.set(a, st.get(a) + b);
        else cout << st.query(a, b) << '\n';
    }
}
//// end
//// ! check_mancala
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    SegTree st(n);
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        st.set(i, x);
    }
    while (m--) {
        int b;
        cin >> b;
        int x = st.get(b);
        st.set(b, 0);
        st.apply(0, n, {1, x / n});
        int r = x % n;
        int t = min(n - b - 1, r);
        st.apply(b + 1, b + 1 + t, {1, 1});
        r -= t;
        if (r) st.apply(0, r, {1, 1});
    }
    for (int i = 0; i < n; i++) cout << st.get(i) << (i + 1 == n ? '\n' : ' ');
}
//// end
//// ! check_affine
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    SegTree<Mint> st(n);
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        st.set(i, x);
    }
    while (q--) {
        int t, l, r;
        cin >> t >> l >> r;
        if (t == 0) {
            int b, c;
            cin >> b >> c;
            st.apply(l, r, {b, c});
        } else cout << st.query(l, r) << '\n';
    }
}
//// end
