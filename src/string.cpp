//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/string.cpp
//// @name String
//// @expl 文字列アルゴリズム（Manacher・Z Algorithm）
//// @check https://judge.yosupo.jp/problem/enumerate_palindromes include check_manacher
//// @check https://judge.yosupo.jp/problem/zalgorithm include check_z
//// ! include
#include <bits/stdc++.h>
using namespace std;
#define int long long

#ifndef DEBUG_OUT
#define debug(...) ((void)0)
#endif
//// end
//// expl 各位置を中心とする最長の奇数長回文の半径（中心を含む）
//// text s = "ababa" -> {1, 2, 3, 2, 1}
//// text 偶数長回文は文字間にダミー文字を挿入して求める
//// comp O(N)
vector<int> manacher(const string& s) {
    int n = s.size(), i = 0, j = 1, k;
    vector<int> res(n);
    while (i < n) {
        while (i >= j && i + j < n && s[i - j] == s[i + j]) j++;
        res[i] = j;
        k = 1;
        while (i - k >= 0 && i + k < n && k + res[i - k] < j) {
            res[i + k] = res[i - k];
            k++;
        }
        i += k;
        j -= k;
    }
    return res;
}

//// expl 各位置から始まる接尾辞と文字列全体の最長共通接頭辞長
//// text s = "ababa" -> {5, 0, 3, 0, 1}
//// text res[0] = N（空文字列なら空配列）
//// comp O(N)
vector<int> z_algorithm(const string& s) {
    int n = s.size(), i = 1, j = 0, k;
    vector<int> res(n);
    while (i < n) {
        while (i + j < n && s[i + j] == s[j]) j++;
        res[i] = j;
        for (k = 1; i + k < n && k + res[k] < j; k++) res[i + k] = res[k];
        i += k;
        j -= min(j, k);
    }
    if (n) res[0] = n;
    return res;
}
//// ! check_manacher
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    string t = "#";
    for (char c : s) {
        t += c;
        t += '#';
    }
    auto r = manacher(t);
    for (int i = 1; i + 1 < (int)t.size(); i++) {
        cout << r[i] - 1 << (i + 2 == (int)t.size() ? '\n' : ' ');
    }
}
//// end
//// ! check_z
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    auto z = z_algorithm(s);
    for (int i = 0; i < (int)z.size(); i++) {
        cout << z[i] << (i + 1 == (int)z.size() ? '\n' : ' ');
    }
}
//// end
