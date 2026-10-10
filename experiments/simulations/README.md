# Simulations

Controlled worlds where the true model is known, so a policy's regret can be compared with a lower bound and a certificate's coverage can be checked exactly.

| Folder | Question | Headline |
| --- | --- | --- |
| [spatiotemporal_benchmark/](spatiotemporal_benchmark/README.md) | Do policies that model persistence and spatial correlation beat iid, spatial-only and temporal-only bandits? (100 arms on a grid, AR(20)) | Joint predictive sampling closes 37% of the gap to the innovation lower bound without tuning; spatial correlation adds 15% on top of persistence |
| [certificates_under_persistence/](certificates_under_persistence/README.md) | Do certified-pooling certificates stay valid when rewards persist? (20 arms, AR(1), φ up to 0.97) | iid certificates are violated in 85–95% of bursty runs at φ ≥ 0.9; innovation-regression certificates (B1, B1′, B1″) never are |
| [theory/](theory/README.md) | Numerical checks for the theory notes in `research/` (graph alignment, predictive AR(1), AR allocation, spatiotemporal bandits) | Reported in each note |

Each experiment folder has a `README.md` (report), a `design.md`, `code/` and `results/`. The theory scripts are the exception: their design, report and outputs live with the notes in `research/` (see [theory/README.md](theory/README.md)).
