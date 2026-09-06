"""Research-only phased autosomal genotype simulation; no clinical labels."""

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp


def calibrate_weights(donors, target, ridge=0.02):
    """Entropy-regularized moment matching of haplotype donor probabilities.

    Feature columns and targets must be selected using training data only.
    Ridge is fixed before evaluation, not selected on the held-out cohort.
    """
    x = np.asarray(donors, dtype=float)
    target = np.asarray(target, dtype=float)
    if x.ndim != 2 or target.shape != (x.shape[1],):
        raise ValueError("Incompatible donor/target dimensions")
    if np.any((target < 0) | (target > 1)) or ridge <= 0:
        raise ValueError("Invalid target or ridge")
    scale = np.sqrt(np.maximum(target * (1 - target), 0.01))
    x = x / scale
    t = target / scale

    def objective(beta):
        scores = x @ beta
        logz = logsumexp(scores)
        weights = np.exp(scores - logz)
        loss = logz - t @ beta + ridge * (beta @ beta) / 2
        gradient = x.T @ weights - t + ridge * beta
        return loss, gradient

    fitted = minimize(
        objective,
        np.zeros(x.shape[1]),
        jac=True,
        method="L-BFGS-B",
        options={"maxiter": 500, "ftol": 1e-12, "gtol": 1e-8},
    )
    if not fitted.success:
        raise RuntimeError(f"Calibration failed: {fitted.message}")
    scores = x @ fitted.x
    weights = np.exp(scores - logsumexp(scores))
    return weights


def sample_haplotypes(donors, count, rng, weights=None):
    return donors[rng.choice(len(donors), count, p=weights)].copy()


def mosaic_haplotypes(donors, positions, count, rng, weights, protected):
    """Copy donor blocks, keeping each protected interval on one donor.

    Fixed 50 kb boundaries are an experimental approximation, NOT a genetic
    recombination map or a one-generation meiosis model. Every block samples
    its donor independently. Long-range LD may consequently be reduced.
    """
    positions = np.asarray(positions)
    boundaries = list(range(int(positions[0]) + 50000, int(positions[-1]) + 1, 50000))
    boundaries = [
        b for b in boundaries if not any(lo <= b <= hi for lo, hi in protected)
    ]
    cuts = [0] + [int(np.searchsorted(positions, b)) for b in boundaries]
    cuts.append(len(positions))
    result = np.empty((count, len(positions)), dtype=np.uint8)
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        donor_ids = rng.choice(len(donors), count, p=weights)
        result[:, lo:hi] = donors[donor_ids, lo:hi]
    return result


def gamete(parent, map_morgans, rng):
    """Poisson-crossovers gamete from two phased parental homologues.

    Caller supplies a monotonic genetic map in Morgans. No interference or
    de novo mutations are modeled. Maternal and paternal maps may differ.
    """
    parent = np.asarray(parent)
    genetic_map = np.asarray(map_morgans, dtype=float)
    if parent.shape != (2, len(genetic_map)) or not len(genetic_map):
        raise ValueError("Expected two phased homologues and a genetic map")
    distances = np.diff(genetic_map)
    if not np.all(np.isfinite(genetic_map)) or np.any(distances < 0):
        raise ValueError("Genetic map must be finite and nondecreasing")
    switches = rng.poisson(distances) % 2
    homologues = np.concatenate([[rng.integers(2)], switches]).cumsum() % 2
    return parent[homologues, np.arange(parent.shape[1])]


def offspring(mother, father, maternal_map, paternal_map, rng):
    """One inherited maternal and one inherited paternal haplotype."""
    return np.stack(
        [gamete(mother, maternal_map, rng), gamete(father, paternal_map, rng)]
    )


def ld_r2(haplotypes):
    x = np.asarray(haplotypes, dtype=float)
    x -= x.mean(axis=0)
    covariance = x.T @ x / len(x)
    variance = np.diag(covariance)
    denominator = variance[:, None] * variance[None, :]
    return np.divide(
        covariance**2,
        denominator,
        out=np.zeros_like(covariance),
        where=denominator > 0,
    )


def row_set(array):
    return {row.tobytes() for row in np.packbits(array, axis=1)}


def new_haplotype_fraction(generated, founders):
    known = row_set(founders)
    return sum(
        row.tobytes() not in known for row in np.packbits(generated, axis=1)
    ) / len(generated)
