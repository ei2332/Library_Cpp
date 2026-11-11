//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/Iset.cpp
//// @name Iset
//// @expl PBDSによる順序統計付き集合。Imapは値を持つ順序統計付き連想配列。
//// @check https://judge.yosupo.jp/problem/ordered_set include check_set
//// @check https://judge.yosupo.jp/problem/associative_array include check_map
//// ! include
#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace std;
using namespace __gnu_pbds;
#define int long long

#ifndef DEBUG_OUT
#define debug(...) ((void)0)
#endif
//// end
template <typename T, typename S = null_type>
struct Iset : tree<T, S, less<T>, rb_tree_tag, tree_order_statistics_node_update> {
    using base = tree<T, S, less<T>, rb_tree_tag, tree_order_statistics_node_update>;
    using base::base;
    //// expl 小さい方からk番目（0-indexed）の要素のイテレータを返す。範囲外ではend()
    //// comp O(log N)
    auto kth(size_t k) { return this->find_by_order(k); }
    //// expl x未満のキーの個数を返す
    //// comp O(log N)
    size_t rank(const T& x) { return this->order_of_key(x); }
};
//// expl 値を持つ順序統計付き連想配列
template <typename T, typename S>
using Imap = Iset<T, S>;
//// ! check_set
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    Iset<int> s;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        s.insert(x);
    }
    while (q--) {
        int t, x;
        cin >> t >> x;
        if (t == 0) s.insert(x);
        else if (t == 1) s.erase(x);
        else if (t == 2) {
            auto it = s.kth(x - 1);
            cout << (it == s.end() ? -1 : *it) << '\n';
        } else if (t == 3) cout << s.rank(x + 1) << '\n';
        else if (t == 4) {
            auto it = s.upper_bound(x);
            cout << (it == s.begin() ? -1 : *prev(it)) << '\n';
        } else {
            auto it = s.lower_bound(x);
            cout << (it == s.end() ? -1 : *it) << '\n';
        }
    }
}
//// end
//// ! check_map
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    Imap<int, int> m;
    while (q--) {
        int t, k;
        cin >> t >> k;
        if (t == 0) {
            int v;
            cin >> v;
            m[k] = v;
        } else cout << m[k] << '\n';
    }
}
//// end
