//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/ModInt.cpp
//// @name ModInt
//// @expl 固定法の剰余整数、CRT、組合せ計算
//// @check https://judge.yosupo.jp/problem/matrix_det include check_det
//// @check https://judge.yosupo.jp/problem/matrix_det no_macro check_det
//// @check https://judge.yosupo.jp/problem/number_of_subsequences include check_subseq
//// @check https://judge.yosupo.jp/problem/number_of_subsequences no_macro check_subseq
//// ! include
#include <bits/stdc++.h>
using namespace std;
#define int long long
//// end
//// ! no_macro
#include <bits/stdc++.h>
using namespace std;
//// end

using ll = long long;

template <int MOD>
struct mint {
    int v;
    mint(ll x = 0) {
        x %= MOD;
        if (x < 0) x += MOD;
        v = x;
    }
    mint& operator+=(const mint& o) {
        v += o.v;
        if (v >= MOD) v -= MOD;
        return *this;
    }
    mint& operator-=(const mint& o) {
        v -= o.v;
        if (v < 0) v += MOD;
        return *this;
    }
    mint& operator*=(const mint& o) {
        v = ll(v) * o.v % MOD;
        return *this;
    }
    mint& operator/=(const mint& o) {
        auto [g, x] = o.inv_gcd();
        assert(g == 1);
        return *this *= x;
    }
    friend mint operator+(mint a, const mint& b) { return a += b; }
    friend mint operator-(mint a, const mint& b) { return a -= b; }
    friend mint operator*(mint a, const mint& b) { return a *= b; }
    friend mint operator/(mint a, const mint& b) { return a /= b; }
    bool operator==(const mint&) const = default;

    //// expl n乗を返す
    //// comp O(log n)
    mint pow(ll n) const {
        mint x = *this, r = 1;
        while (n) {
            if (n & 1) r *= x;
            x *= x;
            n >>= 1;
        }
        return r;
    }

    //// expl (g,x)を返す。v*x ≡ g (mod MOD)、g = gcd(v,MOD)
    //// comp O(log MOD)
    pair<int, int> inv_gcd() const {
        ll a = MOD, b = v, x = 0, y = 1, q;
        while (b) {
            q = a / b;
            swap(a -= q * b, b);
            swap(x -= q * y, y);
        }
        if (x < 0) x += MOD / a;
        return {a, x};
    }
};

//// expl a ≡ x (mod P), a ≡ y (mod Q) を統合する
//// text 解なしなら-1。結果は[0,lcm(P,Q))に正規化
//// comp O(log min(P,Q))
template <int P, int Q>
ll crt(mint<P> x, mint<Q> y) {
    auto [g, inv] = mint<P>(Q).inv_gcd();
    int d = x.v - y.v, p = P / g;
    if (d % g) return -1;
    int t = d / g % p;
    if (t < 0) t += p;
    return y.v + ll(t) * inv % p * Q;
}

//// text 階乗が可逆である範囲を前計算する
//// text 素数MODの場合、前計算上限N < MOD
struct Comb {
    using T = mint<998244353>;
    vector<T> fact, ifact;

    //// comp O(N + log MOD)
    Comb(int n) : fact(n + 1), ifact(n + 1) {
        fact[0] = 1;
        for (int i = 1; i <= n; i++) fact[i] = fact[i - 1] * i;
        ifact[n] = fact[n].inv_gcd().second;
        for (int i = n; i > 0; i--) ifact[i - 1] = ifact[i] * i;
    }

    //// expl 組合せ nCr
    //// comp O(1)
    T C(int n, int r) const {
        if (n < 0 || r < 0 || r > n) return 0;
        return fact[n] * ifact[r] * ifact[n - r];
    }

    //// expl 順列 nPr
    //// comp O(1)
    T P(int n, int r) const {
        if (n < 0 || r < 0 || r > n) return 0;
        return fact[n] * ifact[n - r];
    }

    //// expl 重複組合せ nHr
    //// comp O(1)
    T H(int n, int r) const {
        if (n <= 0 || r < 0) return (n | r) == 0;
        return C(n + r - 1, r);
    }
};

//// ! check_det
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using T = mint<998244353>;
    int n;
    cin >> n;
    vector<vector<T>> a(n, vector<T>(n));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            int x;
            cin >> x;
            a[i][j] = x;
        }
    T det = 1;
    for (int i = 0; i < n; i++) {
        int p = i;
        while (p < n && a[p][i].v == 0) p++;
        if (p == n) { det = 0; break; }
        if (i != p) { swap(a[i], a[p]); det = T(0) - det; }
        T z = a[i][i];
        det *= z;
        for (int j = i + 1; j < n; j++) {
            T c = a[j][i] / z;
            for (int k = i + 1; k < n; k++) a[j][k] -= c * a[i][k];
            a[j][i] = 0;
        }
    }
    cout << det.v << '\n';
}
//// end
//// ! check_subseq
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using T = mint<998244353>;
    int n;
    cin >> n;
    unordered_map<int, T> last;
    last.reserve(n * 2);
    T dp = 1;
    for (int i = 0; i < n; i++) {
        int a;
        cin >> a;
        T prev = dp;
        dp += dp;
        auto it = last.find(a);
        if (it != last.end()) dp -= it->second;
        last[a] = prev;
    }
    cout << (dp - T(1)).v << '\n';
}
//// end
