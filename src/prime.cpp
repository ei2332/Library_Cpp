//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/prime.cpp
//// @name Prime
//// @expl SPF、64bit素数判定（Miller-Rabin法）、素因数分解（Pollard Rho法）
//// @check https://judge.yosupo.jp/problem/primality_test include check_primality
//// @check https://judge.yosupo.jp/problem/primality_test no_macro check_primality
//// @check https://judge.yosupo.jp/problem/factorize no_macro check_factorize
//// @check https://judge.yosupo.jp/problem/factorize include_boost check_factorize
//// @check https://atcoder.jp/contests/abc084/tasks/abc084_d include check_spf
//// @check https://atcoder.jp/contests/abc084/tasks/abc084_d no_macro check_spf
//// ! include
#include <bits/stdc++.h>
using namespace std;
#define int long long
//// end
//// ! no_macro
#include <bits/stdc++.h>
using namespace std;
//// end
//// ! include_boost
#include <bits/stdc++.h>
using namespace std;
#define int long long
#define PRIME_SPF_BOOST
//// end

using ll = long long;

//// expl 符号付き64bit整数の素数判定
//// comp O(log n)
bool isprime(ll n) {
    if (n < 3) return n == 2;
    if (!(n & 1)) return false;

    ll d = n - 1;
    int s = 0;
    while (!(d & 1)) d >>= 1, s++;

    for (ll a : {2, 325, 9375, 28178, 450775, 9780504, 1795265022}) {
        a %= n;
        if (!a) continue;

        ll x = 1, v = a, e = d;
        while (e) {
            if (e & 1) x = (__int128)x * v % n;
            v = (__int128)v * v % n;
            e >>= 1;
        }

        if (x == 1) continue;
        for (int i = 0; i < s; i++) {
            if (x == n - 1) break;
            x = (__int128)x * x % n;
        }
        if (x != n - 1) return false;
    }
    return true;
}

//// expl 最小素因数表と素数列をO(N)で構築する
//// comp O(N)
struct SPF {
    vector<int> p, t;
    SPF(int n) : t(n + 1) {
        for (int i = 2; i <= n; i++) {
            if (!t[i]) {
                p.push_back(i);
                t[i] = i;
            }
            for (auto& j : p) {
                if (j > t[i] || i > n / j) break;
                t[i * j] = j;
            }
        }
    }
    //// expl 素因数を重複込みでrの末尾に追加する。1 <= n <= N
    //// comp O(log n)
    void fact(int n, vector<ll>& r) {
        while (n > 1) n /= r.emplace_back(t[n]);
    }
};

//// expl 合成数nの非自明な約数を1つ返す
ll rho(ll n) {
    if (1 - n % 2) return 2;
    for (ll c = 1;; c++) {
        auto f = [&](ll x) -> ll { return ((__int128)x * x + c) % n; };
        ll x = 2, y = 2;
        while (true) {
            x = f(x), y = f(f(y));
            ll d = gcd(abs(x - y), n);
            if (d == n) break;
            if (d - 1) return d;
        }
    }
}

#ifdef PRIME_SPF_BOOST
SPF _spf(1000000);
#endif

//// expl 素因数を重複込みでrの末尾に追加する。必要ならsort(r.begin(),r.end())
void fact(ll n, vector<ll>& r) {
    if (n < 2) return;
#ifdef PRIME_SPF_BOOST
    if (n <= 1000000) {
        _spf.fact(n, r);
        return;
    }
#endif
    if (isprime(n)) r.push_back(n);
    else {
        ll d = rho(n);
        fact(d, r);
        fact(n / d, r);
    }
}

//// ! check_primality
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    while (q--) {
        ll n;
        cin >> n;
        cout << (isprime(n) ? "Yes" : "No") << '\n';
    }
}
//// end

//// ! check_factorize
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    while (q--) {
        ll n;
        cin >> n;
        vector<ll> r;
        fact(n, r);
        sort(r.begin(), r.end());
        cout << r.size();
        for (ll x : r) cout << ' ' << x;
        cout << '\n';
    }
}
//// end

//// ! check_spf
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    SPF s(100000);
    vector<int> sum(100001);
    for (int i = 1; i <= 100000; i++) {
        sum[i] = sum[i - 1];
        if (s.t[i] == i && s.t[(i + 1) / 2] == (i + 1) / 2) sum[i]++;
    }
    int q;
    cin >> q;
    while (q--) {
        int l, r;
        cin >> l >> r;
        cout << sum[r] - sum[l - 1] << '\n';
    }
}
//// end
