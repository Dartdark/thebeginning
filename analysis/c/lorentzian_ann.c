/* Lorentzian ANN loop exactly as the user's AlphaFlow MultiCharts port (2026-10-24): persistent 9-slot buffer,
   lastDist reset each bar, neighbours = bars lp = 0 .. min(cb-1, maxbb-1) counted from the FIRST bar (or, with
   rolling = 1, from the bar maxbb before the current one), skipping lp % 4 == 0; prediction = sum of 8 labels.
   gcc -O2 -shared -fPIC -o lorentzian_ann.so lorentzian_ann.c -lm */
#include <math.h>
void ann(const double *F, const double *lab, int n, int nf, int maxbb, int nb, int rolling, double *pred) {
    double D[10], P[10]; int cnt = 0;
    int anchor = (int)(nb * 0.75 + 0.5) + 1;
    for (int i = 0; i < n; i++) {
        double last = -1.0; int lim = i; if (lim > maxbb - 1) lim = maxbb - 1;
        int base = rolling ? (i - lim) : 0;
        for (int lp = 0; lp <= lim; lp++) {
            if (lp % 4 == 0) continue;
            int j = base + lp; double d = 0;
            for (int k = 0; k < nf; k++) d += log(1 + fabs(F[i * nf + k] - F[j * nf + k]));
            if (d >= last) {
                last = d; cnt++; if (cnt > 9) cnt = 9;
                D[cnt] = d; P[cnt] = lab[j];
                if (cnt > nb) {
                    last = D[anchor];
                    for (int s = 1; s < 9; s++) { D[s] = D[s + 1]; P[s] = P[s + 1]; }
                    cnt--;
                }
            }
        }
        double p = 0; for (int s = 1; s <= cnt && s <= 8; s++) p += P[s];
        pred[i] = p;
    }
}
