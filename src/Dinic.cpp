//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/Dinic.cpp
//// @name Dinic
//// @expl Dinic法による最大流
//// @check https://judge.yosupo.jp/problem/bipartitematching include check_matching
//// @checked https://atcoder.jp/contests/practice2/tasks/practice2_d include check_atcoder
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

//// ! check_matching
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int l, r, m;
    cin >> l >> r >> m;
    int s = l + r, t = s + 1;
    Dinic flow(t + 1);
    for (int i = 0; i < l; i++) flow.add_edge(s, i, 1);
    for (int i = 0; i < r; i++) flow.add_edge(l + i, t, 1);
    while (m--) {
        int a, b;
        cin >> a >> b;
        flow.add_edge(a, l + b, 1);
    }
    cout << flow.max_flow(s, t) << '\n';
}
//// end

//// ! check_atcoder
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<string> grid(n);
    for (auto& row : grid) cin >> row;

    int s = n * m, t = s + 1;
    Dinic dinic(t + 1);
    const int dr[] = {-1, 1, 0, 0};
    const int dc[] = {0, 0, -1, 1};

    for (int r = 0; r < n; ++r) {
        for (int c = 0; c < m; ++c) {
            if (grid[r][c] == '#') continue;
            int u = r * m + c;
            if ((r + c) % 2 == 1) {
                dinic.add_edge(u, t, 1);
                continue;
            }
            dinic.add_edge(s, u, 1);
            for (int k = 0; k < 4; ++k) {
                int nr = r + dr[k], nc = c + dc[k];
                if (nr < 0 || nr >= n || nc < 0 || nc >= m) continue;
                if (grid[nr][nc] == '.') dinic.add_edge(u, nr * m + nc, 1);
            }
        }
    }

    cout << dinic.max_flow(s, t) << '\n';
    for (int r = 0; r < n; ++r) {
        for (int c = 0; c < m; ++c) {
            if ((r + c) % 2 == 1) continue;
            for (const auto& edge : dinic.e[r * m + c]) {
                if (edge.to >= s || edge.cap != 0) continue;
                int nr = edge.to / m, nc = edge.to % m;
                if (r == nr) {
                    grid[r][min(c, nc)] = '>';
                    grid[r][max(c, nc)] = '<';
                } else {
                    grid[min(r, nr)][c] = 'v';
                    grid[max(r, nr)][c] = '^';
                }
            }
        }
    }
    for (const auto& row : grid) cout << row << '\n';
}
//// end
